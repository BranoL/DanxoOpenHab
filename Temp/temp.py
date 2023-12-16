#!/usr/bin/env python
# coding=UTF-8
"""
===============================================================================
LB Electronics
Potrebuje 
    w1thermsensor python library: 
        pip install w1thermsensor (https://github.com/timofurrer/w1thermsensor)
    paho mqtt python library: 
        pip install paho-mqtt  (https://github.com/eclipse/paho.mqtt.python)

Spustit s: python temp.py
"""

from __future__ import absolute_import, division, print_function, \
                                                    unicode_literals
import time
import threading
import paho.mqtt.client as mqtt
from w1thermsensor import W1ThermSensor
import json
import logging
import logging.handlers


# MQTT nastavenia
mqtt_username = "openhab"
mqtt_password = "1234"
client_id = "1111"
mqt_broker = "127.0.0.1"
# mqt_broker = "192.168.1.2"

# Publish teploty
teploty_out = {"Teplota1":"20.00",
            "Teplota2":"20.00",
            "Teplota3":"20.00",
            "Teplota4":"20.00",
            "Teplota5":"20.00"
            }
tepl_out_topic = "home/temp/out"


class publikovat: # priznak ze je treba publikovat 
    pass
class data_out: # vystupne string JSON na publikovanie
    """Vystupne JSON stringy
    rolety
    rolety_time
    svetla
    teploty
    """
    pass
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
def teploty_task(): 
    """Senzory
    28-000008ffe937  Obyvacka
    28-000009a5ce43  Izba zapad
    28-000009a5d8b3  Izba vychod
    28-000009a6863d  Spalna
    28-000009a74603  Kupelna
    """
    while True:
        try:
            logger.info('Start citania senzorov')
            for sensor in W1ThermSensor.get_available_sensors():
                sen_id = sensor.id
                sen_temp = sensor.get_temperature()
                logger.info("Senzor %s: %.2f °C" % (sen_id, sen_temp))
                if sen_id == "000008ffe937":  # Obyvacka
                    pub_teploty_out("Teplota1",str(sen_temp))
                if sen_id == "000009a67a4d":  # Obyvacka
                    pub_teploty_out("Teplota1",str(sen_temp))
                if sen_id == "000009a5d8b3":  # Izba vychod
                    pub_teploty_out("Teplota2",str(sen_temp))
                if sen_id == "000009a74603":  # Kupelna
                    pub_teploty_out("Teplota3",str(sen_temp))
                if sen_id == "000009a5ce43": # Izna zapad
                    pub_teploty_out("Teplota4",str(sen_temp))
                if sen_id == "000009a6863d": # Spalna
                    pub_teploty_out("Teplota5",str(sen_temp))
            # pub_teploty_out("Teplota1","21.00")
            # pub_teploty_out("Teplota2","22.00")
            # pub_teploty_out("Teplota3","23.00")
            # pub_teploty_out("Teplota4","24.00")
            # pub_teploty_out("Teplota5","25.00")
            time.sleep(60) # Obnova 
        except:
            logger.error('DS18B20 nepripojeny caka sa 60 sekund')
            time.sleep(60)
# Vytvorenie JSON spravy
def pub_teploty_out(item="Teplota1",state="22.00"):
     # Konvert spravy na JSON
    teploty_out[item] = state
    data_out.teploty=json.dumps(teploty_out)# encode oject to JSON
    publikovat.teploty = True # priznak publikovat v main 
# Volanie po pripojení na MQTT broker
def on_connect(client, userdata, flags, rc):
    logger.info("MQTT Broker "+ mqt_broker +" connected with result code "+str(rc))
# Volanie ked je prijata saprva s MQTT brokera
def on_message(client, userdata, msg):
    return
# create logger

logger = logging.getLogger('Teploty')
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

data_out.teploty = ""
publikovat.teploty = False

# instancia MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
t1 = threading.Thread(target=connect_task, args=[])
t1.start()

t2 = threading.Thread(target=teploty_task, args=[])
t2.start() 

def main():
    pass

if __name__ == "__main__":
    main()
    while True:
        try:
            if publikovat.teploty == True:
                # logger.info ("data out teploty=" + data_out.teploty)
                client.publish(tepl_out_topic,data_out.teploty,0,True)
                publikovat.teploty = False
            time.sleep(2)
        except IOError:
            time.sleep(2)