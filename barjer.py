import datetime
import time
import RPi.GPIO as GPIO
import threading

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(22,GPIO.OUT,initial = GPIO.LOW)  # motor up
GPIO.setup(23,GPIO.OUT,initial = GPIO.LOW)  # motor down
GPIO.setup(27,GPIO.OUT,initial = GPIO.LOW)  # status lamp on/off
GPIO.setup(17,GPIO.OUT,initial = GPIO.LOW)  # automatik light
GPIO.setup(12,GPIO.IN,pull_up_down = GPIO.PUD_UP)  # up sensor detection
GPIO.setup(6,GPIO.IN,pull_up_down = GPIO.PUD_UP)  # down sensor detection
GPIO.setup(13,GPIO.IN,pull_up_down = GPIO.PUD_UP)  # safety sensor detection
GPIO.setup(5,GPIO.IN,pull_up_down = GPIO.PUD_UP)  # owerload sensor detection
GPIO.setup(20,GPIO.IN,pull_up_down = GPIO.PUD_UP)  # up command detection
GPIO.setup(21,GPIO.IN,pull_up_down = GPIO.PUD_UP)  # down command detection

counter=0
signal_lamp_stop=0
command_down=0
mesage_old=""

time.sleep(3)

#########################

def logwriter(mesage):

  mesagetime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  log=mesagetime +" "+ mesage +"\n"
  f=open("barjer.log","a")
  f.write(log)
  f.close()

#########################

def printt(mesage):

  global mesage_old

  if mesage==mesage_old:
    pass
  else:
    print mesage
    logwriter(mesage)
    mesage_old=mesage

#########################

printt("RPI_barjer_controller start")

#########################

def timer():

  global counter
  global command_down
  printt("timer on")
  counter=0

  while counter!=30:
    counter=counter+1
    print counter
    time.sleep(1)
  printt("timer off")
  command_down=1


#########################

def signal_lamp():

  global signal_lamp_stop
  printt("signal lamp on")
  signal_lamp_stop=0

  while signal_lamp_stop!=1:
    GPIO.output(27,GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(27,GPIO.LOW)
    time.sleep(0.5)
  print("signal lamp off")

#########################

while True:

  if GPIO.input(12)==0:
    printt("up sensor detected")
  if GPIO.input(6)==0:
    printt("down sensor detected")
  if GPIO.input(13)==0:
    printt("safety sensor detected")
  if GPIO.input(5)==0:
    printt("owerload sensor detected")

  if GPIO.input(20)==0:  #up command detected

    printt("up command detected")
    printt("automatik light on")
    GPIO.output(17,GPIO.HIGH)
    signal_lamp_stop=1
    time.sleep(2)
    t2=threading.Thread(target=signal_lamp)
    t2.start()

    while GPIO.input(12)!=0 and GPIO.input(5)!=0:
      GPIO.output(23,GPIO.HIGH)
      printt("moving up")
      time.sleep(0.5)

    if GPIO.input(12)==0:
      printt("barjer is open")
      GPIO.output(23,GPIO.LOW)
      counter=30
      signal_lamp_stop=1
      time.sleep(2)
      printt("automatik light off")
      command_down=0
      GPIO.output(17,GPIO.LOW)
      t1=threading.Thread(target=timer)
      t1.start()
    else:
      printt("error while moving up")
      GPIO.output(23,GPIO.LOW)
  else:
    signal_lamp_stop=1
    time.sleep(1)

  if GPIO.input(21)==0 or command_down==1:  #down command detected
    printt("down command detected")
    printt("automatik light on")
    GPIO.output(17,GPIO.HIGH)
    signal_lamp_stop=1
    time.sleep(2)
    t2=threading.Thread(target=signal_lamp)
    t2.start()

    while GPIO.input(6)!=0 and GPIO.input(5)!=0 and GPIO.input(13)!=0:
      GPIO.output(22,GPIO.HIGH)
      printt("mowing down")
      time.sleep(0.5)

    if GPIO.input(13)==0:
      GPIO.output(22,GPIO.LOW)
      while GPIO.input(12)!=0 and GPIO.input(5)!=0:
        GPIO.output(23,GPIO.HIGH)
        printt("safety sensor > moving up")
        time.sleep(0.5)

      if GPIO.input(12)==0:
        printt("barjer is open safety sensor detected")
        GPIO.output(23,GPIO.LOW)
      else:
        printt("command safety up > error while moving up")
        if GPIO.input(5)==0:
          GPIO.output(23,GPIO.LOW)
          counter=30
          time.sleep(2)
          command_down=0
          continue
        else:
          GPIO.output(23,GPIO.LOW)
          counter=30
          time.sleep(2)
          command_down=1
      time.sleep(5)
      printt("safety sensor > moving down")
    else:
      pass

    if GPIO.input(6)==0:
      printt("barjer is closed")
      GPIO.output(22,GPIO.LOW)
      counter=30
      signal_lamp_stop=1
      time.sleep(2)
      command_down=0
      printt("automatik light off")
      GPIO.output(17,GPIO.LOW)
    else:
      printt("error while moving down")
      if GPIO.input(5)==0:
        GPIO.output(22,GPIO.LOW)
        counter=30
        time.sleep(2)
        command_down=0
      else:
        GPIO.output(22,GPIO.LOW)
        counter=30
        time.sleep(2)
        command_down=1
  else:
    signal_lamp_stop=1
    time.sleep(1)




#end
