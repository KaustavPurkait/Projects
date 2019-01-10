import numpy as np
import cv2
import time
import csv
import Adafruit_CharLCD as LCD
import Adafruit_GPIO.SPI as SPI
import MAX6675.MAX6675 as MAX6675
import Adafruit_MCP3008
import RPi.GPIO as GPIO


# Raspberry Pi pin configuration:
lcd_rs        = 25  # Note this might need to be changed to 21 for older revision Pi's.
lcd_en        = 24
lcd_d4        = 23
lcd_d5        = 17
lcd_d6        = 12
lcd_d7        = 22
lcd_backlight = 2

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows    = 2

# Initialize the LCD using the pins above.
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)


# Define a function to convert celsius to fahrenheit.
def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0
# Raspberry Pi hardware SPI configuration.
SPI_PORT   = 0
SPI_DEVICE = 0
sensor = MAX6675.MAX6675(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

#Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 1
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

templist=[]
moislist=[]
moiscount= 0
phlist=[]
phcount=0

lcd.message('Kindly put sensors into recent soil')
time.sleep(5)
lcd.clear()
lcd.message('Measuring temp, ph and moisture')
time.sleep(2)
lcd.clear()
lcd.message('Please wait for 10 sec......')

for i in range(10):
    temp = sensor.readTempC()
    templist.append(temp)
    
    mois = mcp.read_adc(1)
    if mois!=0:
        mois=100-((mois-300)/7.23)
        moislist.append(mois)
        moiscount=moiscount+1
    
    ph = mcp.read_adc(0)
    if ph!=0:
        ph=float(ph-210)/64
        phlist.append(ph)
        phcount=phcount+1

    time.sleep(1)

temp=sum(templist)/10
mois=sum(moislist)/moiscount
ph=sum(phlist)/phcount

lcd.clear()
lcd.message('moist temp  ph \n')
lcd.message('%.1f '% mois)
lcd.message('  %.1f C' % temp)
lcd.message(' %.1f ' % ph)
time.sleep(5)

lcd.clear()
lcd.message('Kindly standby for PK sensing')

lcd.message('Please place the sample in the slot in 10 secs')
time.sleep(1)



# Initialize camera
cap = cv2.VideoCapture(0)
time.sleep(4)

avglist=[]
t1=time.time()

ret,frame= cap.read()
print(frame.shape)

while(1):
    
    ## Read the image
    ret, frame = cap.read()
    img=frame[90:250,350:550,:]
    #im= img.copy()

    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    hue=hsv[:,:,0]
    sat= hsv[:,:,1]
    val= hsv[:,:,2]

    H,W,C=img.shape

    cnt=0
    tot=0

    for i in range(H):
        for j in range(W):
            if val[i,j]>0:
                cnt=cnt+1
                tot=tot+val[i,j]


    avg=0
    if cnt !=0:
        avg= round((float(tot)/cnt),2)
        
    print (avg)
    avglist.append(avg)
    #cv2.imshow('frame',frame)
    #cv2.imshow("img",img)

    #cv2.imshow('frame',frame)
    #cv2.imshow("img",img)
    t2=time.time()
    if t2-t1>600:
        break

    time.sleep(1)  ## 27 - ASCII for escape key
    #cv2.waitKey(1000)

cap.release()
cv2.destroyAllWindows()



##Analysing avglist to determine NPK

##Get starting value of graph (point where it crosses 10)
for i in range(3,len(avglist)):
    if avglist[i-2]*avglist[i-1]*avglist[i]*avglist[i+1]*avglist[i+2] :
        start=i
        break

p=0
k=0
start_grad= (avglist[i+30]-avglist[i+10])/float(20)
end_grad = (avglist[len(avglist)-101]-avglist[len(avglist)-1])/float(100)

if avglist[len(avglist)-1]>140:
    p=p+2
    k=k+2

if abs(start_grad-end_grad)> 0.2:
   p=p+1
elif abs(start_grad - end_grad)> 0.08:
    k=k+1
elif abs(start_grad- end_grad)<0.08 and avglist[len(avglist)-1]>25:
    p=p+1
    k=k+1
else :
    p=0
    k=0


##hichki

for i in range(20,len(avglist)-3):
    if avglist[i+1]<avglist[i] and avglist[i+2]<avglist[i+1] and avglist[i+3]<avglist[i+2]:
        p=p+1
        break

if p==1 or p==2:
    print ("high P")
    phos="high"
if k==1:
    print ("high K")
    pot="high"

if p>=3:
    print ("very high P")
    phos="high"

if k>1:
    print("very high K")
    pot="high"

if k==0:
    print ("low K")
    pot="low"

if p==0:
    print ("low P")
    phos="low"


#compare value with database
fields=[]
rows=[]
with open("ecr.csv",'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)
    
    # extracting field names through first row
    #fields.append(csvreader.next())

    # extracting each data row one by one
    for row in csvreader:
        rows.append(row)

phos= "high"
pot= "low"
for row in rows:
    if phos==row[4] and pot==row[5] :
        print (row[0])

csvfile.close()
