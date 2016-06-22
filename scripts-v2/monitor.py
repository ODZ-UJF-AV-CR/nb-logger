#!/usr/bin/python

# Data acquisition control script
# Limited threading version

# GPS part from code by Dan Mandle http://dan.mandle.me September 2012, License: GPL 2.0 

import time
import datetime
import sys
import logging 
import re

import os
from gps import *
from time import *
import time
import threading

from pymlab import config

import m_settings as g
#import m_pcrd
import m_nb as nb
import m_gps
import m_cpu
import m_i2c

import m_reboot

# Get sensor value or -1 if not available
def dv(sname):
  if sname in g.data:
    return(g.data[sname])
  else:
    return(-1)

###################################################################
# Parts
nb_enabled      = True
pcrd_enabled    = False
gps_enabled     = True
cputemp_enabled = True
i2c_enabled     = True

#### Settings #####
#data_dir="/data/balon/"
log_dir=g.data_dir

# Logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s',
                    filename=log_dir+'monitor.log'
                    )

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# Start
logging.info("# Data acquisition script started")
run_start=time.time()

###################################################################
# NB
if nb_enabled:
  arr = ['Epoch','GPS_Alt[m]','Pressure[Pa]'] + nb.get_header()
  nb.store(arr)

###################################################################
# GPS thread initialization and startup
if gps_enabled:
  logging.info("Initializing GPS interface.")
  gpsp = m_gps.GpsPoller() # create the thread
  gpsp.start() # start it up
else:
  logging.warning("GPS interface disabled.")

#### Data Logging #################################################
logging.warn('This is boot nr {0}'.format(m_reboot.get_n_boot_times()))
logging.warn('Beat time is {0} s'.format(g.round_beat))
m_reboot.append_boot_time()

bootcount = m_reboot.get_n_boot_times()

try:
    with open(g.data_dir+"data_log.csv", "a") as f:
        write_header=True

        # Endless main loop 
        while True:
          try:
            round_start=time.time()
            g.data['Epoch'] = round_start
            lcdargs = []

            # Reset NB if it is enabled
            if nb_enabled:
              g.data['nb_restime'] = nb.nb_reset()
            
            # System UTC epoch time
            csv_header = 'Epoch\t'
            lr="%d\t" % dv('Epoch')
 
            # GPS data 
            if gps_enabled:
              logging.info(gpsp.get_status_string())
              csv_header = csv_header + gpsp.get_header()
              logging.info('GPS status: Alt %.2f Fix: %i' % (gpsp.get_alt(), gpsp.get_fix()))
              lr = lr + gpsp.get_record()
              lcdargs.append('GA%.0f' % (gpsp.get_alt()))
              lcdargs.append(' FIX %.0f' % (gpsp.get_fix()))

            # CPU Temperature
            if cputemp_enabled:
              logging.info(m_cpu.get_status_string())
              csv_header = csv_header + m_cpu.get_header()
              lr=lr+m_cpu.get_record()

            # i2c sensors
            if i2c_enabled:
              i2c=m_i2c.get_i2c_data()
              csv_header += i2c['header']
              lr += i2c['record'] 

            # NB sensors
            if nb_enabled:
              # Gets an array, with sum of energies, number of pulses and then energies of events
              csv_header = csv_header + 'NB_Sum\tNB_Count\t'
              nb_records = nb.nb_retrieve()
              lr = lr + '\t'.join(map(str, nb_records[0:1])) + '\t'

              nb_sum = nb_records[0]
              nb_count = nb_records[1]
              lcdargs.append('NB %s' % (str(nb_count)))
              lcdargs.append(' S %s' % (str(nb_sum)))

              nb.store([round_start, gpsp.get_alt(), dv('Altimet_Press')] + nb_records)

            # If LCD available, update it
            if i2c_enabled:
              m_i2c.lcd(lcdargs)

          except ValueError as e:
            logging.critical("%s" % e)

          except TypeError as e:
            logging.critical("%s" % e)

          except IOError as e:
            logging.critical("%s" % e)
          
          finally:
            # End of sensors, write out data
            lr=lr + "\n"
            logging.info("-------------- Writing to file ------------------------\n")
            if write_header:
              f.write('%s\n' % csv_header)
              write_header = False
              
            f.write(lr) 
      	    f.flush()

            #################################################################  
            
            round_timeleft = g.round_beat + round_start - time.time()
            if (round_timeleft > 0) and (round_timeleft <= g.round_beat):
              time.sleep(round_timeleft)

except (KeyboardInterrupt, SystemExit):
    logging.error("Exiting.")
    #f.write("\r\n")
    f.close()
         
    if gps_enabled:
      try:
        gpsp.running = False
        logging.info("GPS thread asked to shut down.")
      except NameError:
        logging.error("GPS part enabled, but not initialized?")

    sys.exit(0)

