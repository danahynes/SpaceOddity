# ------------------------------------------------------------------------------
# Project : SpaceOddity                                            /          \
# Filename: install.py                                            |     ()     |
# Date    : 09/23/2022                                            |            |
# Author  : cyclopticnerve                                        |   \____/   |
# License : WTFPLv2                                                \          /
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

import installerator

# NB: requires:
# installerator

# the user dict
dict_user = {
    "general": {
        "name": "SpaceOddity"
    },
    "py_reqs": [
        "python-crontab"
    ],
    "dirs": [
        "${HOME}/.spaceoddity",
        "${HOME}/.config/spaceoddity"
    ],
    "files": {
        "${SRC}/spaceoddity.py": "${HOME}/.spaceoddity",
        "${SRC}/LICENSE": "${HOME}/.spaceoddity",
        "${SRC}/VERSION": "${HOME}/.spaceoddity",
        "${SRC}/uninstall.py": "${HOME}/.spaceoddity",
        "${SRC}/uninstall.json": "${HOME}/.spaceoddity",
        "${SRC}/cron_uninstall.py": "${HOME}/.spaceoddity"
    },
    "postflight": [
        "${SRC}/convert_json.py",
        "${SRC}/cron_install.py",
        "${HOME}/.spaceoddity/spaceoddity.py"
    ]
}

# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# This happens when we run script from install.py
# ------------------------------------------------------------------------------
if __name__ == '__main__':

    # instantiate installerator class
    # <package>.<module>.<class>()
    inst = installerator.installerator.Installerator()

    # # run the instance
    inst.run(dict_user)

# -)
