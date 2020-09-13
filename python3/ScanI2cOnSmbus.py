import smbus
import sys

def Scan( bus ):
   print( "\n" ) 
   print( "Trying to search on... [{}] ".format( bus ) )  
   try:
      return smbus.SMBus(int(bus)) 
   except Exception as e: 
      print( "\n" ) 
      print( "Darn! Something went Wrong with your I2c device\n   {}".format( e ) )
      print( "   Try to call me with another lucky number dude!" )
      print( "\n" ) 
      sys.exit(255)

bus = Scan( (sys.argv[1] if len(sys.argv) == 2 else 0) ) 

for device in range(128):
   try:
      bus.read_byte( device )
      print( "Found one! decimal_value: {}  hex_value: {} ".format( device, hex(device) ) )
   except: 
      pass
print( "\n" ) 
