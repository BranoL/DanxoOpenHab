#!/usr/bin/env python
# coding=UTF-8
"""
================================================
LBElectronics 

Requires python smbus to be installed
For Python 2 install with: sudo apt-get install python-smbus
For Python 3 install with: sudo apt-get install python3-smbus

run with: python lights.py
"""
from __future__ import absolute_import, division, print_function, \
                                                    unicode_literals
import time
import threading
import os
import paho.mqtt.client as mqtt
import sys
import ConfigParser
from config import *
from IOPi import IOPi
import logging
import logging.handlers
import json
from datetime import datetime
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
func = GPIO.gpio_function(15)
GPIO.setup(15, GPIO.OUT)
GPIO.output(15, False)

class gpioa: # vystupny port 0x20 a
    """0x20 GPA
    """
    pass
class gpiob: # vstupny port 0x20 b
    """0x20 GPB
    """
    pass
class gpioc: # vystupny port 0x21 a
    """0x21 GPA
    """
    pass
class gpiod: # vstupny port 0x21 b
    """0x21 GPB
    """
    pass
class gpioe: # vystupny port 0x22 a
    """0x22 GPA
    """
    pass
class gpiof: # vstupny port 0x22 b
    """0x22 GPB
    """
    pass
class gpiog: # vystupny port 0x23 a
    """0x23 GPA
    """
    pass
class gpioh: # vstupny port 0x23 b
    """0x23 GPB
    """
    pass
class gpioi: # vystupny port 0x24 a
    """0x24 GPA
    """
    pass
class gpioj: # vstupny port 0x24 b
    """0x24 GPB
    """
    pass
class gpiok: # vstupny port 0x25 a
    """0x25 GPA
    """
    pass
class gpiol: # vstupny port 0x25 b
    """0x25 GPB
    """
    pass
class gpiom: # vstupny port 0x26 a
    """0x26 GPA
    """
    pass
class gpion: # vstupny port 0x26 b
    """0x26 GPB
    """
    pass
class dummy: # dummy register portu
    pass
class dummya: # dummy register portu
    pass
class dummyb: # dummy register portu
    pass
class rolety: # trieda rolety - parametre a tvorba prikazov UP/DOWN/STOP, riadenie vystupov
    """Riadenie roliet
        
    Keyword Arguments:
        port_in {class} -- Vstupny port (default: {gpioa})
        port_out {class} -- Vystupny port (default: {gpiob})
        cmd_down {int} -- Cislo vstupu povel DOWN (default: {0})
        cmd_up {int} -- Cislo vstupu povel UP (default: {1})
        out_on {int} -- Cislo vystupu povel ON (default: {0})
        out_up {int} -- Cislo vystupu povel UP (default: {1})
        name {string} -- Oznacenie rolety pre publish JSON (default: {"Roletal"})
    """
    def __init__(self,port_in=gpioa(),port_out=gpiob(),cmd_down=0,cmd_up=1,out_on=0,out_up=1,name="Roletal"):
        self.port_in = port_in
        self.port_out = port_out
        self.cmd_down = cmd_down
        self.cmd_up = cmd_up
        self.out_on = out_on
        self.out_up = out_up
        self.prev_port = port_in.port
        self.command ="STOP"
        self.prev_command = "STOP"
        self.tdown = threading.Timer(5.0,self.tend)
        self.tup = threading.Timer(5.0,self.tend)
        self.time_rol = 5.0
        self.press_rol = 1.0
        self.name = name # meno v dictionary pre publikovanie stavu
        self.timedownon = time.time()
        self.timeupon = time.time() 
    def commands_make(self):
        self.xzmena = self.prev_port ^ self.port_in.port
        if self.xzmena&(1<<self.cmd_down):
            if self.port_in.port&(1<<self.cmd_down):
                if self.command == "STOP":
                    self.command ="DOWN"
                else:
                    self.command ="STOP"
                self.timedownon = time.time()   # Zapis casu pre meranie
                logger.info("Tlacitko dole '" + self.name + "' stlacene")
                
            else:
                self.timecloseddown = time.time()-self.timedownon   # Odmeranie casu zopnutia vtsupu
                logger.info ("Tlacitko dole '" + self.name + "' uvolnene > Dlzka impulzu: " + str(self.timecloseddown) + " ms")
                if self.timecloseddown  <= self.press_rol:
                    self.command ="STOP"
        if self.xzmena&(1<<self.cmd_up):
            if self.port_in.port&(1<<self.cmd_up):
                if self.command == "STOP":
                    self.command ="UP"
                else:
                    self.command ="STOP"
                self.timeupon = time.time()   # Zapis casu pre meranie
                logger.info("Tlacitko hore '" + self.name + "' stlacene")
            else:
                self.timeclosedup = time.time()-self.timeupon   # Odmeranie casu zopnutia vtsupu
                logger.info ("Tlacitko hore '" + self.name + "' uvolnene > Dlzka impulzu: " + str(self.timeclosedup) + " ms")
                if self.timeclosedup  <= self.press_rol:
                    self.command ="STOP"
        self.prev_port =  self.port_in.port
    def roller_control(self):
        if self.command != self.prev_command:
            # smer dole
            if self.command == "UP":
                # zrusi timer pre opacny smer
                self.tup.cancel()
                if self.port_out.port &(1<<self.out_on) == 0 :    # ak je uz vystup zopnuty vypnut
                    self.command ="STOP"
                    # self.port_out.port |=(1<<self.out_on)  # Vypnutie vystupu
                    # self.port_out.port |=(1<<self.out_up)
                    # vypne casovac rolety
                    self.tdown.cancel() 
                    pub_rolety_out(self.name,"STOP")
                else:
                    # self.port_out.port |=(1<<self.out_up)
                    # self.port_out.port &=~(1<<self.out_on)   # Zapnutie vystupov
                    # spusti casova rolety
                    if self.tdown.isAlive():
                        self.tdown.cancel()    
                    self.tdown = threading.Timer(self.time_rol,self.tend)
                    self.tdown.start() 
                    pub_rolety_out(self.name,"UP") 
            if self.command == "DOWN":
                 # zrusi timer pre opacny smer
                self.tdown.cancel()
                if self.port_out.port &(1<<self.out_on) == 0:    # ak je uz vystup zopnuty vypnut
                    self.command ="STOP"
                    # self.port_out.port |=(1<<self.out_on)  # Vypnutie vystupu
                    # self.port_out.port |=(1<<self.out_up)
                    # vypne casovac rolety
                    self.tup.cancel()
                    pub_rolety_out(self.name,"STOP")
                else:
                    # self.port_out.port &=~(1<<self.out_up)
                    # self.port_out.port &=~(1<<self.out_on)   # Zapnutie vystupov 
                    # spusti casova rolety
                    if self.tup.isAlive():
                        self.tup.cancel()
                    self.tup = threading.Timer(self.time_rol,self.tend)
                    self.tup.start()
                    pub_rolety_out(self.name,"DOWN")
            if self.command == "STOP":
                 if not (self.port_out.port &(1<<self.out_on) and self.port_out.port &(1<<self.out_up)):
                        # self.port_out.port |=(1<<self.out_up)  # Vypnutie vystupu
                        # self.port_out.port |=(1<<self.out_on)
                        # vypne casovac rolety
                        if self.tdown.isAlive():
                            self.tdown.cancel()
                        if self.tup.isAlive():
                            self.tup.cancel() 
                        pub_rolety_out(self.name,"STOP")
        self.prev_command = self.command
        self.riadenie_vystupov()
    def tend(self):
        logger.info (self.name + ' > Timer  docasoval ' + str(self.time_rol) + ' s')
        self.command ="STOP"
        # self.port_out.port |=(1<<self.out_up)  # Vypnutie vystupu
        # self.port_out.port |=(1<<self.out_on)
        pub_rolety_out(self.name,"STOP")
    def riadenie_vystupov(self):
        
        if self.command == "STOP":
            if self.port_out.port &(1<<self.out_on) == 0:   # ak je zopnutý relé smeru najprv vypne relé on
                self.port_out.port |= (1<<self.out_on)
                # logger.debug (self.command + " vypnute rele on")
            else: 
                if self.port_out.port &(1<<self.out_up) == 0: # v nasledujucom cykle vypne relé smeru
                    self.port_out.port |= (1<<self.out_up)
                    # logger.debug (self.command + " vypnute rele up")
            return

        if self.command == "UP":
            if self.port_out.port &(1<<self.out_up) == 0:   # ak je zopnuté relé smeru najprv ho vypne
                self.port_out.port |= (1<<self.out_up)
                # logger.debug (self.command + " vypnute rele up")
            else:  
                if self.port_out.port &(1<<self.out_on):  # v nasledujucom zopne pohyb rele on
                    self.port_out.port &=~(1<<self.out_on)
                    # logger.debug (self.command + " zapnutie rele on")
            return

        if self.command == "DOWN":
            if self.port_out.port &(1<<self.out_up):   # ak je vypnuté relé smeru najprv zapne toto relé
                self.port_out.port &=~(1<<self.out_up)
                # logger.debug (self.command + " zapnutie rele up")
            else:                                           # v nasledujucom cykle zopne rele on
                if self.port_out.port &(1<<self.out_on):  # v nasledujucom zopne pohyb rele on
                    self.port_out.port &=~(1<<self.out_on) 
                    # logger.debug (self.command + " zapnutie rele on")
            return
