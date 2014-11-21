'''
DQSEGDB Python Server
Logging config file
'''

# Import.
import Constants
import logging
from logging import FileHandler, StreamHandler
import time

# Set current date/time, used in creating log file.
now = time.localtime()
now = time.strftime("%Y-%m-%d", now)

# Instantiate objects.
constant = Constants.ConstantsHandle()

#default_formatter = logging.Formatter(now_w_s + ":%(levelname)s:%(message)s")
#default_formatter = logging.Formatter(":%(asctime)s:%(levelname)s:%(message)s",
#                                      "%Y-%m-%d %H:%M:%S")
default_formatter = logging.Formatter(":%(asctime)s:%(levelname)s:%(message)s")

console_handler = StreamHandler()
console_handler.setFormatter(default_formatter)

# Set log-file.
error_handler = FileHandler(constant.log_file_location + now + '.log', 'a')
#error_handler.setLevel(logging.ERROR)
error_handler.setLevel(logging.DEBUG)
error_handler.setFormatter(default_formatter)

root = logging.getLogger()
root.addHandler(console_handler)
root.addHandler(error_handler)
root.setLevel(logging.DEBUG)