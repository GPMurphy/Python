#!/usr/bin/python

#http://blog.thehumangeo.com/2015/01/07/string-tokenization/
#https://stackabuse.com/read-a-file-line-by-line-in-python/

import datetime
from datetime import timedelta
import time
from time import sleep             # lets us have a delay 
import sys
import re


print(sys.version)

filepath1 = r"D:\plastic\FWM ST\tools\Python\Saleae logs\\"
filename1 = r"gauge page"
fileext1 = r".csv"
fileext2 = r".txt"
fileext3 = r".txt1"

CurrentDateTime = datetime.datetime.now()

print (CurrentDateTime.strftime("Date : %m/%d/%y"))
print (CurrentDateTime.strftime("Time : %H:%M:%S"))

print (CurrentDateTime)


#print (tokens)
# baud rates less than 19200 use this calculation: ( ( ( ( timer counts per second * 3.5 character times ) * bits per char ) / baud rate ) )
# 10 bits per char start, 8 data, stop
# baud rates above 19200 use 1.75ms inter-frame delay, this is the Modbus specification
# Redlion is using less than the Modbus spec at 115200, looks like they only know about the 3.5 character time
chartimefor9600 = float((1/9600)*10)
chartimefor19200 = float(0.00175) 
chartimefor115200 = float(((1/115200)*10)*3.5) 
endofpackettime = float( chartimefor115200 )
print ("time used to determine end of packet = ", "{:.6f}".format(endofpackettime))
print("The + symbol is used to make searching for the beginning of the line easier.")

packetprintenable = 0   # 0 = off, 1 = on
valuelastchar = 0
valuestartpkt = 0
value1 = 0
value_byte_count = 0
string1 = ""
string2 = ""
string_address = ""
string_bytes = ""
array_pkt = []

MVT485fileoutput = open(filepath1 + filename1 + fileext2,"w")
MVT485fileparsedoutput = open(filepath1 + filename1 + fileext3,"w")