class rolety_spolocne:
    """
    Spolocne ovladanie roliet
    """
    def __init__(self,port_in=gpiob,cmd_down=0,cmd_up=1):
        self.port_in = port_in
        self.cmd_down = cmd_down
        self.cmd_up = cmd_up
        self.prev_port = port_in.port
        self.command ="STOP"
        self.prev_command = "STOP"
        self.tdown = threading.Timer(0.25,self.t_down_end)
        self.tup = threading.Timer(0.25,self.t_up_end)
        self.name = "All"   # meno v dictionary pre publikovanie stavu
        self.pohyb = False  # info o tom ze rolaty maju prikaz
    def commands_make(self):
        self.xzmena = self.prev_port ^ self.port_in.port
        if self.xzmena&(1<<self.cmd_down):
            if self.port_in.port&(1<<self.cmd_down):
                if self.command == "STOP":
                    self.command ="DOWN"
                else:
                    self.command = "STOP"
        if self.xzmena&(1<<self.cmd_up):
            if self.port_in.port&(1<<self.cmd_up):
                if self.command == "STOP":
                    self.command ="UP"
                else:
                    self.command = "STOP"
        self.prev_port =  self.port_in.port
    def roller_control(self):
        """Funkcia otestuje ci prisiel novy prikaz
        Ak bol predchazdajuci prikaz STOP testuje ci novy prikaz je DOWN alebo UP
        potom posle pre pripad ze by bola nejaka roleta v chode najpr STOP vsetkym 
        roletam v skupine a spusti casovac na oneskorene zapnutie smeru chodu roliet
        Ak bol predchadzajuci prikaz UP alebo DOWN to znamena ze treba zastavit
        rolety, zrusia sa casovace a posle sa pr e vsetky rolety prikaz STOP.
        Nastavi sa priznak pohybu na FALSE
        Ak je priznak pohyb = TRUE(nastavuje sa po spusteni pohyb roliet)
        testuje sa stav roleit v skupine a ak su vsetky STOP nasstavit prikaz na stop
        """
        if self.command != self.prev_command:
            # print (str(datetime.now()) + ': Novy prikaz: '+ self.command)
            if self.prev_command == "STOP": # predchadajuci prikaz bol stop tak moze spusti  pohyby
                if self.command =="DOWN": # ak je príkaz stop zastavit vestky roleta a potom dat povel dole
                    for item in g_rolety:
                        item.command = "STOP"
                    #start casovaca do spustenia pohybu
                    self.tdown = threading.Timer(0.1,self.t_down_end)
                    self.tdown.start() 
                    # logger.info("Spolocne ovladanie roliet smer dole za 0,25 s")
                    # print (str(datetime.now()) + ': Start timer DOWN')
                    pub_rolety_out(self.name,"DOWN")
                if self.command == "UP":
                    for item in g_rolety:
                        item.command = "STOP"
                    #start casovaca do spustenia pohybu
                    self.tup = threading.Timer(0.1,self.t_up_end)
                    self.tup.start()
                    # logger.info("Spolocne ovladanie roliet smer hore za 0,25 s")
                    # print (str(datetime.now()) + ': Start timer UP')
                    pub_rolety_out(self.name,"UP")
            else : # predchadzajuci prikaz nebol STOP tak zastavit pohyb
                # zastavit casovace
                self.tdown.cancel()
                self.tup.cancel()
                for item in g_rolety:
                    item.command = "STOP"
                self.pohyb = False
                self.command = "STOP"
                pub_rolety_out(self.name,"STOP")
            self.prev_command = self.command
        if self.pohyb == True:
            if all_test_command(g_rolety,"STOP"):
                self.pohyb = False
                self.command = "STOP"
                self.prev_command = self.command
                pub_rolety_out(self.name,"STOP")
    def t_down_end(self):
        # logger.info("Spolocne ovladanie roliet smer dole")
        # print (str(datetime.now()) + ': Prikaz DOWN')
        for item in g_rolety:
            item.command = "DOWN"
        self.pohyb = True
        # print (str(datetime.now()) + ': Koniec DOWN')
    def t_up_end(self):
        # logger.info("Spolocne ovladanie roliet smer hore")
        # print (str(datetime.now()) + ': Prikaz UP')
        for item in g_rolety:
            item.command = "UP"
        self.pohyb = True
        # print (str(datetime.now()) + ': Kooniec UP')
        
