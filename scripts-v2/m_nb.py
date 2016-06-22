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

NaN = float('nan')

#### Store a data line into file ####
def store(record = []):
  try:
    datafname = g.data_dir+"data_nb.csv"
    with open(datafname, "a") as nbf:
      nbf.write('\t'.join(map(str,record)) + '\n')
    nbf.close()

  except IOError as e:
    logging.critical("%s" % e)

#### Reset NB ####
def nb_reset():
  logging.info('Resetting NB memory')
  reset_time = NaN
  try:
    ser = serial.Serial(nb_port, timeout=5)
    reset_time = time.time()
    ser.write(b'x')

  except IOError as e:
    logging.critical("%s" % e)
    reset_time = NaN 

  finally:
    return(reset_time) 

#### CSV header ####
def get_header():
  array = ['NB_Sum', 'NB_Count'] 
  for i in range(1,1000):
    array.append('NB_%i' % (i))
  return(array)

#### NB retriever ####
def nb_retrieve():
  nb_port = '/dev/USB0'
  result = [NaN,NaN]
  # Open the serial port
  try:
    looptime = time.time() - g.data['nb_restime']
    logging.info("NB readout looptime: %.2f" % (looptime))

    ser = serial.Serial(nb_port, timeout=5)
    logging.info("Port opened for NB readout: %s" % (ser.name))

    # Retrieve data via serial line
    ser.write(b'r')
    record = ser.readline().lstrip().rstrip()

    # Records are retrieved as strings - convert them to integers, that they truly are
    records = record.split(',')  
    irecords = map(int,records)

    # Compute sum of pulses
    suma = sum(map(int,records[1:]))

    result = [suma] + irecords

    logging.info("NB: {} events with total of {:.0f} recorded in {:.2f} since {:s}.".format(records[0], suma, looptime, time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(g.data['nb_restime']))))

    g.data['nb_count_ps'] = 1.0*float(records[0])/looptime
    g.data['nb_sum_ps'] = 1.0*float(suma)/looptime
    ser.close()

  except IOError as e:
    logging.critical("%s" % e)

  finally:
    return(result)

#### main ####
if __name__ == '__main__':
  try:
    logging.basicConfig(level=logging.INFO,
                      format='%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s',
                      )

    logging.info('Starting NB readout')

    # Reset NB timer
    g.data['nb_restime'] = nb_reset()
    logging.info('NB reset at: %s' % (g.data['nb_restime']))
    logging.info('NB readout: ' + ' '.join(nb_retrieve()))
  except (KeyboardInterrupt,SystemExit):
    logging.info("NB thread asked to exit")
  