with open(filepath1 + filename1 + fileext1) as MVT485file:

	for cnt, line in enumerate(MVT485file):
		
		if cnt > 0:  #skip first line that has text
			tokens = line.split(",")
			string2 = str(tokens[2])
			string1 = ( string2[0] + string2[1] + string2[2] + string2[3] + ", " )
			string4 = ( string2[2] + string2[3] )
			string3 = ( string2[2] + string2[3] )
			value1 = float(tokens[0])
			array_pkt.append( string3 )
			
			# print(tokens)
			# print( "here " )
			# print( cnt )
			# print( array_pkt )

			# print(string3)
			# print("{:.0f}".format(int(string3, 16)))
			# print(value1)
			
			value_byte_count += 1
			if value_byte_count == 2:
				string_address = (string2[0] + string2[1] + string2[2] + string2[3])
			if value_byte_count == 3:
				string_address = string_address + (string2[2] + string2[3])
			
			
			# need to subtract one char time because Saleae records the time at the beginning of the char
			timebetweenchars = ( value1 - valuelastchar - chartimefor115200 )
			
			if timebetweenchars > endofpackettime:
				
				if value_byte_count <= 6:
					MVT485fileparsedoutput.write( "\n" + str( array_pkt[0:value_byte_count] ) )
					
					string2 = "\nstart time " + "{:.6f}".format(valuestartpkt)
					MVT485fileparsedoutput.write(string2)
					MVT485fileparsedoutput.write(" bad packet not enough bytes" )
							
				else:
					functioncode = int(array_pkt[1], 16)
					
					if functioncode == 3 or functioncode == 4:
					
						if value_byte_count == 8:
							if packetprintenable == 1:
								MVT485fileparsedoutput.write( "\n" + str( array_pkt[0:value_byte_count] ) )
							
							string2 = "\nstart time " + "{:.6f}".format(valuestartpkt)
							MVT485fileparsedoutput.write(string2)
							MVT485fileparsedoutput.write(" query: node add = " + str( array_pkt[0:1] ) )
							MVT485fileparsedoutput.write(" function code = " + str( array_pkt[1:2] ) )					
							address = ( int(array_pkt[2], 16) * 256 ) + ( int(array_pkt[3], 16) )
							if functioncode == 3:
								address += 400001
							else:   # fucntion code 4
								address += 300001
							MVT485fileparsedoutput.write(" start add = " + "{:.0f}".format( int( address ) ) )
							numberofregisters = ( int(array_pkt[4], 16) * 256 ) + ( int(array_pkt[5], 16) )
							MVT485fileparsedoutput.write(" # reg = " + "{:.0f}".format( int( numberofregisters ) ) )				
							crcvalue = ( int(array_pkt[6], 16) * 256 ) + ( int(array_pkt[7], 16) )
							MVT485fileparsedoutput.write(" CRC = " + "{:.0f}".format( int( crcvalue ) ) )

						elif value_byte_count % 2 == 1:
							if packetprintenable == 1:
								MVT485fileparsedoutput.write( "\n" + str( array_pkt[0:value_byte_count] ) )
							
							string2 = "\nstart time " + "{:.6f}".format(valuestartpkt)
							MVT485fileparsedoutput.write(string2)
							MVT485fileparsedoutput.write(" response: node add = " + str( array_pkt[0:1] ) )
							MVT485fileparsedoutput.write(" function code = " + str( array_pkt[1:2] ) )					
							numberofbytes = ( int(array_pkt[2], 16) )
							MVT485fileparsedoutput.write(" number of bytes = " + "{:.0f}".format( int( numberofbytes ) ) )
							
					elif functioncode == 6:
					
						if value_byte_count == 8:
							if packetprintenable == 1:
								MVT485fileparsedoutput.write( "\n" + str( array_pkt[0:value_byte_count] ) )
							
							string2 = "\nstart time " + "{:.6f}".format(valuestartpkt)
							MVT485fileparsedoutput.write(string2)
							MVT485fileparsedoutput.write(" query/response: node add = " + str( array_pkt[0:1] ) )
							MVT485fileparsedoutput.write(" function code = " + str( array_pkt[1:2] ) )					
							address = ( int(array_pkt[2], 16) * 256 ) + ( int(array_pkt[3], 16) )
							address += 400001
							MVT485fileparsedoutput.write(" start add = " + "{:.0f}".format( int( address ) ) )
							presetvalue = ( int(array_pkt[4], 16) * 256 ) + ( int(array_pkt[5], 16) )
							MVT485fileparsedoutput.write(" data = " + "{:.0f}".format( int( presetvalue ) ) )				
							crcvalue = ( int(array_pkt[6], 16) * 256 ) + ( int(array_pkt[7], 16) )
							MVT485fileparsedoutput.write(" CRC = " + "{:.0f}".format( int( crcvalue ) ) )
							
					elif functioncode == 16:
					
						if value_byte_count % 2 == 1:
							if packetprintenable == 1:
								MVT485fileparsedoutput.write( "\n" + str( array_pkt[0:value_byte_count] ) )
							
							string2 = "\nstart time " + "{:.6f}".format(valuestartpkt)
							MVT485fileparsedoutput.write(string2)
							MVT485fileparsedoutput.write(" query: node add = " + str( array_pkt[0:1] ) )
							MVT485fileparsedoutput.write(" function code = " + str( array_pkt[1:2] ) )					
							address = ( int(array_pkt[2], 16) * 256 ) + ( int(array_pkt[3], 16) )
							address += 400001
							MVT485fileparsedoutput.write(" start add = " + "{:.0f}".format( int( address ) ) )
							numberofregisters = ( int(array_pkt[4], 16) * 256 ) + ( int(array_pkt[5], 16) )
							MVT485fileparsedoutput.write(" # reg = " + "{:.0f}".format( int( numberofregisters ) ) )
							numberofbytes = ( int(array_pkt[6], 16) )
							MVT485fileparsedoutput.write(" number of bytes = " + "{:.0f}".format( int( numberofbytes ) ) )	
							presetvalue = ( int(array_pkt[7], 16) * 256 ) + ( int(array_pkt[8], 16) )
							MVT485fileparsedoutput.write(" data = " + "{:.0f}".format( int( presetvalue ) ) )				
							crcvalue = ( int(array_pkt[6], 16) * 256 ) + ( int(array_pkt[7], 16) )
							MVT485fileparsedoutput.write(" CRC = " + "{:.0f}".format( int( crcvalue ) ) )							
							
						elif value_byte_count == 8:
							if packetprintenable == 1:
								MVT485fileparsedoutput.write( "\n" + str( array_pkt[0:value_byte_count] ) )
							
							string2 = "\nstart time " + "{:.6f}".format(valuestartpkt)
							MVT485fileparsedoutput.write(string2)						
							MVT485fileparsedoutput.write(" response: node add = " + str( array_pkt[0:1] ) )
							MVT485fileparsedoutput.write(" function code = " + str( array_pkt[1:2] ) )					
							address = ( int(array_pkt[2], 16) * 256 ) + ( int(array_pkt[3], 16) )
							address += 400001
							MVT485fileparsedoutput.write(" start add = " + "{:.0f}".format( int( address ) ) )
							numberofregisters = ( int(array_pkt[4], 16) * 256 ) + ( int(array_pkt[5], 16) )
							MVT485fileparsedoutput.write(" # reg = " + "{:.0f}".format( int( numberofregisters ) ) )
							crcvalue = ( int(array_pkt[7], 16) * 256 ) + ( int(array_pkt[8], 16) )
							MVT485fileparsedoutput.write(" CRC = " + "{:.0f}".format( int( crcvalue ) ) )								
							
					else:
						if packetprintenable == 1:
							MVT485fileparsedoutput.write( "\n" + str( array_pkt[0:value_byte_count] ) )
						
						string2 = "\nstart time " + "{:.6f}".format(valuestartpkt)
						MVT485fileparsedoutput.write(string2)
				
				value_byte_count = 0

				# new line because next packet is starting
				MVT485fileoutput.write("\n")
				string2 = "time between packets " + "{:.6f}".format(timebetweenchars) + "\n"
				MVT485fileoutput.write(string2)
				string2 = "start time " + "{:.6f}".format(value1) + ",  + "
				MVT485fileoutput.write(string2)
				del array_pkt[:]
				array_pkt.append( string3 )
				valuestartpkt = value1
				
			MVT485fileoutput.write(string4)
		valuelastchar = value1

	MVT485file.flush()
	MVT485fileoutput.flush()
	MVT485fileparsedoutput.flush()
	sleep(1)
	
	MVT485file.close()
	MVT485fileoutput.close()
	MVT485fileparsedoutput.close()
	sleep(1)
	print("done")
input()
 

