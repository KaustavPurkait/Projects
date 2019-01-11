## Team Id: PB#4183
## Author List: Rohit Kumar, Harsh, Kaustav Purkait, Ashutosh Samal
## Filename: task4-main.py
## Theme: Planter Bot
## Functions: camera(),motor(), blink(color,num),dist(x,y),take_pic(),overlay(color,shape,num),
##      cords(x1,y1,x2,y2),blend_transparent(face_img, overlay_t_img), blink_list(color_list)
## Global Variable: frame, exit,state,repeat,led,slow,cam


#add the imports
import cv2
import os
import threading
from picamera import PiCamera
from picamera.array import PiRGBArray
import RPi.GPIO as GPIO
import numpy as np
import time
import math
import csv



##THREAD TO CONTINUOUSLY TAKE PICS TO ANALYSE
##Function Name: camera()
##Input: None
##Output: Output
##Logic: This function defines the picam camera thread. It ensures the picam keeps taking pictures without slowing down the main thread. The global variable raw_cap keeps storing the variables
##Example Call: camera()

def camera():
    global frame
    global cam

    raw_cap = PiRGBArray(cam,(160,128))
    for frame in cam.capture_continuous(raw_cap,format="bgr",use_video_port=True,splitter_port=2,resize=(160,128)):
        raw_cap.truncate(0)
            
        if exit:
            break
        



##THREAD TO CONTROL MOTOR
##Function Name: motor()
##Input: None
##Output: None
##Logic: Thread to control motor. Various states are given based on the direction we need the bot to move. Description of each state given later
##Example Call: motor()