class svetla_spolocne: 
    def __init__(self,port_in = gpiob,cmd_on = 0): # konstruktor
        self.port_in = port_in
        self.cmd_on = cmd_on
        self.prev_port = port_in.port
        self.command ="NA"
        self.prev_command = "NA"
        self.topic = "All"
    def commands_make(self):
        self.xzmena =  self.prev_port ^ self.port_in.port
        if self.xzmena&(1<<self.cmd_on):
            if self.port_in.port&(1<<self.cmd_on):
                if self.command == "OFF":
                    self.command = "ON"
                    pub_svetla_out(self.topic,"ON")
                else:
                    if self.command == "ON":
                        self.command = "OFF"
                    pub_svetla_out(self.topic,"OFF")
        self.prev_port =  self.port_in.port
    def light_control(self):
        """Funkcia otestuje ci prisiel novy prikaz
        ak je novy prikaz ON alebo OFF zapise ho do vsetky svetiel v skupine svetiel
        a po vykonani sa prikaz vymaze > NA - signalizuje ze sa ocakava dalsi novy pikaz 
        """
        # Test novy prikaz
        if self.command != self.prev_command:
            # zapnut svetlo
            if self.command == "ON":    # Zapnutie vystupov
                for item in g_svetla:   # Vsetky svetla v skupine zapnut
                    item.command = "ON"
                self.command = "NA" # Prikaz vykonany > vymazat
            if self.command == "OFF":   # Vypnutie vystupu
                for item in g_svetla:   # Vsetky svetla v skupine vypnut
                    item.command = "OFF"
                self.command ="NA" # Prikaz vykonany > vymazat
        self.prev_command = self.command  
class vstupy: # trieda vstupy
    """Spracovanie vstupu
            Vstup môže mať dva stavy OPEN/CLOSED. Zároveň sa meria čas zopnutia tlač.
            a ak je čas dlhší ako nastavená hodnota nastaví sa príkaz scena na ON. Scena sa vráti
            do NA po spracovaní v ďalšom behu programu.
    Keyword Arguments:
            port_in {class} -- Vstupny port (default: {gpioa})
            pin {int} -- Cislo vstupu povel ON/OFF (default: {0})
            name {string} -- Oznacenie vstupu pre publish JSON (default: {"Vstup1"})
    """ 
    def __init__(self,port_in = gpioa(),pin = 0, name = "Vstup 1)"):   # Kontstruktor
        self.port_in = port_in
        self.pin = pin
        self.name = name
        self.state = "OPEN" # Stav vstupu
        self.scena = "NA"   # Príkaz scény
        self.prev_port = port_in.port # Pomocný register sledovanie zmeny vstupu
        self.time_on = time.time()  # Čas stlačenia tlačitka
        self.time_impulz = 1.0      # Nastavená dľžka impulzu
        self.timer = threading.Timer(1.0,self.tend)
    def commands_make(self):
        self.xzmena =  self.prev_port ^ self.port_in.port # Porovnanie akt. a predch. stavu portu
        if self.xzmena&(1<<self.pin):
            if self.port_in.port&(1<<self.pin):
                if self.timer.isAlive():
                    self.timer.cancel()
                self.state = "CLOSED"
                self.timer = threading.Timer(1.0,self.tend)
                self.timer.start()
                self.time_on = time.time()   # Zapis casu pre meranie
                logger.info("Tlacitko '" + self.name + "' stlacene")
                pub_tlacidla_out(self.name,"CLOSED")
            else:
                if self.timer.isAlive():
                    self.timer.cancel()
                self.state = "OPEN"
                self.timeclosed = time.time()-self.time_on   # Odmeranie casu zopnutia vstupu
                logger.info ("Tlačidlo '" + self.name + "' uvolnene > Dlzka impulzu: " + str(self.timeclosed) + " ms") 
                pub_tlacidla_out(self.name,"OPEN")
        self.prev_port =  self.port_in.port 
    def tend(self):
        self.scena ="ON"
        logger.info("Scéna >> " + self.scena)
class vystupy: # trieda výstupy
    """Riadenie výstupov
            Sleduje príkaz a zapína elbo vypína svetlo
    Keyword Arguments:
            vstup {class} -- príkaz od vstupu trieda (default: {vstupy})
            výstup {class} -- Výstupny port (default: {gpiob})
            pin {int} -- Cislo vystupu riadenie svetla (default: {0})
            name {string} -- Oznacenie vstupu pre publish JSON (default: {"Vystup1"})
    """
    def __init__ (self,vstup,port_out = gpiob,pin = 0, name = "Vystup1"):
        self.vstup = vstup
        self.port_out = port_out
        self.pin = pin
        self.name = name
        self.prev_command = "OFF"
        self.command = "OFF" 
        self.prev_vstup ="OPEN"
    def control(self):
        if self.prev_vstup != self.vstup.state: # Došlo k zmene vstupu?
            self.prev_vstup = self.vstup.state  # Nový stav do pomocného registra
            if self.vstup.state == "CLOSED":  # Ak je zopnutý prepnúť príkaz ON/OFF
                if self.command == "ON":
                    self.command = "OFF"
                else:
                    self.command = "ON"
        if self.prev_command != self.command:
            if self.command == "ON":
                self.port_out.port &=~(1<<self.pin)   # Zapnutie vystupov   
                pub_svetla_out(self.name,"ON")
            if self.command == "OFF":
                self.port_out.port |=(1<<self.pin)  # Vypnutie vystupu
                pub_svetla_out(self.name,"OFF")
            self.prev_command = self.command  
class skupiny_svetiel: # skupina svetiel
    """Riadenie skupiny svetiel:
       Vstup riadi skupinu svetiel. Svetlá môžu byť súčasťou nejakej skupiny na základe vstupu
       je táto skupina zopnutá
    Keyword Arguments:
            vstup {class} -- Riadiaci vstup
            skupina{list} -- Vstupny port (default: {gpioa})
            name {string} -- Oznacenie skupiny publish JSON (default: {"Scena 1"})
    """
    def __init__(self,vstup, skupina, name = "Scena 1"):
        self.vstup = vstup
        self.skupina = skupina
        self.name = name
        self.prev_scene = "NA"
    def scene(self):
        # logger.info("Skupina scene >> " + self.vstup.scena)
        if self.prev_scene != self.vstup.scena:
            if self.vstup.scena == "ON":
                for item in self.skupina:
                    item.command = "ON"
        self.prev_scene = self.vstup.scena

class publikovat: # priznak ze je treba publikovat 
    pass
class data_out: # vystupne string JSON na publikovanie
    """Vystupne JSON stringy
    rolety
    rolety_time
    svetla
    """
    pass
