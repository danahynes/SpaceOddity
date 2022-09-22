<!----------------------------------------------------------------------------->
<!-- Filename: README.md                                       /          \  -->
<!-- Project : SpaceOddity                                    |     ()     | -->
<!-- Date    : 09/13/2022                                     |            | -->
<!-- Author  : Dana Hynes                                     |   \____/   | -->
<!-- License : WTFPLv2                                         \          /  -->
<!----------------------------------------------------------------------------->

# SpaceOddity
## "It mostly works™"

A program that changes your wallpaper to NASA's Astronomy Picture of the 
Day

![](readme_screenshot.jpg)

# Installing

You should first run:

```bash
foo@bar:~$ sudo apt update && sudo apt upgrade
```

to make sure you have the lastest repos and software installed.

You can download the (hopefully stable)
[latest release](http://github.com/danahynes/SpaceOddity/releases/latest) from 
the main branch, unzip it, and run the *install.py* file from there:

```bash
foo@bar:~$ cd Downloads/SpaceOddity-X.X.X
foo@bar:~/Downloads/SpaceOddity-X.X.X$ ./install.py
```

Or you can clone the git repo to get the latest (and often broken) code
from the dev branch:

```bash
foo@bar:~$ cd Downloads
foo@bar:~/Downloads$ git clone https://github.com/danahynes/SpaceOddity
foo@bar:~/Downloads$ cd SpaceOddity
foo@bar:~/Downloads/SpaceOddity$ ./install.py
```

# Uninstalling

You can run the uninstaller locally:

```bash
foo@bar:~$ cd .spaceoddity
foo@bar:~/.spaeoddity$ ./uninstall.py
```

Or you can download the (hopefully stable)
[latest release](http://github.com/danahynes/SpaceOddity/releases/latest) from 
the main branch, unzip it, and run the *uninstall.py* file from there:

```bash
foo@bar:~$ cd Downloads/SpaceOddity-X.X.X
foo@bar:~/Downloads/SpaceOddity-X.X.X$ ./uninstall.py
```

Or you can clone the git repo to get the latest (and often broken) code
from the dev branch:

```bash
foo@bar:~$ cd Downloads
foo@bar:~/Downloads$ git clone https://github.com/danahynes/SpaceOddity
foo@bar:~/Downloads$ cd SpaceOddity
foo@bar:~/Downloads/SpaceOddity$ ./uninstall.py
```

Or you can remove the files manually (note that this won't remove entries 
from your crontab, but it shouldn't hurt your system):

``` bash
foo@bar:~$ rm -rf "~/.spacoddity"
foo@bar:~$ rm -rf "~/.config/spaceoddity"
```

# -)