def motor():
    global state
    global exit
    time.sleep(2.5)
    Motor1A = 15
    Motor1B = 29
    Motor2A = 33
    Motor2B = 31

    GPIO.setup(Motor1A,GPIO.OUT)
    GPIO.setup(Motor1B,GPIO.OUT)
    GPIO.setup(Motor2A,GPIO.OUT)
    GPIO.setup(Motor2B,GPIO.OUT)
    right = GPIO.PWM(Motor1A, 100)
    left = GPIO.PWM(Motor2A,100)

    right.start(0)
    left.start(0)

    print "Turning motor on"
    GPIO.output(Motor1B,GPIO.LOW)
    GPIO.output(Motor2B,GPIO.LOW)

    ##STATE 0 = GO STRAIGHT
    ##STATE 1= TURN LEFT(TURN RIGHT MOTOR)
    ##STATE 2= TURN RIGHT(TURN LEFT MOTOR)
    ##STATE 4= STOP AND CHECK
    ##STATE 5= TURN RIGHT SHARP(RIGHT MOTOR FRONT LEFT MOTOR BACK
    ##STATE 6= TURN LEFT SHARP(LEFT MOTOR FRONT RIGHT MOTOR BACK
    ##STATE 9= SHED(STOP)
    ##STATE 10= PLANTATION ZONE
    ##STATE 11= GO LEFT THEN RIGHT (MAKING STRAIGHT LINES MORE ACCURATE FOR PZ DETECTION)
    ##STATE 12= GO RIGHT THEN LEFT  
    
    while not exit:

        if slow>10 and repeat ==0: #At low speed near PZ, the bot rotates rather than turning
            if state==1:
                state=6
            if state==2:
                state=5

        if PZ==5: #After PZ 5, the bot moves straight rather than left or right
            if state==5 or state==6:
                state=0

        #GO STRAIGHT
        if state ==0:
            if slow >10 and repeat==0: #lower speed near PZs
                right.ChangeDutyCycle(10)
                left.ChangeDutyCycle(10)
            elif slow <=0:
                right.ChangeDutyCycle(30) # in straight lines
                left.ChangeDutyCycle(32)
            else:
                right.ChangeDutyCycle(25) #at curves
                left.ChangeDutyCycle(25)

            GPIO.output(Motor1B,GPIO.LOW)
            GPIO.output(Motor2B,GPIO.LOW)
            time.sleep(0.03)

        #TURN LEFT  
        elif state ==1:
            right.ChangeDutyCycle(30)             
            left.ChangeDutyCycle(0)
            GPIO.output(Motor1B,GPIO.LOW)
            GPIO.output(Motor2B,GPIO.LOW)
            time.sleep(0.03)

        #TURN RIGHT
        elif state ==2:
            left.ChangeDutyCycle(30)                
            right.ChangeDutyCycle(0)
            GPIO.output(Motor1B,GPIO.LOW)
            GPIO.output(Motor2B,GPIO.LOW)
            time.sleep(0.03)

        #STOP AND CHECK when bot fails to detect contours due to motion blur
        elif state ==4:
            right.ChangeDutyCycle(0)
            left.ChangeDutyCycle(0)
            GPIO.output(Motor1B,GPIO.LOW)
            GPIO.output(Motor2B,GPIO.LOW)
            time.sleep(0.03)

        #TURN LEFT SHARP
        elif state ==6:
            if slow>10 and repeat==0: #near PZs slower speed for improved detection
                left.ChangeDutyCycle(90)
                right.ChangeDutyCycle(10)
                
            else:
                left.ChangeDutyCycle(75)
                right.ChangeDutyCycle(25)

                
            GPIO.output(Motor1B,GPIO.LOW)
            GPIO.output(Motor2B,GPIO.HIGH)
            time.sleep(0.03)
            
        #TURN RIGHT SHARP
        elif state==5:
            if slow>10 and repeat==0: #near PZs
                right.ChangeDutyCycle(90)
                left.ChangeDutyCycle(10)
            else:
                right.ChangeDutyCycle(75)
                left.ChangeDutyCycle(25)
            GPIO.output(Motor1B,GPIO.HIGH)
            GPIO.output(Motor2B,GPIO.LOW)
            time.sleep(0.03)    

        elif state ==9: ## SHED
            right.ChangeDutyCycle(30)
            left.ChangeDutyCycle(30)
            GPIO.output(Motor1B,GPIO.LOW)
            GPIO.output(Motor2B,GPIO.LOW)
            time.sleep(1)
            left.ChangeDutyCycle(0)
            right.ChangeDutyCycle(0)
            GPIO.output(Motor1B,GPIO.LOW)
            GPIO.output(Motor2B,GPIO.LOW)
            time.sleep(2)
            print "SHED"
            exit=1

        elif state ==10: ##PLANTATION ZONE
            left.ChangeDutyCycle(0)
            right.ChangeDutyCycle(0)
            GPIO.output(Motor1B,GPIO.LOW)
            GPIO.output(Motor2B,GPIO.LOW)
            if repeat ==0:
                time.sleep(1)
            while led: #while led is on bot doesnot move
                time.sleep(0.2)
                
            left.ChangeDutyCycle(30)
            right.ChangeDutyCycle(30)
            GPIO.output(Motor1B,GPIO.LOW)
            GPIO.output(Motor2B,GPIO.LOW)
            time.sleep(0.1)
            

        elif state==11: #GO LEFT THEN RIGHT
            right.ChangeDutyCycle(30)
            left.ChangeDutyCycle(22)
            GPIO.output(Motor1B,GPIO.LOW)
            GPIO.output(Motor2B,GPIO.LOW)
            time.sleep(0.1)
            
            right.ChangeDutyCycle(0)
            left.ChangeDutyCycle(20)
            time.sleep(0.03)
            
        elif state==12: #GO RIGHT THEN LEFT
            right.ChangeDutyCycle(22)
            left.ChangeDutyCycle(30)
            GPIO.output(Motor1B,GPIO.LOW)
            GPIO.output(Motor2B,GPIO.LOW)
            time.sleep(0.1)

            right.ChangeDutyCycle(20)
            left.ChangeDutyCycle(0)
            time.sleep(0.03)
            
    ## After shed is detected bot moves 1 sec to reach shed
    right.ChangeDutyCycle(100) 
    left.ChangeDutyCycle(100)
    GPIO.output(Motor1B,GPIO.LOW)
    GPIO.output(Motor2B,GPIO.LOW)
    time.sleep(1)
    
    left.stop()
    right.stop()
    GPIO.output(Motor1A,GPIO.LOW)
    GPIO.output(Motor1B,GPIO.LOW)
    GPIO.output(Motor2A,GPIO.LOW)
    GPIO.output(Motor2B,GPIO.LOW)
    time.sleep(2)
    return


##Blinking the LED
##Function Name: blink
##Input: color, num
##Output: None
##Logic: Function takes the input of color detected at plantation zone and number of contours and blinks the requisite colour the given number of times
##Example Call: blink("red",3)