# funkcia inicializuje stav portov
def ports_init(): 
    gpioa.port = 0xFF # Vystupny port
    gpiob.port = 0x00 # vystupny port
    
    gpioc.port = 0xFF # Vystupny port
    gpiod.port = 0x00    # Vstupny port
    
    gpioe.port = 0xFF # Vystupny port
    gpiof.port = 0x00     # Vstupny port
    
    gpiog.port = 0xFF # Vystupny port
    gpioh.port = 0x00     # Vstupny port

    gpioi.port = 0xFF # Vystupny port
    gpioj.port = 0x00     # Vstupny port

    gpiok.port = 0xFF # Vystupny port
    gpiol.port = 0x00     # Vstupny port

    gpiom.port = 0xFF # Vystupny port
    gpion.port = 0x00     # Vstupny port

    dummy.port = 0x00
    dummya.port = 0x00
    dummyb.port = 0x00
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
# pokusa sa pripojit na MCP23017
def connected_mcp_task():
    global iobus1
    global iobus2
    global iobus3
    global iobus4
    global iobus5
    global iobus6
    global iobus7
    iobus1 = None
    iobus2 = None
    iobus3 = None
    iobus4 = None
    iobus5 = None
    iobus6 = None
    iobus7 = None
    pripojeny = False
    while pripojeny == False:
        pripojeny = True
        # iobus 1
        try:
            if iobus1 == None:
                # instancia IOpi  
                iobus1 = IOPi(0x20)
                logger.info('MCP 0x20 pripojene na: ' + str(iobus1))
                mcp_init_setup()
        except IOError:
            logger.error('MCP 0x20 IOError')
            pripojeny = False
        # iobus 2
        try:
            if iobus2 == None:
                # instancia IOpi  
                iobus2 = IOPi(0x21)
                logger.info('MCP 0x21 pripojene na: ' + str(iobus2))
                mcp_init_setup()
        except IOError:
            logger.error('MCP 0x21 IOError')
            pripojeny = False
        # iobus 3
        try:
            if iobus3 == None:
            # instancia IOpi  
                iobus3 = IOPi(0x22)
                logger.info('MCP 0x22 pripojene na: ' + str(iobus3))
                mcp_init_setup()
        except IOError:
            logger.error('MCP 0x22 IOError')
            pripojeny = False
        # iobus 4
        try:
            if iobus4 == None:
                # instancia IOpi  
                iobus4 = IOPi(0x23)
                logger.info('MCP 0x23 pripojene na: ' + str(iobus4))
                mcp_init_setup()
        except IOError:
            logger.error('MCP 0x23 IOError')
            pripojeny = False
        # iobus 5
        try:
            if iobus5 == None:
                # instancia IOpi  
                iobus5 = IOPi(0x24)
                logger.info('MCP 0x24 pripojene na: ' + str(iobus5))
                mcp_init_setup()
        except IOError:
            logger.error('MCP 0x24 IOError')
            pripojeny = False
        # iobus 6
        try:
            if iobus6 == None:
                # instancia IOpi  
                iobus6 = IOPi(0x25)
                logger.info('MCP 0x25 pripojene na: ' + str(iobus6))
                mcp_init_setup()
        except IOError:
            logger.error('MCP 0x25 IOError')
            pripojeny = False
        # iobus 
        try:
            if iobus7 == None:
                # instancia IOpi  
                iobus7 = IOPi(0x26)
                logger.info('MCP 0x26 pripojene na: ' + str(iobus7))
                mcp_init_setup()
        except IOError:
            logger.error('MCP 0x26 IOError')
            pripojeny = False
        logger.error('Dalsi pokus o vytvorenie spojenia s MCP za 30 sekund')
        logger.info(' Zapinanie power rele ')
        time.sleep(0.5)
        GPIO.output(15, True)
        time.sleep(30)
    return
# vychodzie nastavenie MCPeciek
def mcp_init_setup():
    if iobus1 != None:
        iobus1.set_port_direction(0, 0x00)  # GPIOA ako vystupy
        iobus1.set_port_direction(1, 0xFF)  # GPIOB ako vstupy
        iobus1.set_port_pullups(1, 0xFF)    # Pullup rezistory zapnúť na GPIOB
        iobus1.invert_port(1,0xFF)          # Invertovať polaritu na GPIOB
        # logger.info('Nastavenie MCP 0x20 bolo inicializovane')
    if iobus2 != None:
        iobus2.set_port_direction(0, 0x00)  # GPIOA ako vystupy
        iobus2.set_port_direction(1, 0xFF)  # GPIOB ako vstupy
        iobus2.set_port_pullups(1, 0xFF)    # Pullup rezistory zapnúť na GPIOB
        iobus2.invert_port(1,0xFF)          # Invertovať polaritu na GPIOB
        # logger.info('Nastavenie MCP 0x21 bolo inicializovane')
    if iobus3 != None:
        iobus3.set_port_direction(0, 0x00)  # GPIOA ako vystupy
        iobus3.set_port_direction(1, 0xFF)  # GPIOB ako vstupy
        iobus3.set_port_pullups(1, 0xFF)    # Pullup rezistory zapnúť na GPIOB
        iobus3.invert_port(1,0xFF)          # Invertovať polaritu na GPIOB
        # logger.info('Nastavenie MCP 0x22 bolo inicializovane')
    if iobus4 != None:
        iobus4.set_port_direction(0, 0x00)  # GPIOA ako vystupy
        iobus4.set_port_direction(1, 0xFF)  # GPIOB ako vstupy
        iobus4.set_port_pullups(1, 0xFF)    # Pullup rezistory zapnúť na GPIOB
        iobus4.invert_port(1,0xFF)          # Invertovať polaritu na GPIOB
        # logger.info('Nastavenie MCP 0x23 bolo inicializovane')
    if iobus5 != None:
        iobus5.set_port_direction(0, 0x00)  # GPIOA ako vystupy
        iobus5.set_port_direction(1, 0xFF)  # GPIOB ako vstupy
        iobus5.set_port_pullups(1, 0xFF)    # Pullup rezistory zapnúť na GPIOB
        iobus5.invert_port(1,0xFF)          # Invertovať polaritu na GPIOB
        # logger.info('Nastavenie MCP 0x24 bolo inicializovane')
    if iobus6 != None:
        iobus6.set_port_direction(0, 0x00)  # GPIOA ako vystupy
        iobus6.set_port_direction(1, 0xFF)  # GPIOB ako vstupy
        iobus6.set_port_pullups(1, 0x00)    # Pullup rezistory zapnúť na GPIOB
        iobus6.invert_port(1,0x00)          # Invertovať polaritu na GPIOB
        # logger.info('Nastavenie MCP 0x25 bolo inicializovane')
    if iobus7 != None:
        iobus7.set_port_direction(0, 0x00)  # GPIOA ako vystupy
        iobus7.set_port_direction(1, 0xFF)  # GPIOB ako vstupy
        iobus7.set_port_pullups(1, 0x00)    # Pullup rezistory zapnúť na GPIOB
        iobus7.invert_port(1,0x00)          # Invertovať polaritu na GPIOB
        # logger.info('Nastavenie MCP 0x26 bolo inicializovane')
# prevadza payload na prikaz pre svetlo
def payload_on_off(payload,svetlo):
    """  Prevadza payload na prikaz pre svetlo
    
    Arguments:
        payload {string} -- msg.payload
        svetlo {class} -- instancia triedy svetla
    """
    if str(payload) == "OFF":
        svetlo.command = "OFF"
    if str(payload) == "ON":
        svetlo.command = "ON"
def payload_scena_on(payload,vstup):
    """  Prevadza payload na prikaz pre scenu
    
    Arguments:
        payload {string} -- msg.payload
        vstup {class} -- instancia triedy vstupu sceny
    """
    if str(payload) == "ON":
        vstup.scena = "ON"
# prevadza pyaload na prikaz pre rolety
def payload_up_down(payload,roleta):
    """  Prevadza payload na prikaz pre rolety.
    
    Arguments:
        payload {string} -- msg.payload
        roleta {class} -- instancia triedy rolety
    """
    if str(payload) == "DOWN":
        if roleta.command == "DOWN":
            roleta.command = "STOP"
        else:
            roleta.command = "DOWN"
    if str(payload) == "STOP":
        roleta1.command = "STOP"
    if str(payload) == "UP":
        if roleta.command == "UP":
            roleta.command = "STOP"
        else:
            roleta.command = "UP"
