import sys
import json
from packaging.version import Version
import requests as req
from bs4 import BeautifulSoup as bs

# Determine the best version available to download
def apkpure_best_match(apk, appname, version, session):
    res = session.get(f"https://apkpure.com/{appname}/{apk}/versions")
    res.raise_for_status()
    data = bs(res.text, 'html.parser')
    try:
        vers_list = [Version(x['data-dt-version']) for x in data.css.select(f"a[data-dt-apkid^=\"b/APK/\"]")]
    except:
        sys.exit(f"    There was some error getting list of versions of {apk}...")
    
    if version != '0':
        vers_list = filter(lambda x: x <= Version(version), vers_list)
    
    return max(vers_list)

# Download an apk from APKPure.com
def apkpure_dl(apk, appname, version, hard_version, session, present_vers):
    if not hard_version:
        version = apkpure_best_match(apk, appname, version, session)

    try:
        if present_vers[apk] == version:
            print(f"Recommended version {version} of {apk} is already present.")
            return
    except KeyError:
        pass
    print(f"  Downloading {apk} version {version}...")

    # Get the version code
    res = session.get(f"https://apkpure.com/{appname}/{apk}/versions")
    res.raise_for_status()
    data = bs(res.text, 'html.parser')
    try:
        ver_code = data.css.select(f"a[data-dt-version=\"{version}\"][data-dt-apkid^=\"b/APK/\"]")[0]['data-dt-versioncode']
    except:
        sys.exit(f"    There was some error while downloading {apk}...")
    
    res = session.get(f"https://d.apkpure.com/b/APK/{apk}?versionCode={ver_code}", stream=True)
    res.raise_for_status()
    with open(apk, 'wb') as f:
        for chunk in res.iter_content(chunk_size=8192):
            f.write(chunk)
    print("    Done!")



# Download apk files, if needed
def get_apks(present_vers, build_config):
    print('Downloading required apk files from APKPure...')

    # Get latest patches using the ReVanced API
    try:
        patches = req.get('https://releases.revanced.app/patches').json()
    except req.exceptions.RequestException as e:
        sys.exit(e)
    
    session = req.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0'})

    for app in build_config:
        # Check if we need to build an app
        if not build_config[app].getboolean('build'):
            continue
        print(f"Checking {app}...")

        try:
            apk = build_config[app]['apk']
            apkpure_appname = build_config[app]['apkpure_appname']
        except:
            sys.exit(f"Invalid config for {app} in build_config.toml!")

        try:
            required_ver = build_config[app]['version']
            required_ver[0]
            hard_version = True
            print(f"Using version {required_ver} of {app} from ")
        except:
            hard_version = False
            compatible_vers = []
            for patch in patches:
                for pkg in patch['compatiblePackages']:
                    if pkg['name'] == apk:
                        try:
                            compatible_vers.append(pkg['versions'][-1])
                        except IndexError:
                            pass

            if not compatible_vers:
                required_ver = Version('0')
            else:
                required_ver = min(map(lambda x: Version(x), compatible_vers))

        apkpure_dl(apk, apkpure_appname, str(required_ver), hard_version, session, present_vers)

        present_vers.update({apk: str(required_ver)})
    return present_vers