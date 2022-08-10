# get lock file (write-only, create if necessary)
lock_file = os.open(f"/tmp/" + str_prog_name + ".lock",
        os.O_WRONLY | os.O_CREAT)

# check for existance of lock file
try:
    fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    already_running = False
except IOError:
    already_running = True

# a nother instance is running, log and exit normally
if already_running:
    logging.debug("Already running")
    sys.exit(0)