def blink(color,num):

    
    GPIO.setup(red, GPIO.OUT) 
    GPIO.setup(green, GPIO.OUT)
    GPIO.setup(blue, GPIO.OUT)
    GPIO.output(red,GPIO.LOW)
    GPIO.output(blue,GPIO.LOW)
    GPIO.output(green,GPIO.LOW)
    
    if color == "undetected":
        return
    elif color == "blue":
        col= blue
    elif color == "green":
        col=green
    elif color== "red":
        col= red
        
    if num>0 and num<5:
        for i in range(0,num):
            GPIO.output(col,GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(col,GPIO.LOW)
            time.sleep(0.5)

    return


##Blinking the LED list
##Function Name: blink_list
##Input: color_list
##Output: None
##Logic: Function takes the list of PZ colours and blinks the LEDs according to them
##Example Call: blink_list(PZ_list)

def blink_list(color_list):
##    GPIO.setmode(GPIO.BOARD)
##    green =18
##    red = 16
##    blue = 22
    
    GPIO.setup(red, GPIO.OUT) 
    GPIO.setup(green, GPIO.OUT)
    GPIO.setup(blue, GPIO.OUT)
    GPIO.output(red,GPIO.LOW)
    GPIO.output(blue,GPIO.LOW)
    GPIO.output(green,GPIO.LOW)

    for i in color_list:
        if i=="red":
            GPIO.output(red,GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(red,GPIO.LOW)
            time.sleep(0.5)
        elif i== "green":
            GPIO.output(green,GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(green,GPIO.LOW)
            time.sleep(0.5)
        elif i=="blue":
            GPIO.output(blue,GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(blue,GPIO.LOW)
            time.sleep(0.5)

    return



    

##CALCULTING END POINTS OF HOUGHLINES
##Function Name: cords
##Input: x1,y1,x2,y2
##Output: cord
##Logic: We use mathematical functions to find the end coordinates of the houghlines in our
##      (160,128) resolution. These endpoints are later used to detect colours of contours and
##      form boundary rectangles
##Example Call: cords(-56,1000,100,-986)

def cords(x1,y1,x2,y2):
    x=x2-x1
    if x2==x1:
        x=0.001
    m= float(y2-y1)/x ##calculating gradient
    if m==0:
        m=0.001

    y_x0= m*(0-x1)+y1  ##calculating cords using mathematical formulas
    y_x159= m*(159-x1)+y1
    x_y0= (float)(0-y1)/m +x1
    x_y127= (float)(127-y1)/m +x1

    cord=[]
    
    if y_x0>=0 and y_x0<=127:
        cord.append((int(y_x0),0))

    if x_y127>=0 and x_y127<=159:
        cord.append((127,int(x_y127)))

    if y_x159>=0 and y_x159<=127:
        cord.append((int(y_x159),159))


    if x_y0>=0 and x_y0<=159:
        cord.append((0,int(x_y0)))

    return cord



##CALCULATE DISTANCE BETWEEN 2 POINTS
##Function Name: dist(x,y)
##Input: x,y (which are 2 coordinates)
##Output: d (distance)
##Logic: uses pythogoras theorm to calculate distance between 2 coordinates
##Example Call: dist((24,56),(100,127))

def dist(x,y):
    d=math.sqrt((x[0]-y[0])*(x[0]-y[0]) + (x[1]-y[1])*(x[1]-y[1]))
    return d



##FOR PIC ANALYSIS
##Function Name: take_pic()
##Input: None
##Output: None
##Logic: This function is called when a PZ is detected. Contours are detected in this function.
##      Colour detected by detecting colour at the centroid of the shape. The shape is detected
##      based on ratio of area of contour to minimum area rectangle rather than by counting
##      number of sides. Then it calls the overlay and blink function for the plantation and led
##Example Call: take_pic

def take_pic():
    global cam
    global led
    global PZ
    led=1
    cam.resolution = (640,480)
    PZ_img = PiRGBArray(cam,(640,480))
    cam.capture(PZ_img,format="bgr",splitter_port=1)

    PZ_inp= PZ_img.array
    
    kernel=np.ones((3,3),np.uint8)
    gray=cv2.cvtColor(PZ_inp,cv2.COLOR_BGR2GRAY)
    canny= cv2.Canny(gray,30,150)
    canny = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)
    image, contours, hierarchy = cv2.findContours(canny,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    ##Creating new list to store only path contours
    contours_inp=[]
    
    color="undetected"
    shape = "undetected"

    cir=0
    sq=0
    tri=0
    bl=0
    gr=0
    re=0

    for line in contours:
        approx = cv2.approxPolyDP(line,0.01*cv2.arcLength(line,True),True)
        m = len(approx)

        if 100<(cv2.arcLength(line,True))<300 and m>2 and (cv2.contourArea(line))>500:
            contours_inp.append(line)

    #Detection and display of name of shape
    if contours_inp is not []:
        for a in range(0,len(contours_inp)/2):
            i=a*2
            M=cv2.moments(contours_inp[i])
            if M['m00'] == 0:
                m00=0.01
            else:
                m00=M['m00']
                
            cx = int(M['m10']/m00)
            cy = int(M['m01']/m00)

            m = len(approx)
            rect = cv2.minAreaRect(contours_inp[i])
            box = cv2.boxPoints(rect)
            ##CALCULATE MIN AREA
            h= dist(box[0],box[1])
            l= dist(box[1],box[2])
            area= h*l
            print "ratio=",cv2.contourArea(contours_inp[i])/float(area)
            ratio= cv2.contourArea(contours_inp[i])/float(area)
            box = np.int0(box)
            inp = cv2.drawContours(PZ_inp,[box],0,(0,0,255),2)

            color_b,color_g,color_r= inp[cy,cx]
            
            if color_b>=color_g and color_b>color_r:
                #color="Blue"
                bl+=1
               
            elif color_g>color_b and color_g>color_r :
                #color= "Green"
                if abs(int(color_b)-int(color_g))>10:
                    gr+=1
                else:
                    bl+=1
                
            elif color_r>color_b and color_r>color_g:
                #color= "Red"
                re+=1
               
            print inp[cy,cx]
            if ratio>=0.86:
                #Square detected
                sq+=1
            elif ratio<0.69:
                #Triangle detected
                tri+=1
            elif ratio>=0.69 or ratio < 0.86:
                #Circle detected
                cir+=1
            

    if cir>sq and cir>tri:
        shape="circle"
    elif sq>cir and sq>tri:
        shape="square"
    elif tri>cir and tri>sq:
        shape= "triangle"

    if bl>gr and bl>re:
        color="blue"
    elif gr>re and gr>bl:
        color="green"
    elif re>gr and re>bl:
        color= "red"

    num= len(contours_inp)/2   
    print "number of contours=",num
    print "color=",color
    print "shape=",shape
    cam.resolution = (160,128)
    if num>0 and PZ<5 and color != "undetected" and shape != "undetected":
        overlay(color,shape,num) 
        blink(color,num)
        for i in range(0,num):
            PZ_list.append(color)
            
    led=0
    return

##Function Name: blend_transperent
##Input: face_img,overlay_img
##Output: overlayed image
##Logic: Overlays the image by creating a mask of the overlay_t_img and overlaying it on
##      the face_img
##Example Call: blend_transparent(face_img,overlay_t_img)

def blend_transparent(face_img, overlay_t_img):
    # Split out the transparency mask from the colour info
    overlay_img = overlay_t_img[:,:,:3] # Grab the BRG planes
    overlay_mask = overlay_t_img[:,:,3:]  # And the alpha plane

    # Again calculate the inverse mask
    background_mask = 255 - overlay_mask

    # Turn the masks into three channel, so we can use them as weights
    overlay_mask = cv2.cvtColor(overlay_mask, cv2.COLOR_GRAY2BGR)
    background_mask = cv2.cvtColor(background_mask, cv2.COLOR_GRAY2BGR)

    # Create a masked out face image, and masked out overlay
    # We convert the images to floating point in range 0.0 - 1.0
    face_part = (face_img * (1 / 255.0)) * (background_mask * (1 / 255.0))
    overlay_part = (overlay_img * (1 / 255.0)) * (overlay_mask * (1 / 255.0))
    
    # And finally just add them together, and rescale it back to an 8bit integer image    
    return np.uint8(cv2.addWeighted(face_part, 255.0, overlay_part, 255.0, 0.0))


##Function Name: Overlay
##Input: color,shape,num
##Output: None
##Logic: Overlays the requisite number of flowers based on colour and shape of the contours
##      in the PZ. Each plantation zone in the Plantation image is divided into zones and
##      zones are further divided into equal areas onto which flowers are overlaid
##Example Call: overlay("blue","triangle",3)
def overlay(color,shape,num):

    ##Zone 1
    z1_shape=(75,65)
    z1_in=((300,235),(375,235),(450,235),(525,235))
    z1_out=((375,300),(450,300),(525,300),(600,300))

    #Zone 2
    z2_shape=(45,35)
    z2_in=((105,200),(150,200),(60,235),(105,235))
    z2_out=((150,235),(195,235),(105,270),(150,270))

    ##Zone3
    z3_shape=(35,30)
    z3_in=((245,170),(280,170),(315,170),(350,170))
    z3_out=((280,200),(315,200),(350,200),(385,200))

    ##Zone4
    z4_shape=(35,45)
    z4_in=((500,180),(535,180),(570,180),(605,180))
    z4_out=((535,225),(570,225),(605,225),(640,225))
    

    if color == "red" and shape =="circle":
        flower= red_circle
    elif color == "red" and shape =="triangle":
        flower = red_triangle
    elif color == "red" and shape =="square":
        flower = red_square
    elif color == "green" and shape =="circle":
        flower = green_circle
    elif color == "green" and shape =="triangle":
        flower = green_triangle
    elif color == "green" and shape =="square":
        flower = green_square
    elif color == "blue" and shape =="circle":
        flower = blue_circle
    elif color == "blue" and shape =="triangle":
        flower = blue_triangle
    elif color == "blue" and shape =="square":
        flower = blue_square

    if PZ==1:
        flower = cv2.resize(flower,z1_shape)
        z_in=z1_in
        z_out=z1_out
    elif PZ==2:
        flower = cv2.resize(flower,z2_shape)
        z_in=z2_in
        z_out=z2_out
    elif PZ==3:
        flower = cv2.resize(flower,z3_shape)
        z_in=z3_in
        z_out=z3_out
    elif PZ==4:
        flower = cv2.resize(flower,z4_shape)
        z_in=z4_in
        z_out=z4_out
        
    
    for i in range(0,num):
        roi=plantation[z_in[i][1]:z_out[i][1],z_in[i][0]:z_out[i][0]]
        dst = blend_transparent(roi, flower)
        plantation[z_in[i][1]:z_out[i][1],z_in[i][0]:z_out[i][0]]=dst

    cv2.imshow("Plantation",plantation)
    return
    

      
#exit: Set to 1 to signify end of run
exit=0

##state: States the direction motor is supposed to turn thus deciding movement of bot. Expected value: 0-12
state=0

##angle_prev: saves previous value of angle which would be compared to lines in newer pictures to decide if path is straight or 90 degree turns
angle_prev=0 

# csv file name
filename = "Input Table.csv"
# initializing the titles and rows list
fields = []
rows = []

# reading csv file
with open(filename,'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)
    
    # extracting field names through first row
    fields = csvreader.next()

    # extracting each data row one by one
    for row in csvreader:
        rows.append(row)

##variable for combinations of colours and shapes
red_circle=cv2.imread(rows[0][2],-1)
red_triangle=cv2.imread(rows[1][2],-1)
red_square=cv2.imread(rows[2][2],-1)
green_circle=cv2.imread(rows[3][2],-1)
green_triangle=cv2.imread(rows[4][2],-1)
green_square=cv2.imread(rows[5][2],-1)
blue_circle=cv2.imread(rows[6][2],-1)
blue_triangle=cv2.imread(rows[7][2],-1)
blue_square=cv2.imread(rows[8][2],-1)
        


##to slow down bot in turns and make it faster on straight. It is continuously decremented in straight lines and set to 10 at curves and 20 near PZs
slow =0

#plantation: contains plantation pic
plantation= cv2.imread("Plantation.png")
cv2.imshow("Plantation",plantation)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

#red,green,blue GPIO pins
green =18
red = 16
blue = 22

##SETTING UP PICAM MODULE
cam = PiCamera()
cam.resolution = (160,128)
cam.framerate = 50

#frame: contains continuous frames from picam
frame= PiRGBArray(cam,(160,128))

#repeat: set to 1 when PZ has been detected, so as to not detect the same PZ twice. At repeat =0, detects first PZ it sees. Expected value: 0-1
repeat =0

#led: set to 1 when PZ processed and LED lighted and then set to 0 when done
led=0

#PZ: Count number of PZs detected till that point. Expected value: 0-5
PZ=0

#PZ_list: Contains list of colours at each PZ
PZ_list=[] 

#for erosion and dilation operations
kernel=np.ones((5,5),np.uint8)

perp_size=0 #perp_size: Contains distance between perpendicular lines in image which appear during right turns and plantations
par_size=0 #par_size: Contains distance between parallel lines i.e lines which indicate our current path
perp_l=[] #perp_l: Contains left side coordinates of perpendicular lines
perp_r=[] #perp_r: Contains right side coordinates of perpendicular lines

cam_thread= threading.Thread(target=camera) #Define camera thread
motor_thread= threading.Thread(target=motor) #Define motor thread
cam_thread.start()  ##Start camera thread
motor_thread.start() ##Start Motor thread


time.sleep(2) #Waits for camera to warm up

    
while not exit:
    img = frame.array #Read from camera thread
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    
    ##Removing grid lines from the image
    closing = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    blur= cv2.GaussianBlur(closing,(3,3),1)
    canny= cv2.Canny(blur,30,150)

    ##FOR CORDS CHECKING PURPOSES WHEN MAX-MIN THET>90
    blur= cv2.medianBlur(gray,5)
    erosion = cv2.erode(blur,kernel,iterations = 2)

    ##Finding contours in the resultant image
    image, contours, hierarchy = cv2.findContours(canny,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    ##Creating new list to store only path contours
    mod_contour=[]

    ##Creating black image to print edited contours, bounding rect and hough lines
    mask= np.zeros(img.shape,np.uint8)

    ##Getting extreme points
    H,W= image.shape
    cord_x1=W #cord_x1: contains x coordinate of one side of bounding rect
    cord_x2=0 #cord_x2: contains x coordinate of other side of bounding rect
    cord_y1=0 #cord_y1: contains y coordinate of one side of bounding rect
    cord_y2=H #cord_y2: contains y coordinate of other side of bounding rect

    #GETTING THE BOUNDING RECT WHICH ENCAPSULATES ALL CONTOURS
    for line in contours:
        if (cv2.arcLength(line,False))>120:
            x,y,w,h= cv2.boundingRect(line)
            if x<cord_x1:
                cord_x1=x
            if (x+w)>cord_x2:
                cord_x2=x+w
            if (y+h)>cord_y1:
                cord_y1= y+h
            if y<cord_y2:
                cord_y2=y
            mod_contour.append(line)

    ##Converting image to gray and finding houghlines
    mask = cv2.drawContours(mask, mod_contour,-1, (255,255,255), 2)
    mask=cv2.cvtColor(mask,cv2.COLOR_BGR2GRAY)
    lines= cv2.HoughLines(mask,1,np.pi/180,50)
    mask=cv2.cvtColor(mask,cv2.COLOR_GRAY2BGR)

    
    angle=0 #angle: contains average angle of houghlines detected and gives an estimate to turn left or right Expected value: -90 to 90
    perp_angle=0 #perp_angle: stores angle of perpendicular lines so that bot can rotate and detect PZs on curves properly
    
    ##Parallel hough lines indicate our main path or original path
    par_l=[] #stores bottom coords of parallel lines
    par_r=[] #stores top coords of parallel lines
    
    if lines is not None:
        max_thet=-360 #calculating max difference between angles of hough lines
        min_thet=360
        angle=0
        for i in range(0,len(lines)):
            for rho,theta in lines[i]:
                a=np.cos(theta)
                b=np.sin(theta)
                x0= a*rho
                y0= b*rho
                x1= int(x0+1000*(-b))
                y1= int(y0+1000*(a))
                x2= int(x0-1000*(-b))
                y2= int(y0-1000*(a))
                       
                cv2.line(mask,(x1,y1),(x2,y2),(0,255,0),2)

                cord=cords(x1,y1,x2,y2)
                par_l.append(cord[0])
                par_r.append(cord[1])
                
                theta= theta*180/np.pi
                if theta>90 and theta<180: #bringing angles to range of -90 to 90
                    theta= theta-180
                
                if min_thet>theta:
                    min_thet=theta

                if max_thet<theta:
                    max_thet=theta
                    
                angle += theta

        angle = angle/len(lines)


    mask= cv2.rectangle(mask,(cord_x1,cord_y1),(cord_x2,cord_y2),(0,0,255),1)
    wid= abs(cord_x1-cord_x2) ##wid:width of boundary rect Expected value: 0 to 159
    mean = (cord_x1+cord_x2)/2 ## mean: mid of boundary rect Expected value: 0 to 159
    angle_range= max_thet-min_thet ##angle_range: max range of angles Expected value: 0 to 180


    ##CHECKING FOR RIGHT TURN/LEFT TURN/PATCH
    if len(mod_contour)>0:
        ##check picture for 90 degree turns
        if angle_range>=80:
            slow = 10##takes 10 iterations of straight line to go to faster speed
            if lines is not None:
                par_l=[] #redefining list to categorise hough lines into parallel and perpendicular lines
                par_r=[]
                
                perp_l=[] #to store left coordinates of perpendicular hough lines
                perp_r=[]

                perp_ang=0 #initialise perp_ang
                ang=0 #to calculate average of parallel hough line angles
                
                for i in range(0,len(lines)):
                    for rho,theta in lines[i]:
                        a=np.cos(theta)
                        b=np.sin(theta)
                        x0= a*rho
                        y0= b*rho
                        x1= int(x0+1000*(-b))
                        y1= int(y0+1000*(a))
                        x2= int(x0-1000*(-b))
                        y2= int(y0-1000*(a))

                        cord=cords(x1,y1,x2,y2)
                        theta= theta*180/np.pi
                        if theta>90 and theta<180:
                            theta= theta-180
                        
                        if abs(theta-angle_prev)<45: #checks hough lines to see if it belongs to current path or incoming right turn path
                            par_l.append(cord[0]) ##(y,x)
                            par_r.append(cord[1]) ##(y,x)
                            ang+=theta
                            cv2.line(mask,(x1,y1),(x2,y2),(255,0,0),2)
                            
                        else:
                            perp_ang+=theta
                            perp_l.append(cord[0]) ##(y,x)
                            perp_r.append(cord[1]) ##(y,x)
                            cv2.line(mask,(x1,y1),(x2,y2),(0,0,255),2)


            ##CALCULATING PAR ANGLE TO FOLLOW
            if len(par_l)>0:    
                angle=ang/len(par_l)
                angle_prev=angle
            else:
                angle= angle_prev
                
            if len(perp_l)>0:
                perp_angle=perp_ang/len(par_l)

            
            ##Removing excess hough lines
            if len(par_l)>1:
                i=0
                while i<len(par_l):
                    j=i+1
                    while j<len(par_l):
                        if (dist(par_l[i],par_l[j])<=15) or (dist(par_r[i],par_r[j])<=15):
                            del par_l[j]
                            del par_r[j]
                            j=j-1

                        j+=1
                    i+=1

            
            if len(perp_l)>1:
                i=0
                while i<len(perp_l):
                    j=i+1
                    while j<len(perp_l):
                        if (dist(perp_l[i],perp_l[j])<=10) or(dist(perp_r[i],perp_r[j])<=10):
                            del perp_l[j]
                            del perp_r[j]
                            j=j-1
                        j+=1
                    i+=1

            ##Calculating max width between parallel lines and between perpendicular lines
            perp_size=0
            par_size=0

            # We consider the first two hough lines in each list as they go through the highest number of points
            if len(perp_l)>=2:
                perp_size= dist(perp_l[0],perp_l[1])

            if len(par_l)>2:
                par_size= dist(par_l[0],par_l[1])
                

            ##FINDING MIDPOINTS of houghlines
            if len(perp_l)==1:
                perp_mid_l=(perp_l[0][1],perp_l[0][0])  ##(x,y)format perp_mid_l: contains the left midpoint detected between perpendicular houghlines
                perp_mid_r=(perp_r[0][1],perp_r[0][0])  ##(x,y) format perp_mid_r: contains the right midpoint detected between perpendicular houghlines
            elif len(perp_l)>1:
                perp_mid_l=((perp_l[0][1]+perp_l[1][1])/2,(perp_l[0][0]+perp_l[1][0])/2) ##(x,y)
                perp_mid_r=((perp_r[0][1]+perp_r[1][1])/2,(perp_r[0][0]+perp_r[1][0])/2) ##(x,y)
             

            if len(par_l)>=2:
                par_mid_l=((par_l[0][1]+par_l[1][1])/2,(par_l[0][0]+par_l[1][0])/2) ##(x,y)
                par_mid_r=((par_r[0][1]+par_r[1][1])/2,(par_r[0][0]+par_r[1][0])/2) ##(x,y)
            elif len(par_l)==1:
                par_mid_l=(par_l[0][1],par_l[0][0]) ##(x,y)
                par_mid_r=(par_r[0][1],par_r[0][0]) ##(x,y)



##            ##DRAW THE MIDLINES BETWEEN HOUGHLINES ALONG WHICH COLOURS CHECKED
##            cv2.line(mask,par_mid_l,par_mid_r,(0,255,0),2)
##            cv2.line(mask,perp_mid_l,perp_mid_r,(0,255,0),2)

            ##GET THE COLOUR VALUES AT THOSE POINTS
            ##We use erosion so that in cases of only 1 hough line we can still detect black
            val_l= erosion[perp_mid_l[1],perp_mid_l[0]]  ##erosion[y,x] val_l: contains colour value at the left perpendicular coordinate. Expected value: 10 to 130
            val_r= erosion[perp_mid_r[1],perp_mid_r[0]]  ##erosion[y,x] val_r: contains colour value at the right perpendicular coordinate. Expected value: 10 to 130


            if perp_size>= 35: #and perp_size<62: ##Slows down bot if PZ detected closeby
                slow=20
                if PZ==5 and repeat==0:
                    exit=1
                
            if len(par_l)>0 and len(perp_l)>0:
                if (perp_l[0][0]>50 or perp_r[0][0]>50):
                    #val_b= erosion[par_mid_l[1],par_mid_l[0]]  ##erosion[y,x] ##val_b: contains colour value at the bottom parallel coordinate. Expected value: 10 to 130
                    val_t= erosion[par_mid_r[1],par_mid_r[0]]  ##erosion[y,x] ##val_t: contains colour value at the top parallel coordinate. Expected value: 10 to 130
                    print "val_t=",val_t
                    if val_t>50 and slow <=10:#checks the top of the parallel lines. White in case of 90 degree turns, shed, inversal   
                        if abs(wid)>130 and (perp_size<=62) and (perp_size>=35): 
                            print "SHED" ##bounding rect has higher wid in case of shed
                            state =9
                        elif val_l<80 and val_r>80:##TURN LEFT
                            print "TURN LEFT VAL"
                            state=1
                        elif val_l>80 and val_r<80:##TURN RIGHT
                            print "TURN RIGHT VAL"
                            state=2
                        elif val_l>80 and val_r>80:
                            slow=20
                            if wid>60 and perp_size>35: #<60
                                print perp_mid_l,perp_mid_r
                                if ((perp_mid_l[1]+perp_mid_r[1])/2)>70 and repeat==0 and 40< mean < 120 and 70<abs(perp_angle)<100:
                                    state=10
                                    print "PLANTATION ZONE"
                                    PZ+=1
                                    time.sleep(1)
                                    take_pic()
                                    time.sleep(0.5)
                                    repeat=1
                                elif ((perp_mid_l[1]+perp_mid_r[1])/2)>50 and repeat==0 and 40<mean<120 and ((abs(perp_angle)<70 or abs(perp_angle)>100)):
                                    state=10
                                    print "PLANTATION ZONE"
                                    PZ+=1
                                    time.sleep(1)
                                    take_pic()
                                    time.sleep(0.5)
                                    repeat=1
                                else:
                                    print "follow path"
                                    angle_range=0
                             
                        else: 
                            print "follow path" #in case of inversal we make it follow parallel path
                            angle_range=0 #by changing angle range it satisfies next if statement


                    else: #if top of parallel lines is black i.e PZ or zone right before shed
                        if val_l >80 and val_r>80:
                            slow=20

                        if wid>60 and perp_size>35: #<60
                            print perp_mid_l,perp_mid_r
                            if ((perp_mid_l[1]+perp_mid_r[1])/2)>70 and repeat==0 and 40<mean<120 and abs(perp_angle)>70:
                                state=10
                                print "PLANTATION ZONE"
                                PZ+=1
                                time.sleep(1)
                                take_pic()
                                time.sleep(0.5)
                                repeat=1
                            elif ((perp_mid_l[1]+perp_mid_r[1])/2)>50 and repeat==0 and 40<mean<120 and abs(perp_angle)<70:
                                state=10
                                print "PLANTATION ZONE"
                                PZ+=1
                                time.sleep(1)
                                take_pic()
                                time.sleep(0.5)
                                repeat=1
                                
                            else:
                                print "follow path"
                                angle_range=0


                elif len(par_l)==0:
                    if abs(wid)>130 and (perp_size<=62) and (perp_size>=35):
                        print "SHED"
                        state =9
                        
                    elif abs(cord_y2-cord_y1)<60 and (cord_y1==127 or cord_y2==127) : ##???
                        if mean>90:
                            print "TURN RIGHT MEAN"
                            state= 6

                        elif mean<70:
                            print "TURN LEFT MEAN"
                            state =5
        
        ##IF NO RIGHT ANGLE TURNS IN PIC
        if angle_range<80:
            if angle_range !=0:
                repeat=0

            ##GETTING UNIQUE PAR LINES
            if len(par_l)>1:
                i=0
                while i<len(par_l):
                    j=i+1
                    while j<len(par_l):
                        if (dist(par_l[i],par_l[j])<=12) or(dist(par_r[i],par_r[j])<=12):
                            del par_l[j]
                            del par_r[j]
                            j=j-1

                        j+=1
                    i+=1


            if len(par_l)>2: ##INVERSAL ......
                ##SELECT LINES WHICH ARE CLOSEST TO EACH OTHER as there are 3 contours in case of inversal
                l0= dist(par_l[0],par_l[1])*dist(par_l[0],par_l[2]) 
                l1= dist(par_l[1],par_l[0])*dist(par_l[1],par_l[2])
                l2= dist(par_l[2],par_l[0])*dist(par_l[2],par_l[1])

                if l0>l1 and l0>l2:
                    del par_l[0]
                    del par_r[0]
                elif l1>l0 and l1>l2:
                    del par_l[1]
                    del par_r[1]
                elif l2>l0 and l2>l1:
                    del par_l[2]
                    del par_r[2]
                    
                mean= (par_l[0][1]+par_l[1][1])/2 #changing mean and wid accordingly
                wid= abs(par_l[0][1]-par_l[1][1])
            
            
            angle_prev= angle ##Updating previous angle to check again in next iteration
            if wid>=95 or wid<=-95:##Following the gradient if boundary rectangle is wide
                slow=10
                if angle>10 and angle<45:
                    print "turn right"
                    state =2
                elif angle<-10 and angle>-45:
                    print "turn left"
                    state =1
                elif -10<=angle<=10:
                    slow= slow-1
                    ##to bring the bot to middle of the path
                    if mean>90:
                        print "go right then left"
                        state=12
                    elif mean<70:
                        print "go left then right"
                        state=11
                    else:
                        print "go straight"
                        state =0
                        
                elif angle>=45:
                    print "turn sharp right"
                    state =5
                    
                elif angle<=-45:
                    print "turn sharp left"
                    state =6

            else: #if boundary rect is less than 95
                
                if (cord_y2+cord_y1)/2<50: #if the path diverses too much to be captured in camera
                    print "go straight a bit"
                    state=0
                elif mean > 100:
                    slow=10
                    print "turn right"
                    state =2
                elif mean < 60:
                    slow=10
                    print "turn left"
                    state =1

                else:
                    slow=slow-1
                    if slow ==0:
                        if mean>90:
                            print "go right then left"
                            state=12
                        elif mean<70:
                            print "go left then right"
                            state=11
                        else:
                            print "go straight"
                        state =0
                    else:
                        print "go straight"
                        state=0

            if (cord_y1+cord_y2)/2>80: #redundancy just in case where camera detects too late
                if (cord_x1+cord_x2)/2>100:
                    print "SHARP RIGHT"
                    state=5
                if (cord_x1+cord_x2)/2<60:
                    print "SHARP LEFT"
                    state=6
                    

            
    else: ##IF NO. OF CONTOURS=0 i.e UNDETECTED
        print "stop and check"
        state =4


    k= cv2.waitKey(1)
        
    if k ==27: ##Press escape to stop bot just in case of reset
        exit=1
        break
    
 
if len(PZ_list)>0:
    blink_list(PZ_list)
    
GPIO.cleanup()
print "Ending...."
cv2.waitKey(0)
cv2.destroyAllWindows()
