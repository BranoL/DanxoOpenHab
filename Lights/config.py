"""
Nastavenie konstant
"""
# MQTT nastavenia
mqtt_username = "openhab"
mqtt_password = "1234"
client_id = "1111"
mqt_broker = "127.0.0.1"
# mqt_broker = "192.168.1.2"

# Subscribe povel pre rolety
rol_out_topic = "home/rol/out" # Publish stav roliet do JSON
rol_topics = "home/rol/#" # Subscribe povely pre riadenie roleit
rol1_topic = "home/rol/rol_1"
rol2_topic = "home/rol/rol_2"
rol3_topic = "home/rol/rol_3"
rol4_topic = "home/rol/rol_4"
rol5_topic = "home/rol/rol_5"
rol6_topic = "home/rol/rol_6"
rol7_topic = "home/rol/rol_7"
rol8_topic = "home/rol/rol_8"
rol_all_topic = "home/rol/all"
# Subscribe nastavenych casov
rol_time_out_topic = "home/rol/time_out" # Publish hodnota casov JSON
roll_press_rol =  "home/rol/press_rol"  # Subscribe hodnoty casov
rol1_time_topic = "home/rol/rol_1_time"
rol2_time_topic = "home/rol/rol_2_time"
rol3_time_topic = "home/rol/rol_3_time"
rol4_time_topic = "home/rol/rol_4_time"
rol5_time_topic = "home/rol/rol_5_time"
rol6_time_topic = "home/rol/rol_6_time"
rol7_time_topic = "home/rol/rol_7_time"
rol8_time_topic = "home/rol/rol_8_time"
# Subscribe = povel pre svetla
lgt_out_topic = "home/lights/out"  # publish stav svetiel
lgt_topics = "home/lights/#"    # Subscribe povely pre riadenie svetiel
lgt1_topic = "home/lights/light_1"
lgt2_topic = "home/lights/light_2"
lgt3_topic = "home/lights/light_3"
lgt4_topic = "home/lights/light_4"
lgt5_topic = "home/lights/light_5"
lgt6_topic = "home/lights/light_6"
lgt7_topic = "home/lights/light_7"
lgt8_topic = "home/lights/light_8"
lgt9_topic = "home/lights/light_9"
lgt10_topic = "home/lights/light_10"
lgt11_topic = "home/lights/light_11"
lgt12_topic = "home/lights/light_12"
lgt13_topic = "home/lights/light_13"
lgt14_topic = "home/lights/light_14"
lgt15_topic = "home/lights/light_15"
lgt16_topic = "home/lights/light_16"
lgt17_topic = "home/lights/light_17"
lgt18_topic = "home/lights/light_18"
lgt19_topic = "home/lights/light_19"
lgt20_topic = "home/lights/light_20"
lgt21_topic = "home/lights/light_21"
lgt22_topic = "home/lights/light_22"
lgt23_topic = "home/lights/light_23"
lgt24_topic = "home/lights/light_24"
lgt25_topic = "home/lights/light_25"
lgt26_topic = "home/lights/light_26"
lgt27_topic = "home/lights/light_27"
lgt28_topic = "home/lights/light_28"
lgt29_topic = "home/lights/light_29"
lgt30_topic = "home/lights/light_30"
lgt31_topic = "home/lights/light_31"
lgt32_topic = "home/lights/light_32"
lgt33_topic = "home/lights/light_33"
lgt34_topic = "home/lights/light_34"
lgt35_topic = "home/lights/light_35"
lgt36_topic = "home/lights/light_36"
lgt37_topic = "home/lights/light_37"
lgt38_topic = "home/lights/light_38"
lgt39_topic = "home/lights/light_39"
lgt40_topic = "home/lights/light_40"

lgt_all_topic = "home/lights/all"
lgt_scena01_topic = "home/lights/scena_01"
lgt_scena02_topic = "home/lights/scena_02"
lgt_scena03_topic = "home/lights/scena_03"
# Tlacidla
tl_out_topic = "home/btns/out" # publish stav tlacidiel
# Vstupy
o1 = 6
z1 = 7
o2 = 4
z2 = 5
o3 = 2
z3 = 3
o4 = 0
z4 = 1
o5 = 6
z5 = 7
o6 = 4
z6 = 5
o7 = 3
z7 = 2
o8 = 1
z8 = 0
oall = 1
zall = 0