# funkcia zapise do JSON stav rolety
def pub_rolety_out(item="Roleta1",state="STOP"): 
    # Konvert spravy na JSON
    rolety_out[item] = state
    data_out.rolety=json.dumps(rolety_out)# encode oject to JSON
    publikovat.rolety = True
# funkcia zapise do JSON cas rolety
def pub_rolety_time_out(item="Roleta1",state="5.0"): 
    # Konvert spravy na JSON
    rolety_time_out[item] = state
    data_out.rolety_time=json.dumps(rolety_time_out)# encode oject to JSON
    publikovat.rolety_time = True
# funkcia zapise do JSON stav svetla
def pub_svetla_out(item="sv_01",state="OFF"):
    # Konvert spravy na JSON
    logger.info("Public stav svetla " + item + " Stav " + state)
    svetla_out[item] = state
    data_out.svetla=json.dumps(svetla_out)# encode oject to JSON
    publikovat.svetla = True
def pub_tlacidla_out(item="tl_01",state="OPEN"):
    logger.info("Public stav tlacidla " + item + " Stav " + state)
    vstupy_out[item] = state
    data_out.tlacidla = json.dumps(vstupy_out)
    publikovat.tlacidla = True
# Testuje ci su vsteky prikazy v skupine listu urcitej hodnoty
def all_test_command(iterable,value):
    """ Testuje ci su vsteky prikazy v skupine  listu urcitej hodnoty"""
    for element in iterable:
        if not element.command == value :
            return False
    return True
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logger.info("MQTT Broker "+ mqt_broker +" connected with result code "+str(rc))
    client.subscribe(rol_topics) # odoberat vsetky rolety JSON
    client.subscribe(lgt_topics) # odoberat vsetky svetla JSON
    data_out.rolety=json.dumps(rolety_out) # encode oject to JSON
    publikovat.rolety = True # publikovat na konci cyklu
    data_out.rolety_time=json.dumps(rolety_time_out)# encode oject to JSON
    publikovat.rolety_time = True
    data_out.svetla=json.dumps(svetla_out)# encode oject to JSON
    publikovat.svetla = True
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if msg.topic == lgt_all_topic:
        logger.info('MQTT < subscribe vsetky svetla: '+ str(msg.payload))
        payload_on_off(msg.payload,svetla_spol)
        return
    if msg.topic == lgt_scena01_topic:
        logger.info('MQTT < subscribe scena 01: '+ str(msg.payload))
        payload_scena_on(msg.payload,vstup07)
        return
    if msg.topic == lgt_scena02_topic:
        logger.info('MQTT < subscribe scena 02: '+ str(msg.payload))
        payload_scena_on(msg.payload,vstup21)
        return
    if msg.topic == lgt_scena03_topic:
        logger.info('MQTT < subscribe scena 03: '+ str(msg.payload))
        payload_scena_on(msg.payload,vstup25)
        return
    if msg.topic == lgt1_topic:
        logger.info('MQTT < subscribe svetlo 01 '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo01)
        return
    if msg.topic == lgt2_topic:
        logger.info('MQTT < subscribe svetlo 02 '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo02) 
        return
    if msg.topic == lgt3_topic:
        logger.info('MQTT < subscribe svetlo 03 '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo03)
        return
    if msg.topic == lgt4_topic:
        logger.info('MQTT < subscribe svetlo 04 '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo04)
        return
    if msg.topic == lgt5_topic:
        logger.info('MQTT < subscribe svetlo 05 '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo05)
        return
    if msg.topic == lgt6_topic:
        logger.info('MQTT < subscribe svetlo 06 '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo06)
        return
    if msg.topic == lgt7_topic:
        logger.info('MQTT < subscribe svetlo 07 '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo07)
        return
    if msg.topic == lgt8_topic:
        logger.info('MQTT < subscribe svetlo 08 '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo08)
        return
    if msg.topic == lgt9_topic:
        logger.info('MQTT < subscribe svetlo 09 '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo09)
        return
    if msg.topic == lgt10_topic:
        logger.info('MQTT < subscribe svetlo 10: '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo10)
        return
    if msg.topic == lgt11_topic:
        logger.info('MQTT < subscribe svetlo 11: '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo11)
        return
    if msg.topic == lgt12_topic:
        logger.info('MQTT < subscribe svetlo 12: '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo12)
        return
    if msg.topic == lgt13_topic:
        logger.info('MQTT < subscribe svetlo 13: '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo13)
        return
    if msg.topic == lgt14_topic:
        logger.info('MQTT < subscribe svetlo 14: '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo14)
        return
    if msg.topic == lgt15_topic:
        logger.info('MQTT < subscribe svetlo 15: '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo15)
        return
    if msg.topic == lgt16_topic:
        logger.info('MQTT < subscribe svetlo 16: '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo16)
        return
    if msg.topic == lgt17_topic:
        logger.info('MQTT < subscribe svetlo 17: '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo17)
        return
    if msg.topic == lgt18_topic:
        logger.info('MQTT < subscribe svetlo 18: '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo18)
        return
    if msg.topic == lgt19_topic:
        logger.info('MQTT < subscribe svetlo 19: '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo19)
        return
    if msg.topic == lgt20_topic:
        logger.info('MQTT < subscribe svetlo 20: '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo20)
        return
    if msg.topic == lgt21_topic:
        logger.info('MQTT < subscribe svetlo 21: '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo21)
        return
    if msg.topic == lgt22_topic:
        logger.info('MQTT < subscribe svetlo 22: '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo22)
        return
    if msg.topic == lgt23_topic:
        logger.info('MQTT < subscribe svetlo 23: '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo23)
        return
    if msg.topic == lgt24_topic:
        logger.info('MQTT < subscribe svetlo 24: '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo24)
        return
    if msg.topic == lgt25_topic:
        logger.info('MQTT < subscribe svetlo 25: '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo25)
        return
    if msg.topic == lgt26_topic:
        logger.info('MQTT < subscribe svetlo 26: '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo26)
        return
    if msg.topic == lgt27_topic:
        logger.info('MQTT < subscribe svetlo 27: '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo27)
        return
    if msg.topic == lgt28_topic:
        logger.info('MQTT < subscribe svetlo 28: '+ str(msg.payload))
        payload_on_off(msg.payload,svetlo28)
        return 
    if msg.topic == rol_all_topic:
        logger.info('MQTT < subscribe vsetky rolety: '+ str(msg.payload))
        payload_up_down(msg.payload,rolety_spol)
        return
    if msg.topic == rol1_topic:
        logger.info('MQTT < subscribe roleta 1: '+ str(msg.payload))
        payload_up_down(msg.payload,roleta1)
        return
    if msg.topic == rol2_topic:
        logger.info('MQTT < subscribe roleta 2: '+ str(msg.payload))
        payload_up_down(msg.payload,roleta2)
        return
    if msg.topic == rol3_topic:
        logger.info('MQTT < subscribe roleta 3: '+ str(msg.payload))
        payload_up_down(msg.payload,roleta3)
        return
    if msg.topic == rol4_topic:
        logger.info('MQTT < subscribe roleta 4: '+ str(msg.payload))
        payload_up_down(msg.payload,roleta4)
        return
    if msg.topic == rol5_topic:
        logger.info('MQTT < subscribe roleta 5: '+ str(msg.payload))
        payload_up_down(msg.payload,roleta5)
        return
    if msg.topic == rol6_topic:
        logger.info('MQTT < subscribe roleta 6: '+ str(msg.payload))
        payload_up_down(msg.payload,roleta6)
        return
    if msg.topic == rol7_topic:
        logger.info('MQTT < subscribe roleta 7: '+ str(msg.payload))
        payload_up_down(msg.payload,roleta7)
        return
    if msg.topic == rol8_topic:
        logger.info('MQTT < subscribe roleta 8: '+ str(msg.payload))
        payload_up_down(msg.payload,roleta8)
        return
    if msg.topic == rol1_time_topic:
        roleta1.time_rol = float(msg.payload)
        pub_rolety_time_out("Roleta1",roleta1.time_rol)
        logger.info ('MQTT < subscribe nove nastavenie casu rolety 1: ' + str(roleta1.time_rol)+' s')
        config.set('TimesRoll', 'time_rol1', str(roleta1.time_rol))
        config_save()
        return
    if msg.topic == rol2_time_topic:
        roleta2.time_rol = float(msg.payload)
        pub_rolety_time_out("Roleta2",roleta2.time_rol)
        logger.info ('MQTT < subscribe nove nastavenie casu rolety 2: ' + str(roleta2.time_rol)+' s')
        config.set('TimesRoll', 'time_rol2', str(roleta2.time_rol))
        config_save()
        return
    if msg.topic == rol3_time_topic:
        roleta3.time_rol = float(msg.payload)
        pub_rolety_time_out("Roleta3",roleta3.time_rol)
        logger.info ('MQTT < subscribe nove nastavenie casu rolety 3: ' + str(roleta3.time_rol)+' s')
        config.set('TimesRoll', 'time_rol3', str(roleta3.time_rol))
        config_save()
        return
    if msg.topic == rol4_time_topic:
        roleta4.time_rol = float(msg.payload) 
        pub_rolety_time_out("Roleta4",roleta4.time_rol)
        logger.info ('MQTT < subscribe nove nastavenie casu rolety 4: ' + str(roleta4.time_rol)+' s')
        config.set('TimesRoll', 'time_rol4', str(roleta4.time_rol))   
        config_save()
        return
    if msg.topic == rol5_time_topic:
        roleta5.time_rol = float(msg.payload)
        pub_rolety_time_out("Roleta5",roleta5.time_rol)
        logger.info ('MQTT < subscribe nove nastavenie casu rolety 5: ' + str(roleta5.time_rol)+' s')
        config.set('TimesRoll', 'time_rol5', str(roleta5.time_rol))
        config_save()
        return
    if msg.topic == rol6_time_topic:
        roleta6.time_rol = float(msg.payload)
        pub_rolety_time_out("Roleta6",roleta6.time_rol)
        logger.info ('MQTT < subscribe nove nastavenie casu rolety 6: ' + str(roleta6.time_rol)+' s')
        config.set('TimesRoll', 'time_rol6', str(roleta6.time_rol))
        config_save()
        return
    if msg.topic == rol7_time_topic:
        roleta7.time_rol = float(msg.payload)
        pub_rolety_time_out("Roleta7",roleta7.time_rol)
        logger.info ('MQTT < subscribe nove nastavenie casu rolety 7: ' + str(roleta7.time_rol)+' s')
        config.set('TimesRoll', 'time_rol7', str(roleta7.time_rol))
        config_save()
        return
    if msg.topic == rol8_time_topic:
        roleta8.time_rol = float(msg.payload)
        pub_rolety_time_out("Roleta8",roleta8.time_rol)
        logger.info ('MQTT < subscribe nove nastavenie casu rolety 8: ' + str(roleta8.time_rol)+' s')
        config.set('TimesRoll', 'time_rol8', str(roleta8.time_rol))
        config_save()
        return
    if msg.topic == roll_press_rol:
        Impulz = float(msg.payload)
        roleta1.press_rol = Impulz
        roleta2.press_rol = Impulz
        roleta3.press_rol = Impulz
        roleta4.press_rol = Impulz
        roleta5.press_rol = Impulz
        roleta6.press_rol = Impulz
        roleta7.press_rol = Impulz
        roleta8.press_rol = Impulz
        pub_rolety_time_out("Impulz",str(Impulz))
        logger.info ('MQTT < subscribe nove nastavenie dlzka impulzu: ' + msg.payload + ' s')
        config.set('TimesLongPress', 'press_rol', msg.payload)
        config_save()
        return
    return
