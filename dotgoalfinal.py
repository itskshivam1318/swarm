from scipy.spatial import distance as dist
from imutils.video import VideoStream
import numpy as np
import cv2
import imutils
import time
import urllib.request


print("Requesting ipcam url")
url='http://192.168.43.113:8080/shot.jpg'

forward = 'http://192.168.43.85/car?a=2'
backward = 'http://192.168.43.85/car?a=4'
stop = 'http://192.168.43.85/car?a=5'
right = 'http://192.168.43.85/car?a=1'
left = 'http://192.168.43.85/car?a=3'
#url='http://192.168.43.78:8080/shot.jpg'
#target 
x1,y1 = -1, -1
Targetcenter = x1,y1
dot = False
def draw_circle(event,x,y,flags,param):
    global x1,y1
    if event == cv2.EVENT_LBUTTONDBLCLK:
        cv2.circle(frame,(x,y),10,(255,0,0),-1)
        x1,y1 =  x,y
        dot = True

#defining object color
#blue
BlueLower = np.array([90,60,0])
BlueUpper =np.array([121,255,255])

#red
#RedLower = np.array([155,25,0])
#RedUpper =np.array([185,255,255])
RedLower = np.array([170,120,70])
RedUpper =np.array([180,255,255])

vs= cv2.VideoCapture(0)

#define the codec for saving video
fourcc = cv2.VideoWriter_fourcc(*'X264')
out = cv2.VideoWriter('target.mp4',fourcc,20.0,(640,480))


time.sleep(2.0)

while True:

    imgResp=urllib.request.urlopen(url)
    imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
    frame=cv2.imdecode(imgNp,-1)
    
    #ret, frame =vs.read()

    # blurring to cancel the noice
    blurred = cv2.GaussianBlur(frame,(11,11),0)

    # convert to hsv
    hsv = cv2.cvtColor(blurred,cv2.COLOR_BGR2HSV)

    # show hsv frame
    #cv2.imshow("hsv",hsv)

    #creating mask
    #blue
    Bluemask = cv2.inRange(hsv,BlueLower, BlueUpper)
    Bluemask = cv2.erode(Bluemask,None,iterations=2)
    Bluemask = cv2.dilate(Bluemask,None,iterations = 2)
    #red
    Redmask = cv2.inRange(hsv,RedLower, RedUpper)
    Redmask = cv2.erode(Redmask,None,iterations=2)
    Redmask = cv2.dilate(Redmask,None,iterations = 2)

    '''
    #finding contours
    #Blue
    Bluecnts, hierarchy = cv2.findContours(Bluemask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    #red
    Redcnts, hierarchy = cv2.findContours(Redmask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
    #draw contours
    #blue
    cv2.drawContours(frame, Bluecnts,-1,(255,0,0),2)
    #red
    cv2.drawContours(frame, Redcnts,-1,(0,0,255),2)
    '''

    #Finding contours
    #Blue
    Bluecnts = cv2.findContours(Bluemask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    Bluecnts = imutils.grab_contours(Bluecnts)
    #red
    Redcnts = cv2.findContours(Redmask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    Redcnts = imutils.grab_contours(Redcnts)

    #loop over contours
    #blue contours
    if len(Bluecnts) > 0:
        
        for bc in Bluecnts:
            if cv2.contourArea(bc) <1000:
                continue
            
            #the centroid points
            M = cv2.moments(bc)
            x2 = int(M['m10'] / M['m00'])
            y2 = int(M['m01'] / M['m00'])
            Bluecenter = x2,y2
            #print(cx,cy)
        
            #cv2.drawContours(frame, cnts,-1,(0,255,0),2)
            cv2.circle(frame, (x2,y2), 7,(255,255,255),-1)
            cv2.putText(frame,"centre",(x2-20,y2-20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2)
            bx,by,bw,bh = cv2.boundingRect(bc)
            cv2.rectangle(frame,(bx,by),(bx+bw,by+bh),(0,255,0),2)
    
    #red contours
    if len(Redcnts) > 0:
        
        for rc in Redcnts:
            if cv2.contourArea(rc) <1000:
                continue
            
            #the centroid points
            M = cv2.moments(rc)
            x3 = int(M['m10'] / M['m00'])
            y3 = int(M['m01'] / M['m00'])
            Redcenter = x3,y3
            #print(cx,cy)
        
            #cv2.drawContours(frame, cnts,-1,(0,255,0),2)
            cv2.circle(frame, (x3,y3), 7,(255,255,255),-1)
            cv2.putText(frame,"centre",(x3-20,y3-20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2)
            rx,ry,rw,rh = cv2.boundingRect(rc)
            cv2.rectangle(frame,(rx,ry),(rx+rw,ry+rh),(0,255,0),2)

    #eculidean distance between centre of blue and red
    D = dist.euclidean((x2,y2),(x3, y3))

    #if D<=100:
    cv2.line(frame,(x2,y2),(x3,y3),(255,0,0),2)

    #drawing the dot
    cv2.setMouseCallback('frame',draw_circle)
    cv2.circle(frame,(x1,y1),10,(255,255,0),-1)

    #draw line between blue centre to dot
    cv2.line(frame,(x1,y1),(x2,y2),(255,255,255),2)

    #distance between goal and blue dot
    goaldist = dist.euclidean((x1, y1),(x2,y2))


    #find if facing towards target
    a = x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)
    
    print(a)
    if(a == 0 or a <= 100 and a >= -100):
        print("algined")
        if goaldist >=50:
            #movement code
            urllib.request.urlopen(forward)
            print('forward')
        else:
            print ('goal')
            urllib.request.urlopen(stop)
    elif(a<0):
        urllib.request.urlopen(left)
        print("left turn")
    else:
        urllib.request.urlopen(right)
        print("right turn")

    out.write(frame)
    #cv2.imwrite(filename,frame)
        
    cv2.imshow("frame",frame)
    key = cv2.waitKey(1)
    if key == 27:
        break
    elif key == ord('q') or key == ord('Q'):
        urllib.request.urlopen(stop)
        time.sleep(20)
        

urllib.request.urlopen(stop)
vs.release()
out.release()
cv2.destroyAllWindows()