# Vystupy
r_on1 = 0  
r_za1 = 1
r_on2 = 2 
r_za2 = 3
r_on3 = 4 
r_za3 = 5
r_on4 = 6 
r_za4 = 7
r_on5 = 0 
r_za5 = 1
r_on6 = 2 
r_za6 = 3
r_on7 = 4 
r_za7 = 5
r_on8 = 6 
r_za8 = 7

# JSON
rolety_out = {"Roleta1":"STOP",
            "Roleta2":"STOP",
            "Roleta3":"STOP",
            "Roleta4":"STOP",
            "Roleta5":"STOP",
            "Roleta6":"STOP",
            "Roleta7":"STOP",
            "Roleta8":"STOP",
            "All":"STOP"
            }
rolety_time_out = {"Roleta1":"5.0",
            "Roleta2":"5.0",
            "Roleta3":"5.0",
            "Roleta4":"5.0",
            "Roleta5":"5.0",
            "Roleta6":"5.0",
            "Roleta7":"5.0",
            "Roleta8":"5.0",
            "Impulz":"1.5"
            }
svetla_out =  {"sv_01":"OFF",
            "sv_02":"OFF",
            "sv_03":"OFF",
            "sv_04":"OFF",
            "sv_05":"OFF",
            "sv_06":"OFF",
            "sv_07":"OFF",
            "sv_08":"OFF",
            "sv_09":"OFF",
            "sv_10":"OFF",
            "sv_11":"OFF",
            "sv_12":"OFF",
            "sv_13":"OFF",
            "sv_14":"OFF",
            "sv_15":"OFF",
            "sv_16":"OFF",
            "sv_17":"OFF",
            "sv_18":"OFF",
            "sv_19":"OFF",
            "sv_20":"OFF",
            "sv_21":"OFF",
            "sv_22":"OFF",
            "sv_23":"OFF",
            "sv_24":"OFF",
            "sv_25":"OFF",
            "sv_26":"OFF",
            "sv_27":"OFF",
            "sv_28":"OFF",
            "sv_29":"OFF",
            "sv_30":"OFF",
            "sv_31":"OFF",
            "sv_32":"OFF",
            "sv_33":"OFF",
            "sv_34":"OFF",
            "sv_35":"OFF",
            "sv_36":"OFF",
            "sv_37":"OFF",
            "sv_38":"OFF",
            "sv_39":"OFF",
            "sv_40":"OFF",
            "All":"OFF"
            }
vstupy_out = {"tl_01":"OPEN",
            "tl_02":"OPEN",
            "tl_03":"OPEN",
            "tl_04":"OPEN",
            "tl_05":"OPEN",
            "tl_06":"OPEN",
            "tl_07":"OPEN",
            "tl_08":"OPEN",
            "tl_09":"OPEN",
            "tl_10":"OPEN",
            "tl_11":"OPEN",
            "tl_12":"OPEN",
            "tl_13":"OPEN",
            "tl_14":"OPEN",
            "tl_15":"OPEN",
            "tl_16":"OPEN",
            "tl_17":"OPEN",
            "tl_18":"OPEN",
            "tl_19":"OPEN",
            "tl_20":"OPEN",
            "tl_21":"OPEN",
            "tl_22":"OPEN",
            "tl_23":"OPEN",
            "tl_24":"OPEN",
            "tl_25":"OPEN",
            "tl_26":"OPEN",
            "tl_27":"OPEN",
            "tl_28":"OPEN",
            "tl_29":"OPEN",
            "tl_30":"OPEN",
            "tl_31":"OPEN",
            "tl_32":"OPEN",
            "tl_33":"OPEN",
            "tl_34":"OPEN",
            "tl_35":"OPEN",
            "tl_36":"OPEN",
            "tl_37":"OPEN",
            "tl_38":"OPEN",
            "tl_39":"OPEN",
            "tl_40":"OPEN"
            }
