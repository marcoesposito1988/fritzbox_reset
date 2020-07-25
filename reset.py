#!/usr/bin/env python3
"""
Usage:
    fritzbox_reset.py [--ip IP] NEW_PASSWORD SETTINGS_FILE_PATH
    fritzbox_reset.py (-h | --help)

Arguments:
    NEW_PASSWORD        New admin password to be set for the router
    SETTINGS_FILE_PATH  Path to the settings backup file to be restored

Options:
  -h --help     Show this screen.
  --ip IP         IP address that the FRITZ!Box assumes at first boot (default: 192.168.178.1)

This script allows to completely configure a brand new FRITZ!Box, setting the password and importing the settings from a backup file.
Said file needs to be compatible with the model and OS version!
This program was developed for a FRITZ!Box 3490 with FRITZ!OS 6. Other configurations are completely untested.
"""
from docopt import docopt
import requests
import re
import os


def reset_fritzbox(new_password, settings_file_path, ip=None, check_address=None, update_status=print):
    if not os.path.exists(settings_file_path):
        raise ValueError(f"Can't find settings file at {settings_file_path}")

    if ip is None:
        ip = '192.168.178.1'
        print(f'Using default IP address for FRITZ!Box 3490, FRITZ!OS 6: {ip}')

    if check_address:
        import socket
        print((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
                 if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close())
                                                    for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]])
               + ["no IP found"])[0])

    # get page and find SID

    update_status('fetching welcome page')

    try:
        welcome_page_get = requests.get(f'http://{ip}', timeout=5)
    except requests.exceptions.Timeout:
        raise RuntimeError(f'ERROR: could not reach the FritzBox at the address {ip}'
                           'you must be connected to a FRITZ!Box with FRITZ!OS version 6, via ethernet or WiFi')

    sid = re.search('secure_link\.lua\?sid=([0-9a-f]{16})', welcome_page_get.text, re.IGNORECASE).group(0)[-16:]

    update_status('fetched welcome page, SID: {}'.format(sid))

    # set password

    update_status('setting password')

    set_password_post = requests.post(f'http://{ip}/no_password.lua',
                                      data={
                                          'sid': sid,
                                          'validate': 'apply',
                                          'xhr': 1,
                                          'pass': new_password
                                      })
    set_password_confirm_post = requests.post(f'http://{ip}/data.lua',
                                              data={
                                                  'sid': sid,
                                                  'apply': '',
                                                  'no_sidrenew': '',
                                                  'xhr': 1,
                                                  'pass': new_password,
                                                  'oldpage': '/no_password.lua',
                                              })

    update_status('set password')

    # tell that we will restore settings

    update_status('asking reset')

    after_setting_password_get = requests.get(f'http://{ip}/system/import.lua?sid={sid}')
    after_setting_password_confirm_post = requests.post(f'http://{ip}/data.lua',
                                                        data={
                                                            'sid': sid,
                                                            'no_sidrenew': '',
                                                            'xhr': 1,
                                                            'oldpage': '/system/import.lua',
                                                        })

    update_status('asked reset')

    # provide settings file with password

    update_status('resetting...')

    reset_settings_post = requests.post(f'http://{ip}/cgi-bin/firmwarecfg',
                                        files={'ConfigImportFile': open(settings_file_path, 'rb')},
                                        data={
                                            'sid': sid,
                                            'ImportExportPassword': new_password,
                                        })

    update_status('reset! the FritzBox should be restarting now')


if __name__ == '__main__':
    arguments = docopt(__doc__)
    password = arguments['NEW_PASSWORD']
    settings_path = arguments['SETTINGS_FILE_PATH']
    reset_fritzbox(new_password=password, settings_file_path=settings_path)
