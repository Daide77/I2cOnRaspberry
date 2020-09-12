import smbus
import time
from   datetime import datetime
import ctypes
import json
import paho.mqtt.client as mqtt
import sys, getopt
c_uint8             = ctypes.c_uint8

# User Section
DEFAULT_CONFIG_FILE = '/home/pi/python/mycfng.json' 
# To find the I2C adapter address
# sudo i2cdetect -y 1

class GeneralStruct:
        pass

# Basic Function
def StringToList( sep, string, purpose="logLevel" ):
   log("INFO","preparing new list for "+purpose)
   try:
      newList = string.split( sep )
   except:
      log("WARN", ("No new list, keeping old list ",GS.LOG_LEVEL) )
      newList = []
      return GS.LOG_LEVEL
   if len(newList) > 0:
      log("INFO", ("new list is",newList) )
      return newList
   else:
      log("INFO", ("keeping old list ",GS.LOG_LEVEL) )
      return GS.LOG_LEVEL

def fileExists(filename):
    try:
        os.stat(filename)
        return True;
    except OSError:
        return False

def log( Level, msg ):
        if Level in GS.LOG_LEVEL:
            now = datetime.now()
            print( "{} Level: {} Msg: {} ".format( now.strftime("%Y/%m/%d, %H:%M:%S:%f"), str(Level), str(msg)) )

def LoadConfig( GS ):
   with open( GS.ConfigFile ) as data_file:
      # data            = json.load( str(data_file.readlines()).strip() )
      log( "INFO", "Loading conf from file: ["+GS.ConfigFile+"]" )
      GS.data           = json.load( data_file )
      GS.CLIENTID       = GS.data["MQTTclientid"]
      GS.USER           = GS.data["MQTTuserid"]
      GS.PSWD           = GS.data["MQTTpasswd"]
      GS.SERVER         = GS.data["MQTTserver"]
      GS.statusMsg      = { "status":"ONLINE" }
      GS.SMBus          = GS.data["SMBus"]        
      GS.I2cAddresses   = GS.data["I2cAddresses"]    
      GS.IN_CMD_TOPIC   = GS.data["MQTT_IN_CMD_TOPIC"]
      GS.OUT_STATUS     = GS.data["MQTT_OUT_STATUS"]
      GS.LOG_LEVEL      = StringToList( ',', str( GS.data["LOG_LEVEL"] ) )

def sub_cb( client, userdata, msg ):
    log( 'INFO', "Called sub_cb:" )
    log( 'INFO', ( msg.topic, msg.payload.decode("utf-8") ) )
    if msg.topic == GS.IN_CMD_TOPIC:
       # MsddgIn example : '{ "COMMAND": "REBOOT" }'
       try:
          cmd = json.loads( msg.payload.decode("ut8-8") )
       except:
          cmd = {}
       if type( cmd ) is not dict:
          log( "WARN", "wrong command format! " + str( msg ))
          cmd = {}
       for k in cmd :
          if k == 'COMMAND' and cmd[k] == 'REBOOT':
               log( "INFO", "Command is to reboot!" )
       # TODO pensare a comandi tipo free, top, df, who -b per investigare lo stato le raspy        
       # GS.c.publish( GS.OUT_STATUS, msg=json.dumps(GS.statusMsg), retain=True, qos=1 )

def MqttSetUP( GS ):
   GS.c            = mqtt.Client()
   GS.c.username_pw_set( GS.USER, GS.PSWD )
   GS.c.on_message = sub_cb
   GS.c.will_set( GS.OUT_STATUS, payload=b'{"status": "OFFLINE"}', qos=1, retain=True)
   try:
      log( "INFO", "Connecting to MQTT server...." )
      GS.c.connect( GS.SERVER )
   except Exception as e:
      log( "ERROR", "Error MqttConnection {}".format(e) )
   log( "INFO", "OK! Connected to MQTT server" )
   GS.c.subscribe( GS.IN_CMD_TOPIC )
   GS.c.loop_start()
   GS.c.publish( GS.OUT_STATUS, payload=b'{"status": "ONLINE"}',qos=1, retain=True )

# Gestione bitfield 
class Flags_bits(ctypes.LittleEndianStructure):
   _fields_ = [
               ("Pin0", c_uint8, 1) ,
               ("Pin1", c_uint8, 1) ,
               ("Pin2", c_uint8, 1) ,
               ("Pin3", c_uint8, 1) ,
               ("Pin4", c_uint8, 1) ,
               ("Pin5", c_uint8, 1) ,
               ("Pin6", c_uint8, 1) ,
               ("Pin7", c_uint8, 1) ,
              ]

class Flags(ctypes.Union):
   _fields_ = [ 
                ("b"     , Flags_bits) ,
                ("asbyte", c_uint8   )
              ]

def write(ad,value):
   bus.write_byte_data(ad, 0, value)
   return -1

def range(ad):
   range0 = bus.read_byte(ad)
   return range0

def GetArguments( argv, defaultValue ):
   ConfigFile = defaultValue
   try:
       opts, args = getopt.getopt( argv, "c:",["config="])
   except:
       log( "WARN","No config file! continue with default file {} ".format( ConfigFile ) )
       return ConfigFile
   for opt, arg in opts:
       if opt == '-c':
          ConfigFile = arg
   return ConfigFile
   
if __name__ == "__main__":
   GS                = GeneralStruct()
   GS.LOG_LEVEL      = [ "DEBUG", "INFO", "WARN", "ERROR" ]
   GS.ConfigFile     = GetArguments( sys.argv[1:], DEFAULT_CONFIG_FILE )
   LoadConfig( GS )
   bus               = smbus.SMBus(GS.SMBus)
   addresses         = GS.I2cAddresses
   MqttSetUP( GS )
   
   GS.i2cDevStatus   = {}
   
   for address in addresses:                           # keeping track of each device pin status
      GS.i2cDevStatus[str(address)]          = {}
      GS.i2cDevStatus[str(address)]["Value"] = 666     # Impossible value to force push the first time
   
   flags                                     = Flags() # Easy way to manage a bitfield
   while True:
      for address in addresses: 
         write( address, 0x00 )
         time.sleep(0.7)
         rng                 = range(address)
         flags.asbyte        = rng
         log( "DEBUG", "New Reading Device: [ {} ] Byte Value: [ {} ]".format( address, flags.asbyte )  )
         GS.statusMsg["I2C"] = {}
         # TODO add lastupdate
         for f in flags.b._fields_:
             name                      = "Dev{}{}".format( address,f[0] )
             value                     = getattr( flags.b, f[0] ) 
             GS.statusMsg["I2C"][name] = value
         # you can always access manually to each pin    
         # log( "DEBUG", ( "port 0 "+ str( flags.b.port0 ) ) ) 
         if GS.i2cDevStatus[str(address)]["Value"] != flags.asbyte: # Pubblish only if it's needed
            log( "INFO", "----- Status Cahnged reading Device: [ {} ] Byte Value: [ {} ] -------".format( address, flags.asbyte ) )
            GS.c.publish( GS.OUT_STATUS, payload=json.dumps( GS.statusMsg ),qos=1, retain=True )
            GS.i2cDevStatus[str(address)]["Value"] = flags.asbyte
         log( "DEBUG", "----- END -------" )
