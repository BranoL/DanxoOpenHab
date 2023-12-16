#!/usr/bin/env python
# coding=UTF-8

import time
import threading
import sys
import datetime
from influxdb import InfluxDBClient
import logging
import logging.handlers
import paho.mqtt.client as mqtt
import json

# MQTT nastavenia
mqtt_username = "openhab"
mqtt_password = "1234"
client_id = "1111"
mqt_broker = "127.0.0.1"
# mqt_broker = "192.168.1.2"

# Set this variables, influxDB should be localhost on Pi
host = "localhost"
port = 8086
user = "python"
password = "python"
 
# The database we created
dbname = "teploty_db"

tepl_in_topic = "home/temp/out"

# funkcia pripojenie MQTT
def connect_task(): 
    pripojit = True
    while pripojit:
        try:
            logger.info ('MQTT try connect to: ' + mqt_broker)
            client.connect(mqt_broker, 1883, 60)
        except Exception as chyba:
            logger.error('MQTT connect chyba')
            logger.info ('MQTT reconnect za 5 sekund')
            time.sleep(5)
        else:
            client.loop_start()
            pripojit = False
    return
# Volanie po pripojeni na MQTT broker
def on_connect(client, userdata, flags, rc):
    logger.info("MQTT Broker "+ mqt_broker +" connected with result code "+str(rc))
    client.subscribe(tepl_in_topic) # odoberat vsetky rolety JSON
# Volanie ked je prijata saprva s MQTT brokera
def on_message(client, userdata, msg):
    if msg.topic == tepl_in_topic:
        logger.info('MQTT < subscribe teploty topics: ' + str(msg.payload))  
        m_decode=str(msg.payload.decode("utf-8","ignore"))
        m_in=json.loads(m_decode) #decode json data
        logger.info("Teplota 1 = " + m_in["Teplota1"])
        logger.info("Teplota 2 = " + m_in["Teplota2"])
        logger.info("Teplota 3 = " + m_in["Teplota3"])
        logger.info("Teplota 4 = " + m_in["Teplota4"])
        logger.info("Teplota 5 = " + m_in["Teplota5"])
        json_body = [
        {
          "measurement": "Teploty",
              "tags": {
                  "typ": "DS18B20",
                  },
            #   "time": time.ctime(),
              "fields": {
                  "Teplota1" : float(m_in["Teplota1"]), "Teplota2" : float(m_in["Teplota2"]), "Teplota3" : float(m_in["Teplota3"]),
                  "Teplota4" : float(m_in["Teplota4"]),"Teplota5" : float(m_in["Teplota5"])
              }
          }
        ]
        # Write JSON to InfluxDB
        try:
            client_db.create_database(dbname)
            client_db.write_points(json_body)
            logger.info("Data do databazy zapisane")
        except Exception as e:
            logger.error("Influx error write points")
            
    return

# create logger 
logger = logging.getLogger('Databaza Influx')
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
# fh = logging.handlers.RotatingFileHandler('temp.log', maxBytes=5000000, backupCount=5)
ch.setLevel(logging.DEBUG)
# fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
# fh.setFormatter(formatter)
logger.addHandler(ch)
# logger.addHandler(fh)

# instancia MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
t1 = threading.Thread(target=connect_task, args=[])
t1.start()
# Create the InfluxDB object
client_db = InfluxDBClient(host, port, user, password, dbname)
while True:
    try:
        logger.info ('Influx try connect to: ' + host )
        client_db.create_database(dbname)
    except Exception as e:
        logger.error("Influx error create database")
        time.sleep(15)
    else:
        break


# Run until keyboard out
try:
    while True:
        # Wait for next sample
        time.sleep(10)
 
except KeyboardInterrupt:
    pass