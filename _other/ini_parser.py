
import os

class ConfParser:

    file = ''

    def __init__(self):
        pass
    def parse(self, file):
        file = file
        pass


try:

    if os.path.exists(file):
        with open(file, "r") as f:
            lines = f.readlines()

            # read key/value pairs from conf file
            for line in lines:
                line_clean = line.strip().upper()

                # ignore comment lines or blanks or lines with no values
                if line_clean.startswith("#") or line_clean == "":
                    continue

                # split key off at equals
                key_val = line_clean.split("=")
                key = key_val[0].strip()

                # split val off ignoring trailing comments
                val = ""
                if (len(key_val) > 1):
                    val_array = key_val[1].split("#")
                    val = val_array[0].strip()

                # check if we are enabled
                if key == "ENABLED":
                    if val != "":
                        enabled = int(val)

                # # get delay
                # if key == "DELAY":
                #     if val != "":
                #         delay = int(val)

                # get caption
                if key == "CAPTION":
                    if val != "":
                        caption = int(val)

except Exception as e:
    logging.debug(str(e))

if not enabled:
    logging.debug("Not enabled")
    sys.exit(0)

    # test