# Zapsie konfig do suboru
def config_save():
    logger.info("Zapis configu do suboru")
    with open('lights.cfg', 'wb') as configfile:
        config.write(configfile)
        configfile.close()

# create logger
logger = logging.getLogger('Ovladanie svetiel a roliet')
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
# fh = logging.handlers.RotatingFileHandler('debug.log', maxBytes=5000000, backupCount=5)
ch.setLevel(logging.DEBUG)
# fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
# fh.setFormatter(formatter)
logger.addHandler(ch)
# logger.addHandler(fh)
logger.info("***** Start skryptu  *****")

# Pripojenie MCP v druhom vlakne
t2 = threading.Thread(target=connected_mcp_task, args=[])
t2.start()

ports_init() # inicializovat stav vstupov
# instancie svetiel
try:
    g_svetla = [] # skupina svetla
    g_vstupy = [] # skupina vstupy

    
    vstup01 = vstupy(gpiof,7,"tl_01")
    vstup02 = vstupy(gpiof,6,"tl_02")
    vstup03 = vstupy(gpiof,5,"tl_03")
    vstup04 = vstupy(gpiof,4,"tl_04")
    vstup05 = vstupy(gpiof,3,"tl_05")
    vstup06 = vstupy(gpiof,2,"tl_06")
    vstup07 = vstupy(gpiof,1,"tl_07")
    vstup08 = vstupy(gpiof,0,"tl_08")
    vstup09 = vstupy(gpioh,7,"tl_09")
    vstup10 = vstupy(gpioh,6,"tl_10")
    vstup11 = vstupy(gpioh,5,"tl_11")
    vstup12 = vstupy(gpioh,4,"tl_12")
    vstup13 = vstupy(gpioh,3,"tl_13")
    vstup14 = vstupy(gpioh,2,"tl_14")
    vstup15 = vstupy(gpioh,1,"tl_15")
    vstup16 = vstupy(gpioh,0,"tl_16")
    vstup17 = vstupy(gpioj,7,"tl_17")
    vstup18 = vstupy(gpioj,6,"tl_18")
    vstup19 = vstupy(gpioj,5,"tl_19")
    vstup20 = vstupy(gpioj,4,"tl_20")
    vstup21 = vstupy(gpioj,3,"tl_21")
    vstup22 = vstupy(gpioj,2,"tl_22")
    # vstup23 = vstupy(gpioj,1,"tl_23")   # vstupy sa pouzivaju sa na centalne ovladanie roliet
    # vstup24 = vstupy(gpioj,0,"tl_24")   # vstupy sa pouzivaju sa na centalne ovladanie roliet
    vstup25 = vstupy(gpiol,7,"tl_25")
    vstup26 = vstupy(gpiol,6,"tl_26")
    vstup27 = vstupy(gpiol,5,"tl_27")
    vstup28 = vstupy(gpiol,4,"tl_28")
    vstup29 = vstupy(gpiol,3,"tl_29")
    vstup30 = vstupy(gpiol,2,"tl_30")
    vstup31 = vstupy(gpiol,1,"tl_31")
    vstup32 = vstupy(gpiol,0,"tl_32")
    vstup33 = vstupy(gpion,7,"tl_33")
    vstup34 = vstupy(gpion,6,"tl_34")
    vstup35 = vstupy(gpion,5,"tl_35")
    vstup36 = vstupy(gpion,4,"tl_36")
    vstup37 = vstupy(gpion,3,"tl_37")
    vstup38 = vstupy(gpion,2,"tl_38")
    vstup39 = vstupy(gpion,1,"tl_39")
    vstup40 = vstupy(gpion,0,"tl_40")

    g_vstupy = [vstup01,vstup02,vstup03,vstup04,vstup05,vstup06,vstup07,vstup08]
    g_vstupy = g_vstupy + [vstup09,vstup10,vstup11,vstup12,vstup13,vstup14,vstup15,vstup16]
    g_vstupy = g_vstupy + [vstup17,vstup18,vstup19,vstup20,vstup21,vstup22]
    g_vstupy = g_vstupy + [vstup25,vstup26,vstup27,vstup28,vstup29,vstup30,vstup31,vstup32]
    g_vstupy = g_vstupy + [vstup33,vstup34,vstup35,vstup36,vstup37,vstup38,vstup39,vstup40]

    svetlo01 = vystupy(vstup01,gpioe,0,"sv_01")
    svetlo02 = vystupy(vstup02,gpioe,1,"sv_02")
    svetlo03 = vystupy(vstup03,gpioe,2,"sv_03")
    svetlo04 = vystupy(vstup04,gpioe,3,"sv_04")
    svetlo05 = vystupy(vstup05,gpioe,4,"sv_05")
    svetlo06 = vystupy(vstup06,gpioe,5,"sv_06")
    svetlo07 = vystupy(vstup07,gpioe,6,"sv_07")
    svetlo08 = vystupy(vstup08,gpioe,7,"sv_08")
    svetlo09 = vystupy(vstup09,gpiog,0,"sv_09")
    svetlo10 = vystupy(vstup10,gpiog,1,"sv_10")
    svetlo11 = vystupy(vstup11,gpiog,2,"sv_11")
    svetlo12 = vystupy(vstup12,gpiog,3,"sv_12")
    svetlo13 = vystupy(vstup13,gpiog,4,"sv_13")
    svetlo14 = vystupy(vstup14,gpiog,5,"sv_14")
    svetlo15 = vystupy(vstup15,gpiog,6,"sv_15")
    svetlo16 = vystupy(vstup16,gpiog,7,"sv_16")
    svetlo17 = vystupy(vstup17,gpioi,0,"sv_17")
    svetlo18 = vystupy(vstup18,gpioi,1,"sv_18")
    svetlo19 = vystupy(vstup19,gpioi,2,"sv_19")
    svetlo20 = vystupy(vstup20,gpioi,3,"sv_20")
    svetlo21 = vystupy(vstup21,gpioi,4,"sv_21")
    svetlo22 = vystupy(vstup22,gpioi,5,"sv_22")
    # svetlo23 = vystupy(vstup23,gpioi,6,"sv_23") # rezerva
    # svetlo24 = vystupy(vstup24,gpioi,7,"sv_24") # rezerva
    svetlo25 = vystupy(vstup25,gpiok,0,"sv_25")
    svetlo26 = vystupy(vstup26,gpiok,1,"sv_26")
    svetlo27 = vystupy(vstup27,gpiok,2,"sv_27")
    svetlo28 = vystupy(vstup28,gpiok,3,"sv_28")
    svetlo29 = vystupy(vstup29,gpiok,4,"sv_29")
    svetlo30 = vystupy(vstup30,gpiok,5,"sv_30")
    svetlo31 = vystupy(vstup31,gpiok,6,"sv_31")
    svetlo32 = vystupy(vstup32,gpiok,7,"sv_32")
    svetlo33 = vystupy(vstup33,gpiom,0,"sv_33")
    svetlo34 = vystupy(vstup34,gpiom,1,"sv_34")
    svetlo35 = vystupy(vstup35,gpiom,2,"sv_35")
    svetlo36 = vystupy(vstup36,gpiom,3,"sv_36")
    svetlo37 = vystupy(vstup37,gpiom,4,"sv_37")
    svetlo38 = vystupy(vstup38,gpiom,5,"sv_38")
    svetlo39 = vystupy(vstup39,gpiom,6,"sv_39")
    svetlo40 = vystupy(vstup40,gpiom,7,"sv_40")

    g_svetla = [svetlo01,svetlo02,svetlo03,svetlo04,svetlo05,svetlo06,svetlo07,svetlo08]
    g_svetla = g_svetla + [svetlo09,svetlo10,svetlo11,svetlo12,svetlo13,svetlo14,svetlo15,svetlo16]
    g_svetla = g_svetla + [svetlo17,svetlo18,svetlo19,svetlo20,svetlo21,svetlo22]
    g_svetla = g_svetla + [svetlo25,svetlo26,svetlo27,svetlo28,svetlo29,svetlo30,svetlo31,svetlo32]
    g_svetla = g_svetla + [svetlo33,svetlo34,svetlo35,svetlo36,svetlo37,svetlo38,svetlo39,svetlo40]

    scena1 = [svetlo03,svetlo06,svetlo11] # scéna svetiel
    skupina1 = skupiny_svetiel(vstup07,scena1,"Obyvacka kupelna LED") # Konfiguracia scény
    scena2 = [svetlo17, svetlo22, svetlo26]
    skupina2 = skupiny_svetiel(vstup21,scena2,"Vonkajsok")
    # scena3 = [svetlo25,svetlo26]
    # skupina3 = skupiny_svetiel(vstup25,scena3,"Test")

    svetla_spol = svetla_spolocne(dummy,0) # svetla nemaju hardvarovy spinac
    
