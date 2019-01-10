from __future__ import print_function
import pyzbar.pyzbar as pyzbar
import numpy as np
import cv2
import threading
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import RPi.GPIO as GPIO
import csv


def camera():
    global frame
    global cam

    raw_cap = PiRGBArray(cam,(1920,1088))
    try:
        for frame in cam.capture_continuous(raw_cap,format="bgr",use_video_port=True,splitter_port=2,resize=(1920,1088)):
            time.sleep(0.05)
            raw_cap.truncate(0)          
            if exit:
                break
            
    except KeyboardInterrupt:
        GPIO.cleanup()

          
def decode(im) : 
    # Find barcodes and QR codes
    decodedObjects = pyzbar.decode(im)

    # Print results
    for obj in decodedObjects:
        print('Type : ', obj.type)
        print('Data : ', obj.data,'\n')

    return decodedObjects


# Display barcode and QR code location  
def display(im, decodedObjects):
    h,w,c=im.shape

    # Loop over all decoded objects
    for decodedObject in decodedObjects: 
        #points = decodedObject.location
        points=((0,0),(w,0),(h,w),(0,h))
        # If the points do not form a quad, find convex hull
        if len(points) > 4 : 
            hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
            hull = list(map(tuple, np.squeeze(hull)))
        else : 
            hull = points;

        # Number of points in the convex hull
        n = len(hull)

        # Draw the convext hull
        for j in range(0,n):
        cv2.line(im, hull[j], hull[ (j+1) % n], (255,0,0), 3)

    # Display results 
    cv2.imshow("Results", im);

def im_detect():
    t1=time.time()
    
    while True:
        im = frame.array
        decodedObjects = decode(im)
        if decodedObjects is not None:
            for obj in decodedObjects:
                check_data(str(obj.data))

        if found==0:
            t2=time.time()

        if t2-t1>=6:
            print "ID not registered, pls pay cash."
            break

    return

def check_data(dat):
    global found
    found=0
    fields = []
    rows = []
    
    # reading csv file
    with open("Input Table1.csv",'r') as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)
        
        # extracting field names through first row
        fields.append(csvreader.next())

        # extracting each data row one by one
        for row in csvreader:
            rows.append(row)

    for row in rows:
        if dat==row[0] and int(row[1])>=100 :
            print 'Transaction successful'
            row[1]= int(row[1])-100
            print 'remaining balance',row[1]
            writer=csv.writer(open('Input Table1.csv','wb'))
            writer.writerows(fields)
            writer.writerows(rows)
            barrier()
            found=1
            break

        elif dat==row[0] and int(row[1])<100 :
            print 'Transaction unuccessful.','Please recharge your wallet'
            found=1
            break

    csvfile.close()
    return

def barrier():
    Motor1A = 15
    Motor1B = 29
    sensor2= 30
    GPIO.setup(Motor1A,GPIO.OUT)
    GPIO.setup(Motor1B,GPIO.OUT)
    GPIO.setup(sensor2,GPIO.IN)
    right = GPIO.PWM(Motor1A, 100)
    right.start(10)
    GPIO.output(Motor1B,GPIO.LOW)
    time.sleep(0.3)
    right.stop()
    while not GPIO.input(sensor2):
        time.sleep(0.2)

    right.start(90)
    GPIO.output(Motor1B,GPIO.HIGH)
    time.sleep(0.2)
    right.stop()
    return
    
      
# Main 
if __name__ == '__main__':

    exit=0 #refers to exit status of program
    #open=0 #refers to opening of barrier
    found=0 #refers to if QR code is found in database
        
    ##SETTING UP PICAM MODULE
    cam = PiCamera()
    cam.resolution = (1920,1088)
    cam.framerate = 50

    #frame: contains continuous frames from picam
    frame= PiRGBArray(cam,(1920,1088))
    #Define camera thread
    cam_thread= threading.Thread(target=camera)


    #Setting Database
    filename = "Input Table1.csv"
            
    #Setting RPI
    GPIO.setmode(GPIO.BOARD)
    sensor1 = 16 #sensor1
    buzzer = 18
    GPIO.setup(sensor1,GPIO.IN)
    GPIO.setup(buzzer,GPIO.OUT)
    GPIO.output(buzzer,False)
        
    try:
        while True:
            if GPIO.input(sensor1):
                GPIO.output(buzzer,True)
                print "Object Detected"
                cam_thread.start()  ##Start camera thread
                time.sleep(1.5)
                GPIO.output(buzzer,False)
                im_detect()
                cam_thread.stop()  ##Stop camera thread

            else:
                GPIO.output(buzzer,False)


    except KeyboardInterrupt:
        GPIO.cleanup()
