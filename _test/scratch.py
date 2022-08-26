
import os
import shlex
import subprocess

fake_exp = 'Lorem ipsum dolor sit amet, consectetur adipiscing '
fake_exp += 'elit, sed do eiusmod tempor incididunt ut labore '
fake_exp += 'et dolore magna aliqua. Ut enim ad minim veniam, '
fake_exp += 'quis nostrud exercitation ullamco laboris nisi ut '
fake_exp += 'aliquip ex ea commodo consequat. Duis aute irure '
fake_exp += 'dolor in reprehenderit in voluptate velit esse '
fake_exp += 'cillum dolore eu fugiat nulla pariatur. Excepteur '
fake_exp += 'sint occaecat cupidatat non proident, sunt in '
fake_exp += 'culpa qui officia deserunt mollit anim id est '
fake_exp += 'laborum.'
fake_exp += 'elit, sed do eiusmod tempor incididunt ut labore '
fake_exp += 'et dolore magna aliqua. Ut enim ad minim veniam, '
fake_exp += 'quis nostrud exercitation ullamco laboris nisi ut '
fake_exp += 'aliquip ex ea commodo consequat. Duis aute irure '
fake_exp += 'dolor in reprehenderit in voluptate velit esse '
fake_exp += 'cillum dolore eu fugiat nulla pariatur. Excepteur '
fake_exp += 'sint occaecat cupidatat non proident, sunt in '
fake_exp += 'culpa qui officia deserunt mollit anim id est '
fake_exp += 'laborum.'
fake_exp += 'elit, sed do eiusmod tempor incididunt ut labore '
fake_exp += 'et dolore magna aliqua. Ut enim ad minim veniam, '
fake_exp += 'quis nostrud exercitation ullamco laboris nisi ut '
fake_exp += 'aliquip ex ea commodo consequat. Duis aute irure '
fake_exp += 'dolor in reprehenderit in voluptate velit esse '
fake_exp += 'cillum dolore eu fugiat nulla pariatur. Excepteur '
fake_exp += 'sint occaecat cupidatat non proident, sunt in '
fake_exp += 'culpa qui officia deserunt mollit anim id est '
fake_exp += 'laborum.'
fake_exp += 'elit, sed do eiusmod tempor incididunt ut labore '
fake_exp += 'et dolore magna aliqua. Ut enim ad minim veniam, '
fake_exp += 'quis nostrud exercitation ullamco laboris nisi ut '
fake_exp += 'aliquip ex ea commodo consequat. Duis aute irure '
fake_exp += 'dolor in reprehenderit in voluptate velit esse '
fake_exp += 'cillum dolore eu fugiat nulla pariatur. Excepteur '
fake_exp += 'sint occaecat cupidatat non proident, sunt in '
fake_exp += 'culpa qui officia deserunt mollit anim id est '
fake_exp += 'laborum.'

fake_exp2 = 'Lorem ipsum dolor sit amet, consectetur adipiscing '
fake_exp2 += 'elit, sed do eiusmod tempor incididunt ut labore '
fake_exp2 += 'et dolore magna aliqua. Ut enim ad minim veniam, '
fake_exp2 += 'quis nostrud exercitation ullamco laboris nisi ut '
fake_exp2 += 'aliquip ex ea commodo consequat. Duis aute irure '
fake_exp2 += 'dolor in reprehenderit in voluptate velit esse '
fake_exp2 += 'cillum dolore eu fugiat nulla pariatur. Excepteur '
fake_exp2 += 'sint occaecat cupidatat non proident, sunt in '
fake_exp2 += 'culpa qui officia deserunt mollit anim id est '
fake_exp2 += 'laborum.'

old_path = '/home/dana/Documents/Projects/SpaceOddity/_test/test.png'
if os.path.exists(old_path):
    os.remove(old_path)
 
cmd = \
    f'convert \
    -size 100 \
    -pointsize 8 \
    -background none \
    -fill rgba(1.0,1.0,1.0,1.0) \
    caption:\"{fake_exp}\" \
    {old_path}'
cmd_array = shlex.split(cmd)

proc = subprocess.Popen(cmd_array, stderr=subprocess.PIPE)
str_out, str_err = proc.communicate()

# print('out:', str_out.decode())
print('err:', str_err.decode()[:80])
