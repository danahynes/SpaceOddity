import shlex
import subprocess

pic_path = '/home/dana/Documents/Projects/SpaceOddity/_static/test.jpg'


cmd = \
    f'identify \
    -format %w \
    {pic_path}'
cmd_array = shlex.split(cmd)

# proc = subprocess.Popen(cmd_array, stdout=subprocess.PIPE,
#                         stderr=subprocess.PIPE)
# str_out, str_err = proc.communicate()

# print('out:', str_out.decode())
# print('err:', str_err.decode())

# proc = subprocess.run(cmd_array, capture_output=True)
# out = proc.stdout.decode()
# err = proc.stderr.decode()
# if err is not None:
#     print('ERROR')

# print('out:', out)
# print('err:', err)

try:
    proc = subprocess.run(cmd_array, check=True, capture_output=True)

    print('ret:', proc.returncode)
    print('out:', proc.stdout.decode())
    print('err:', proc.stderr.decode())

except subprocess.CalledProcessError as e:

    print('err ret:', e.returncode)
    print('err out:', e.stdout.decode())
    print('err err:', e.stderr.decode())
