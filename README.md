<!----------------------------------------------------------------------------->
<!-- Project : SpaceOddity                                     /          \  -->
<!-- Filename: README.md                                      |     ()     | -->
<!-- Date    : 09/13/2022                                     |            | -->
<!-- Author  : cyclopticnerve                                 |   \____/   | -->
<!-- License : WTFPLv2                                         \          /  -->
<!----------------------------------------------------------------------------->

# SpaceOddity

## "It mostly works™"

[![License: WTFPL](https://img.shields.io/badge/License-WTFPL-brightgreen.svg)](http://www.wtfpl.net/about/)

A program that changes your wallpaper to NASA's Astronomy Picture of the 
Day

![](readme/readme_ss.jpg)

## Requirements

This app also requires two additional libraries:<br>
[Configurator](https://github.com/cyclopticnerve/Configurator/releases/latest)<br>
[Installerator](https://github.com/cyclopticnerve/Installerator/releases/latest)<br>
See their respective repos for installation instructions.

## Installing

You should first run:

```bash
foo@bar:~$ sudo apt update && sudo apt upgrade
```

to make sure you have the lastest software installed.

You can download the (hopefully stable)
[latest release](https://github.com/cyclopticnerve/SpaceOddity/releases/latest) 
from the main branch, unzip it, and run the *install.py* file from there:

```bash
foo@bar:~$ cd Downloads/SpaceOddity-X.X.X
foo@bar:~/Downloads/SpaceOddity-X.X.X$ ./install.py
```

Or you can clone the git repo to get the latest (and often broken) code 
from the dev branch:

```bash
foo@bar:~$ python -m pip install build
foo@bar:~$ cd Downloads
foo@bar:~/Downloads$ git clone https://github.com/cyclopticnerve/SpaceOddity
foo@bar:~/Downloads$ cd SpaceOddity
foo@bar:~/Downloads/SpaceOddity$ ./install.py
```

## Uninstalling

```bash
foo@bar:~$ cd .spaceoddity
foo@bar:~/.spaeoddity$ ./uninstall.py
```

## -)
