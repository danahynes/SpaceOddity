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
fake_exp += '\n'
fake_exp += 'Lorem ipsum dolor sit amet, consectetur adipiscing '
fake_exp += 'elit, sed do eiusmod tempor incididunt ut labore '
fake_exp += 'et dolore magna aliqua. Ut enim ad minim veniam, '
fake_exp += 'quis nostrud exercitation ullamco laboris nisi ut '
fake_exp += 'aliquip ex ea commodo consequat. Duis aute irure '
fake_exp += 'dolor in reprehenderit in voluptate velit esse '
fake_exp += 'cillum dolore eu fugiat nulla pariatur. Excepteur '
fake_exp += 'sint occaecat cupidatat non proident, sunt in '
fake_exp += 'culpa qui officia deserunt mollit anim id est '
fake_exp += 'laborum.'
fake_exp += '\n'
fake_exp += 'Lorem ipsum dolor sit amet, consectetur adipiscing '
fake_exp += 'elit, sed do eiusmod tempor incididunt ut labore '
fake_exp += 'et dolore magna aliqua. Ut enim ad minim veniam, '
fake_exp += 'quis nostrud exercitation ullamco laboris nisi ut '
fake_exp += 'aliquip ex ea commodo consequat. Duis aute irure '
fake_exp += 'dolor in reprehenderit in voluptate velit esse '
fake_exp += 'cillum dolore eu fugiat nulla pariatur. Excepteur '
fake_exp += 'sint occaecat cupidatat non proident, sunt in '
fake_exp += 'culpa qui officia deserunt mollit anim id est '
fake_exp += 'laborum.'
fake_exp += '\n'
fake_exp += 'Lorem ipsum dolor sit amet, consectetur adipiscing '
fake_exp += 'elit, sed do eiusmod tempor incididunt ut labore '
fake_exp += 'et dolore magna aliqua. Ut enim ad minim veniam, '
fake_exp += 'quis nostrud exercitation ullamco laboris nisi ut '
fake_exp += 'aliquip ex ea commodo consequat. Duis aute irure '
fake_exp += 'dolor in reprehenderit in voluptate velit esse '
fake_exp += 'cillum dolore eu fugiat nulla pariatur. Excepteur '
fake_exp += 'sint occaecat cupidatat non proident, sunt in '
fake_exp += 'culpa qui officia deserunt mollit anim id est '
fake_exp += 'laborum.'

# ----------------
width = 100
font_size = 40
limit = 1000
# ----------------

if limit == 0:
    new_text = fake_exp
else:
    new_text = fake_exp[:limit]

old_path = '/home/dana/Documents/Projects/SpaceOddity/_test/test.png'
if os.path.exists(old_path):
    os.remove(old_path)

cmd = \
    f'convert \
    -size {width} \
    -pointsize {font_size} \
    -background none \
    -fill rgba(255,255,255,1.0) \
    caption:\"{new_text}\" \
    {old_path}'
cmd_array = shlex.split(cmd)

proc = subprocess.Popen(cmd_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
str_out, str_err = proc.communicate()

size = width * font_size * limit
print('size:', size)
print('out:', str_out.decode())
print('err:', str_err.decode()[:80])

# skinny/short:
# skinny/tall
# wide/short:
# wide/tall:
