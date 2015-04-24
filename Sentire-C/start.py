import serial, time, datetime, sys
from struct import *
from xbee import ZigBee
import time
import sqlite3
import smtplib





##############################################################################################
def sendmail (current_time, temp1, temp2, batt):

    smtpUser = 'monitor@boosterjuice.com'
    smtpPass = 'Radish6'
    toAdd = 'monitor@boosterjuice.com'
    fromAdd =  'store1234@boosterjuice.com'
    subject = 'Test - Store:1234 temperature readings'
    header = 'To: ' + toAdd + '\n' +'From: ' + fromAdd + '\n' + 'Subject: ' + subject
    body = current_time + ', ' + str(temp1) + ', ' + str(temp2) + ', ' + str(batt)
    #print header + '\n' + body
    s = smtplib.SMTP('mail.boosterjuice.com',8025)
    s.ehlo()
    #s.starttls()
    s.ehlo()
    s.login(smtpUser, smtpPass)
    s.sendmail(fromAdd, toAdd, header + '\n\n' + body)
    s.quit()



#############################################################################################
#This function pulls the two temperature readings, the batery level, and mac address
# of the sensors
def get_readings(data):
    #iterate over data elements
    temperature1 = 1.0303030303030303
    temperature2 = 1.20202020202020202
    battery = 1.00000000000
    vtemp1 = []
    vtemp2 = []
    vbatt = []
    address= []
    for item in data:
        vtemp1.append(item.get('adc-1'))
        vtemp2.append(item.get('adc-2'))
        vbatt.append(item.get('adc-7'))
        temperature1=sum(vtemp1)
        temperature2=sum(vtemp2)
        battery=sum(vbatt)

        #now calculate the proper mv
        #Each reading is mulltiplied by the reference voltage of the Xbee2,
        # Subtracted by 500 (which is the TMP36 set point) and then /10 to move the decimel :-)
        temperature1 = ((temperature1*1.2)-500)/10
        temperature2 = ((temperature2*1.2)-500)/10
        #The battery reading is multiplied by a factor which is derived from 1024/1000
        battery = (battery*1.171875)/1000

    #return the two temperature readings....touse it...
    #  temp1, temp2 = Get_temperature(data, format"c")
    return (temperature1,temperature2,battery)




#############################################################################################
#  This function saves the reading into a sqllite database locally on the coordinator

def save_temp_reading (store_str, zone_str, temp1, temp2, batt, source_addr):
    # I used triple quotes so that I could break this string into two lines for formatting purposes
    curs.execute("INSERT INTO temperature_log values( (?), (?), (?), (?), (?), (?), (?) )", (int(time.time()), store_str,zone_str,temp1,temp2,batt,source_addr))

    # commit the changes
    conn.commit()
    return





SERIALPORT = "/dev/ttyAMA0"     # the com/serial port the XBee is connected to
BAUDRATE = 9600                 # the baud rate we talk to the xbee
TEMPSENSE = 0                   # which XBee ADC has current draw data
STORE = "777"
ZONE = "Walk In"                # for now, when we add a second unit we will change this
TABLENAME = 'temperature_log'   # Name of the table in the SQLlite database
battery = 0


conn=sqlite3.connect('omega-appdata.db')
curs=conn.cursor()
###   --> This next two lines are for debugging....to kill the table
#sql = 'drop table ' + TABLENAME
#curs.execute(sql)

###--> Setup the table in the database.
sql = 'create table if not exists ' + TABLENAME + ' (time TEXT,stor_str TEXT,zone_str TEXT,air_temp1 INTEGER,prod_temp2 INTEGER,batt INTEGER,src_addr TEXT)'
curs.execute(sql)


ser = serial.Serial(SERIALPORT, BAUDRATE)
ser.close()
ser = serial.Serial(SERIALPORT, BAUDRATE)

xbee = ZigBee(ser)
print ('Starting Up Tempature Monitor')
# Continuously read and print packets

while True:
    try:
        response = xbee.wait_read_frame()
        current_time = time.asctime( time.localtime(time.time()) )
        #print response
        temperature1, temperature2, battery = get_readings(response['samples'])
        addr_raw = (response ['source_addr_long'])
        addr_raw = addr_raw.strip("\\x")
        addr = ':'.join("{:02X}".format(ord(c)) for c in addr_raw)

        #print our timestamp and tempature to standard_out
        print ("{0}, {1}, {2}, {3}, {4}, {5}, {6}").format(int(time.time()), STORE, ZONE, temperature1, temperature2, battery, addr)

        #save the tempature to the databse
        save_temp_reading(STORE, ZONE, temperature1, temperature2, battery, addr)

        #Send temperature readings to BoosterJuice email parser (right now, just to me)
        #sendmail (current_time, temperature1, temperature2, battery)
    except serial.serialutil.SerialException:
        print ("boink") 
                

ser.close()
