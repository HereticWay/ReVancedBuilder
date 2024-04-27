#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Sayantan Santra <sayantan.santra689@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only

import os
import sys
import time

from ReVancedBuilder.Notifications import send_notif

# Move apps to proper location


def move_apps(appstate):
    build_config = appstate['build_config']
    log = appstate['logger']

    try:
        os.mkdir('archive')
    except FileExistsError:
        pass

    for app in build_config:
        if not build_config[app].getboolean('build'):
            continue
        name = build_config[app]['output_name']
        final_name = f"{name}_{appstate['timestamp']}.apk"
        build_config[app]['final_name'] = final_name
        
        final_apk_location = f'archive/{final_name}'
        appstate['final_built_apk_locations'][app] = final_apk_location

        try:
            os.rename(name+'.apk', final_apk_location)
        except FileNotFoundError:
            pass
            # sys.exit('There was an error moving the final apk files!')

        # Do some cleanup, keep only the last 3 build's worth of files and a week worth of logs
        with os.scandir('archive') as dir:
            files = []
            for f in dir:
                if name in f.name:
                    files.append(f)
            files.sort(key=lambda f: f.stat().st_ctime)
            files.reverse()
            for f in files[3:]:
                os.remove(f)
                log.info('Deleted old build '+f.name)

        # Delete logs older than 7 days
        with os.scandir('logs') as dir:
            now = time.time()
            for f in dir:
                if f.stat().st_ctime < now - 7 * 86400:
                    os.remove(f)
            # Do some cleanup, keep only the last 3 build's worth of files and a week worth of logs

    # Clean up GmsCore archive
    with os.scandir('archive') as dir:
        files = []
        for f in dir:
            if 'GmsCore' in f.name:
                files.append(f)
        files.sort(key=lambda f: f.stat().st_ctime)
        files.reverse()
        for f in files[3:]:
            os.remove(f)
            log.info('Deleted old build '+f.name)


def err_exit(msg, appstate, code=1):
    log.info = appstate['logger'].info

    try:
        appstate['notification_config']
        if appstate['flag'] != 'checkonly':
            send_notif(appstate, error=True)
    except:
        pass

    if msg:
        log.info(f"ERROR: {msg}")

    # Delete the lockfile
    os.remove('lockfile')
    sys.exit(code)
