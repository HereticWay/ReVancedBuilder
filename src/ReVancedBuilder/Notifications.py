#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Sayantan Santra <sayantan.santra689@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only

import os
import json
import re
import requests as req
import subprocess


def send_notif(appstate, error=False):
    log = appstate['logger']
    timestamp = appstate['timestamp']

    if error:
        msg = f"There was an error during build! Please check the logs.\nTimestamp: {timestamp}"
    else:
        notification_config = appstate['notification_config']
        build_config = appstate['build_config']
        present_vers = appstate['present_vers']
        flag = appstate['flag']

        msg = json.dumps(present_vers, indent=0)
        msg = re.sub('("|\{|\}|,)', '', msg).strip('\n')

        msg = msg.replace('revanced-', 'ReVanced ')
        msg = msg.replace('cli', 'CLI')
        msg = msg.replace('integrations', 'Integrations')
        msg = msg.replace('patches', 'Patches')

        for app in build_config:
            if not build_config[app].getboolean('build'):
                continue
            msg = msg.replace(
                build_config[app]['apk'], build_config[app]['pretty_name'])

        msg += '\nTimestamp: ' + timestamp
        if appstate['gmscore_updated']:
            msg += '\nGmsCore was updated.'

    config = appstate['notification_config']
    for entry in config:
        if not config[entry].getboolean('enabled'):
            continue
        encoded_title = '⚙⚙⚙ ReVanced Build ⚙⚙⚙'.encode('utf-8')

        if entry == 'ntfy':
            log.info('Sending notification through ntfy.sh...')
            try:
                url = config[entry]['url']
                topic = config[entry]['topic']
            except:
                log.info('URL or TOPIC not provided!')
                continue
            headers = {'Icon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Revanced-logo-round.svg/240px-Revanced-logo-round.svg.png',
                       'Title': encoded_title}
            try:
                req.post(f"{url}/{topic}", msg, headers=headers)
            except Exception as e:
                log.exception()

        elif entry == 'gotify':
            log.info('Sending notification through Gotify...')
            try:
                url = config[entry]['url']
                token = config[entry]['token']
            except:
                log.info('URL or TOKEN not provided!')
                continue
            data = {'Title': encoded_title, 'message': msg, 'priority': '5'}
            try:
                req.post(f"{url}/message?token={token}", data)
            except Exception as e:
                log.exception()

        elif entry == 'telegram':
            log.info('Sending notification through Telegram...')
            try:
                chat = config[entry]['chat']
                token = config[entry]['token']
            except:
                log.info('CHAT or TOKEN not provided!')
                continue
            cmd = f"./telegram.sh -t {token} -c {chat} -T \"{encoded_title.decode('utf-8')}\" -M \"{msg}\""
            try:
                log.info(cmd)
                with subprocess.Popen(cmd, shell=True, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout as output:
                    for line in output:
                        line_utf = line.decode('utf-8').strip('\n')
                        if line_utf:
                            log.info(line_utf)
            except Exception as e:
                log.exception()
            
            # Send apk links to Telegram channel
            for apk_location in appstate['final_built_apk_locations'].values():
                try:
                    file_name = os.path.basename(apk_location)
                    cmd = f'./telegram.sh -t {token} -c {chat} -D -H \'<a href="{config[entry]['file_server_url']}/{apk_location}">{file_name}</a>\''
                    with subprocess.Popen(cmd, shell=True, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout as output:
                        for line in output:
                            line_utf = line.decode('utf-8').strip('\n')
                            if line_utf:
                                log.info(line_utf)
                except Exception as e:
                    log.exception()
                    

        else:
            log.info('Don\'t know how to send notifications to ' + entry)

    # Telegram send emojis as "seperator"
    cmd = f'./telegram.sh -t {token} -c {chat} \'🚧🚦🚧\''
    with subprocess.Popen(cmd, shell=True, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout as output:
        for line in output:
            line_utf = line.decode('utf-8').strip('\n')
            if line_utf:
                log.info(line_utf)

