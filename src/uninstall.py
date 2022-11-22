# ------------------------------------------------------------------------------
# Project : SpaceOddity                                            /          \
# Filename: uninstall.py                                          |     ()     |
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
    "preflight": {
        "${SRC}/cron_uninstall.py"
    },
    "dirs": [
        "${HOME}/.spaceoddity",
        "${HOME}/.config/spaceoddity"
    ]
}

# ------------------------------------------------------------------------------
# Run the main class if we are not an import
# This happens when we run script from install.py
# ------------------------------------------------------------------------------
if __name__ == '__main__':

    # instantiate installerator class
    uninst = installerator.installerator.Uninstallerator()

    # # run the instance
    uninst.run(dict_user)

# -)
