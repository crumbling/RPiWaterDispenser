import RPi.GPIO as GPIO
import LCD1602 
from ABE_ADCPi import ADCPi             	#import the ADCPi library
from ABE_helpers import ABEHelpers      	#import ABEHelpers for smbus
import time		                	#import time module for delay
import smbus		                	#import smbus for i2c
LCD1602.init(0x27, 1)                   	#Assign LCD i2c address

GPIO.setwarnings(False)                 #remove uncecessary warnings
GPIO.setmode(GPIO.BCM)                  #setting pin mode to BCM

i2c_helper=ABEHelpers()	       #Creating instance of ABEHelpers() for i2c_bus object
bus=i2c_helper.get_smbus()	 	#Creating instance of i2c_bus
ADC=ADCPi(bus, 0X69, 0X6f, 18)   	#Set the i2c configuration address and bit rate
time.sleep(0.2)
#########

#Keypad input/output pins
GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_UP) 
GPIO.setup(20, GPIO.IN, pull_up_down = GPIO.PUD_UP) 
GPIO.setup(21, GPIO.IN, pull_up_down = GPIO.PUD_UP) 
GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP) 

GPIO.setup(23, GPIO.OUT) 
GPIO.setup(24, GPIO.OUT) 
GPIO.setup(25, GPIO.OUT) 
GPIO.setup(26, GPIO.OUT)

#Initializing the GPIO pins for Ultrasound, Buzzer, motion sensor, and LED
GPIO.setmode(GPIO.BCM) 
TRIG=13 #ultrasonic
GPIO.setup(TRIG,GPIO.OUT)
ECHO=12 #ultrasonic
GPIO.setup(ECHO,GPIO.IN)
BUZZ=17 #buzzer
GPIO.setup(BUZZ, GPIO.OUT)
MOTION=27 #motion
GPIO.setup(MOTION, GPIO.IN, pull_up_down=GPIO.PUD_UP)
LEDR=16 #Hot water LED
GPIO.setup(LEDR, GPIO.OUT)
LEDG=5 #System on LED
GPIO.setup(LEDG, GPIO.OUT)
LEDB=4 #water being dispensed LED
GPIO.setup(LEDB, GPIO.OUT)

