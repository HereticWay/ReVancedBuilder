# Revanced Build
This repo template will allow one to build [ReVanced](https://github.com/revanced/) apps automatically. It uses [telegram.sh](https://github.com/fabianonline/telegram.sh) and [telegram-upload](https://github.com/Nekmo/telegram-upload) to messages. Make sure that `Java 17` is installed and selected as default.

## How to use
Just run `./build_revanced <working-directory> (force/clean/experimental)`. Might be a good idea to set it up to run periodically using cron. I currently use the following in a user crontab:
```
0 6 * * * <full-script-location> <full-working-directory-location>
```

## Notes
- The script will download the **automatically selected compatible version** (using compatibility of patches as listed [here](https://github.com/revanced/revanced-patches#list-of-available-patches)) of Youtube on APKMirror, **NOT** latest official version on Google Play.
- Under **NO CIRCUMSTANCES** any APKs will be uploaded to this repository to avoid DMCA.

## Customize your build
If you wish to continue with the default settings, you may skip this step.

By default this will build ReVanced with ALL available patches. Follow [this guide](PATCHES_GUIDE.md) to exclude/customizing patches for your build.
