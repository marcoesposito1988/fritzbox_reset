# FRITZ!Box reset script

This script allows to completely configure a brand new (or resetted) FRITZ!Box, setting the password and importing the settings from a backup file.

Said file needs to be compatible with the model and OS version!

This program was developed for a FRITZ!Box 3490 with FRITZ!OS 6. Other configurations are completely untested. 

## Usage
```
Usage:
    fritzbox_reset.py [--ip IP] NEW_PASSWORD SETTINGS_FILE_PATH
    fritzbox_reset.py (-h | --help)

Arguments:
    NEW_PASSWORD        New admin password to be set for the router
    SETTINGS_FILE_PATH  Path to the settings backup file to be restored

Options:
  -h --help     Show this screen.
  --ip IP         IP address that the FRITZ!Box assumes at first boot (default: 192.168.178.1)

```