SWITCH=6 #switch to turn on/off system
GPIO.setup(SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#function to read water level, simulated by potentiometer, returns percentage value
def getwaterlevel():
    wlevel=ADC.read_voltage(1)*100.0/5.0    #reading analog input
    return wlevel

def gettemp():
    temperature_volts= ADC.read_voltage(2) # reading analog value for temperature is 
                                                                             # in volts on channel 2
    temperature_Celcius = temperature_volts/0.01 # converting temp from voltage to temp in oC.
    print(temperature_Celcius)
    return (temperature_Celcius)


#Utilizing a function to calculate distance to the ultrasound buzzer
def distance ():
    GPIO.output(TRIG,0)
    time.sleep(0.000002)
    GPIO.output(TRIG,1)
    time.sleep(0.00001)
    GPIO.output(TRIG,0)
    while GPIO.input(ECHO)==0:
        a=0
    time1=time.time()
    while GPIO.input(ECHO)==1:
        a=0
    time2=time.time()
    duration=time2-time1
    return duration*1000000/58          #returns distance in cm

#Motion interrupt function, to indicate motion when required
def motion(self):
    global flag
    flag=1

#Heating function to read temperature and start heating according to specified temp
def heating():
    global heat_led
    if(gettemp()<26):       #checks temp less than 26
        print("Heating on") #turns on heating 
        GPIO.output(LEDR, GPIO.HIGH)
    else:
        print("Heating off")
        GPIO.output(LEDR, GPIO.LOW)

#defining variable for state of system on/off 
on_off=True
#On_off function to run when system is interrupted by switch input
def ON_OFF(self):   
    global on_off
    LCD1602.clear()
    if GPIO.input(SWITCH)==0:   #if system is off
        GPIO.output(LEDR, GPIO.LOW)
        GPIO.output(LEDG, GPIO.LOW)
        on_off=False
    else:                       #if system is on
        GPIO.output(LEDG, GPIO.HIGH)
        on_off=True

#Interrupts, for detecting on/off and for detecting motion 
GPIO.add_event_detect(SWITCH, GPIO.BOTH, callback=ON_OFF, bouncetime=2000)
GPIO.add_event_detect(MOTION, GPIO.FALLING, callback=motion, bouncetime=2000)

#Keypad function to read keypad, no shift values
def keypad(): 
    while(True & on_off):   #also checks if system is on, if not keypad returns 0
        GPIO.output(26, GPIO.LOW)
        GPIO.output(25, GPIO.HIGH)
        GPIO.output(24, GPIO.HIGH)
        GPIO.output(23, GPIO.HIGH)

        if (GPIO.input(22)==0):
            return(0)
            break

        if (GPIO.input(21)==0):
            return(4)
            break

        if (GPIO.input(20)==0):
            return(8)
            break

        if (GPIO.input(19)==0):
            return(0XC)
            break

        GPIO.output(26, GPIO.HIGH)
        GPIO.output(25, GPIO.LOW)
        GPIO.output(24, GPIO.HIGH)
        GPIO.output(23, GPIO.HIGH)

        if (GPIO.input(22)==0):
            return(1)
            break

        if (GPIO.input(21)==0):
            return(5)
            break

        if (GPIO.input(20)==0):
            return(9)
            break
 
        if (GPIO.input(19)==0):
            return(0XD)
            break


        GPIO.output(26, GPIO.HIGH)
        GPIO.output(25, GPIO.HIGH)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(23, GPIO.HIGH)

        if (GPIO.input(22)==0):
            return(2)
            break

        if (GPIO.input(21)==0):
            return(6)
            break
        #Scan row 2
        if (GPIO.input(20)==0):
            return(0XA)
            break
 
        if (GPIO.input(19)==0):
            return(0XE)
            break

        GPIO.output(26, GPIO.HIGH)
        GPIO.output(25, GPIO.HIGH)
        GPIO.output(24, GPIO.HIGH)
        GPIO.output(23, GPIO.LOW)

        if (GPIO.input(22)==0):
            return(3)
            break

        if (GPIO.input(21)==0):
            return(7)
            break

        if (GPIO.input(20)==0):
            return(0XB)
            break

        if (GPIO.input(19)==0):
            return(0XF)
            break
    return 0

b=GPIO.PWM(BUZZ,100)
b.start(0)
#Defining a buzzer function that turns buzzer on/off
def buzzer(x):
    #starts buzzer
    if(x==1):
        print("buzzer starting")
        b.ChangeDutyCycle(50)
    else:
        b.ChangeDutyCycle(0)

##########################################################################
############################## Main Program ##############################
##########################################################################        
while True:
    if on_off:      #checks if system is on
        global flag
        flag=0
        heating()   #checks if heating needs to be turned on/off
        wl=getwaterlevel()  #checks water level
        LCD1602.write(0,0,"1:HOT   2:COLD  ")
        LCD1602.write(0,1,"WLevel:%0.02f %%" %wl)
        if (wl<10):         #buzzer starts if water level too low
            print("Water Level:%0.02f%%" %wl)
            buzzer(1)
        else:
            print(wl)
            buzzer(0)
        password=65
        sel = keypad()
        time.sleep(0.3)
        if sel == 1:        #selection 1 - Hot water (requires password)
            LCD1602.clear()
            LCD1602.write(0,0,"Enter pass:         ")
            n1 = keypad()
            LCD1602.write(0,0,"Enter pass:*        ")
            time.sleep(0.3)
            n2 = keypad()
            LCD1602.write(0,0,"Enter pass:**       ")
            time.sleep(0.3)
            n = n1*10 + n2
            print (n)       #reads password, prints to terminal
            LCD1602.clear()
            if n == password:   #checks if password is true
                while flag==0:  #waits for motion
                    LCD1602.write(0,0,"Place Glass")    
                while (distance()>5):       #waits until glass nearby
                    print("Glass too far")
                    LCD1602.write(0,0,"Glass too far")
                    time.sleep(0.2)
                print("Hot Dispensing")     #starts dispensing    
                LCD1602.write(0,0,"Hot Dispensing    ")
            else:               #incorrect password returns to main loop
                print("Incorrect Password") 
                LCD1602.write(0,0,"Incorrect Pass")
                time.sleep(0.5)
                continue
        
        if sel == 2:    #selection 2 - Cold water (no password)
            LCD1602.clear()
            while flag==0:  #waits for motion
                LCD1602.write(0,0,"Place Glass")
            while (distance()>5):       #waits until glass is nearby
                print("Glass too far")
                LCD1602.write(0,0,"Glass too far")
                time.sleep(0.2)
                
            print("Cold Dispensing")        #starts dispensing
            LCD1602.write(0,0,"Cold Dispensing    ")
        else:
            continue
        #Initializing LED
        l=GPIO.PWM(LEDB,2)      #starting the dispensing LED to flash
        l.start(50)
        time.sleep(2)
        flag=0
        l.ChangeDutyCycle(0)
        LCD1602.clear()
        time.sleep(0.2)
                    
    else:                       #condition when system is off
        print("System is off")
        LCD1602.write(0,0,"OFF")
        time.sleep(0.1)
 