except:
    pass
# instancie roliet
try:
    g_rolety = []
    rolety_spol = rolety_spolocne(gpioj,zall,oall)
    roleta1 = rolety(gpiob,gpioa,z1,o1,r_on1,r_za1,"Roleta1") # Kuchyna
    g_rolety = g_rolety + [roleta1]
    roleta2 = rolety(gpiob,gpioa,z2,o2,r_on2,r_za2,"Roleta2") # Jedáleň
    g_rolety = g_rolety + [roleta2]
    roleta3 = rolety(gpiob,gpioa,z3,o3,r_on3,r_za3,"Roleta3") # Obývačka
    g_rolety = g_rolety + [roleta3]
    roleta4 = rolety(gpiob,gpioa,z4,o4,r_on4,r_za4,"Roleta4") # WC
    g_rolety = g_rolety + [roleta4]
    roleta5 = rolety(gpiod,gpioc,z6,o6,r_on5,r_za5,"Roleta5") # Kúpeľňa
    g_rolety = g_rolety + [roleta5]
    roleta6 = rolety(gpiod,gpioc,z7,o7,r_on6,r_za6,"Roleta6") # Spálňa
    g_rolety = g_rolety + [roleta6]
    roleta7 = rolety(gpiod,gpioc,z5,o5,r_on8,r_za8,"Roleta7") # Detská izba
    g_rolety = g_rolety + [roleta7]
    roleta8 = rolety(gpiod,gpioc,z8,o8,r_on7,r_za7,"Roleta8") # Izba
    g_rolety = g_rolety + [roleta8]
