I had a spare old Raspberry ( Raspberry Pi Model B Rev 1 )

and with a couple of cheap "PCF8574 PCF8574T Module IO Extension"

I wanted to check on the status of 16 contats for a project of mine.

How to eneable the I2C:

https://raspberry-projects.com/pi/pi-operating-systems/raspbian/io-pins-raspbian/i2c-pins

here you can find more information:

https://raspberry-projects.com/pi/programming-in-python/i2c-programming-in-python/using-the-i2c-interface-2

The python program checks each pin on each PCF8574 and if it founds a change on the pin status
it writes the whole json structure on a MQTT topic.
The program has a configuration file.

The nodejs program is unfinisched and abbandoned because on my old raspberry with ARMV6 processor nodejs is very old and slow
python3 performs far better, maybe one day with a newer raspberry I'll finish it or I'll try a different version of nodejs.

