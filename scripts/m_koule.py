#!/usr/bin/python
#
# Non-threaded NB poller
# 

import m_settings as g
import time
import datetime
import logging
import serial
import math
import threading

port = '/dev/koule' # descriptive-name.rules includes SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", ATTRS{serial}=="A60181R1", SYMLINK+="koule"

baud = 9600

serial_port = serial.Serial(port, baud, timeout=5)

def handle_data(data):
  print(data)
  datafname = "/data/balon/data_koule.csv"
  with open(datafname, "a") as nbf:
    nbf.write(data)
  nbf.close()

def read_from_port(ser):
  connected = False
  while not connected:
    #serin = ser.read()
    connected = True

    while (True):
      if (ser.read()>0):
          time.sleep(0.1)
          reading = ser.read(ser.inWaiting()).rstrip()
          if reading != '':
             handle_data(str(time.time()) + ' ' + reading )#+ '\n')
          
try:
    thread = threading.Thread(target=read_from_port, args=(serial_port,))
    thread.start()

except (KeyboardInterrupt, SystemExit):
    logging.error("Exiting.")
    #f.write("\r\n")
    f.close()

    sys.exit(0)