except:
    pass
# Nacitanie configu
try:
    logger.debug ('Konfiguracny subor lights.cfg start citania')
    config = ConfigParser.SafeConfigParser()
    config.read('lights.cfg')

    roleta1.time_rol = float(config.get('TimesRoll', 'time_rol1'))
    roleta2.time_rol = float(config.get('TimesRoll', 'time_rol2'))
    roleta3.time_rol = float(config.get('TimesRoll', 'time_rol3'))
    roleta4.time_rol = float(config.get('TimesRoll', 'time_rol4'))
    roleta5.time_rol = float(config.get('TimesRoll', 'time_rol5'))
    roleta6.time_rol = float(config.get('TimesRoll', 'time_rol6'))
    roleta7.time_rol = float(config.get('TimesRoll', 'time_rol7'))
    roleta8.time_rol = float(config.get('TimesRoll', 'time_rol8'))
    pub_rolety_time_out("Roleta1",str(roleta1.time_rol))
    pub_rolety_time_out("Roleta2",str(roleta2.time_rol))
    pub_rolety_time_out("Roleta3",str(roleta3.time_rol))
    pub_rolety_time_out("Roleta4",str(roleta4.time_rol))
    pub_rolety_time_out("Roleta5",str(roleta5.time_rol))
    pub_rolety_time_out("Roleta6",str(roleta6.time_rol))
    pub_rolety_time_out("Roleta7",str(roleta7.time_rol))
    pub_rolety_time_out("Roleta8",str(roleta8.time_rol))
    list_roll_time = [roleta1.time_rol,roleta2.time_rol,roleta3.time_rol,roleta4.time_rol,roleta5.time_rol,roleta6.time_rol,roleta7.time_rol,roleta8.time_rol]
    for item in list_roll_time:
        logger.info (item)

    Impulz = float(config.get('TimesLongPress', 'press_rol'))
    roleta1.press_rol = Impulz
    roleta2.press_rol = Impulz
    roleta3.press_rol = Impulz
    roleta4.press_rol = Impulz
    roleta5.press_rol = Impulz
    roleta6.press_rol = Impulz
    roleta7.press_rol = Impulz
    roleta8.press_rol = Impulz
    pub_rolety_time_out("Impulz",str(Impulz))
    list_pres_rol = [roleta1.press_rol,roleta2.press_rol,roleta3.press_rol,roleta4.press_rol,roleta5.press_rol,roleta6.press_rol,roleta7.press_rol,roleta8.press_rol]
    for item in list_pres_rol:
        logger.info(item)

    logger.debug ('Konfiguracny subor lights.cfg nacitany')
except:
    logger.error ('Konfiguracny subor lights.cfg nebol nacitany')
# Príprava tried pre publikovanie MQTT
data_out.rolety = ""
data_out.rolety_time = ""
data_out.svetla = ""
publikovat.rolety = False
publikovat.rolety_time = False
publikovat.svetla = False
publikovat.tlacidla = False

# instancia MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
t1 = threading.Thread(target=connect_task, args=[])
t1.start()

def main():
    pass
# main
if __name__ == "__main__":
    main()
    """
    Main program function
    """
    logger.info('*****  Spustenie logiky  *****')
    reconnect = False
    pocet_cyklov = 0 # pomocna premnná pre reinit mcpečiek
    cas = 0

    while True:
        try:
            # cas = time.clock()
            if reconnect == True:
                mcp_init_setup()
                reconnect = False
                pocet_cyklov = 0
                print ("MCPecka boli reinicializovane")
            else:
                if pocet_cyklov >= 40:
                    mcp_init_setup()
                    pocet_cyklov = 0
                else: 
                    pocet_cyklov += 1
            # Nacitanie stavu vstupneho portu GPIO 
            if iobus1 != None:
                gpiob.port = iobus1.read_port(1)
            if iobus2 != None:
                gpiod.port = iobus2.read_port(1)
            if iobus3 != None:
                gpiof.port = iobus3.read_port(1)
            if iobus4 != None:
                gpioh.port = iobus4.read_port(1)
            if iobus5 != None:
                gpioj.port = iobus5.read_port(1)
            if iobus6 != None:
                gpiol.port = iobus6.read_port(1)
            if iobus7 != None:
                gpion.port = iobus7.read_port(1)
            # Riadenie svetiel a roliet  
            svetla_spol.commands_make()
            svetla_spol.light_control()
            
            for itme_l in g_vstupy:   # Spracovanie vstupov
                itme_l.commands_make()
            
            skupina1.scene()          # Riadenie sceny
            skupina2.scene()
            # skupina3.scene()

            for item_l in g_svetla:   # Riadenie vsetkych svetiel v skupine g_svetla
                item_l.control()
            
            for itme_l in g_vstupy:   # Po spracovaní scén príkaz na NA
                itme_l.scena = "NA"
           

        
            rolety_spol.commands_make()
            rolety_spol.roller_control()
            for item_r in g_rolety:   # Riadenie vsetky roliet v skupine g_rolety
                item_r.commands_make()
                item_r.roller_control()
            
            if publikovat.rolety == True:
                # logger.info ("MQTT > data out rolety=" + data_out.rolety)
                client.publish(rol_out_topic,data_out.rolety,0,True)
                publikovat.rolety = False
            if publikovat.rolety_time == True:
                # logger.info ("MQTT > data out rolety time=" + data_out.rolety_time)
                client.publish(rol_time_out_topic,data_out.rolety_time,0,True)
                publikovat.rolety_time = False
            if publikovat.svetla == True:
                # logger.info ("MQTT > data out svetla =" + data_out.svetla)
                client.publish(lgt_out_topic,data_out.svetla,0,True)
                publikovat.svetla = False
            if publikovat.tlacidla == True:
                # logger.info ("MQTT > data out tlacidla =" + data_out.tlacidla)
                client.publish(tl_out_topic,data_out.tlacidla,0,True)
                publikovat.tlacidla = False
            # Zapis vystupov do MCP
            if iobus1 != None:
                iobus1.write_port(0,gpioa.port) 
            if iobus2 != None:
                iobus2.write_port(0,gpioc.port) 
            if iobus3 != None:
                iobus3.write_port(0,gpioe.port) 
            if iobus4 != None:
                iobus4.write_port(0,gpiog.port) 
            if iobus5 != None:
                iobus5.write_port(0,gpioi.port) 
            if iobus6 != None:
                iobus6.write_port(0,gpiok.port)
            if iobus7 != None:
                iobus7.write_port(0,gpiom.port)
            # wait 0.05 seconds before reading the pins again
            # cas_cyklu = time.clock() - cas
            # logger.info("Cas vykonania programu"+ str(cas_cyklu))
            time.sleep(0.05)
        except IOError as e:
            timetoreconnetc = 2
            logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
            logger.error('IOError reconnect after '+ str(timetoreconnetc) +' seconds')
            time.sleep(timetoreconnetc)
            reconnect = True
