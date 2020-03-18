from scipy.spatial import distance as dist
from imutils.video import VideoStream
import numpy as np
import cv2
import imutils
import time
import urllib.request

#red 192.168.43.120
redforward = 'http://192.168.43.85/car?a=2'
redbackward = 'http://192.168.43.85/car?a=4'
redstop = 'http://192.168.43.85/car?a=5'
redright = 'http://192.168.43.85/car?a=1'
redleft = 'http://192.168.43.85/car?a=3'
redultrasonic = 'http://192.168.43.85/car?a=6'

#yellow 192.168.43.132
yellowforward = 'http://192.168.43.132/car?a=2'
yellowbackward = 'http://192.168.43.132/car?a=4'
yellowstop = 'http://192.168.43.132/car?a=5'
yellowright = 'http://192.168.43.132/car?a=1'
yellowleft = 'http://192.168.43.132/car?a=3'
yellowultrasonic = 'http://192.168.43.132/car?a=6'

#green 192.168.43.133
greenforward = 'http://192.168.43.133/car?a=2'
greenbackward = 'http://192.168.43.133/car?a=4'
greenstop = 'http://192.168.43.133/car?a=5'
greenright = 'http://192.168.43.133/car?a=1'
greenleft = 'http://192.168.43.133/car?a=3'
greenultrasonic = 'http://192.168.43.133/car?a=6'

#blue 192.168.43.85
blueforward = 'http://192.168.43.85/car?a=2'
bluebackward = 'http://192.168.43.85/car?a=4'
bluestop = 'http://192.168.43.85/car?a=5'
blueright = 'http://192.168.43.85/car?a=1'
blueleft = 'http://192.168.43.85/car?a=3'
blueultrasonic = 'http://192.168.43.85/car?a=6'

print("Requesting ipcam url")
url='http://192.168.0.101:8080/shot.jpg'
print("Request granted")

#defining object color
#blue
BlueLower = np.array([90,60,0])
BlueUpper =np.array([121,255,255])
#red
RedLower = np.array([170,120,70])
RedUpper =np.array([180,255,255])

#Yellow
yellowLower = np.array([20, 100, 100])
yellowUpper = np.array([30, 255, 255])

#Green
greenLower = np.array([65,60,60])
greenUpper = np.array([80,255,255])

#list of tracked points
Bluepts = []
Redpts = []
Yellowpts = []
Greenpts = []


img1 = np.zeros((512,512,3),np.uint8)
filename = 'map.jpg'

print("Starting camera")
vs= cv2.VideoCapture(0)

#define the codec for saving video
fourcc = cv2.VideoWriter_fourcc(*'X264')
out = cv2.VideoWriter('output1.mp4',fourcc,20.0,(640,480))


#time.sleep(2.0)

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

    urllib.request.urlopen(greenultrasonic)
    urllib.request.urlopen(yellowultrasonic)
    urllib.request.urlopen(redultrasonic)
    urllib.request.urlopen(blueultrasonic)

    #creating mask
    #blue
    Bluemask = cv2.inRange(hsv,BlueLower, BlueUpper)
    Bluemask = cv2.erode(Bluemask,None,iterations=2)
    Bluemask = cv2.dilate(Bluemask,None,iterations = 2)

    #red
    Redmask = cv2.inRange(hsv,RedLower, RedUpper)
    Redmask = cv2.erode(Redmask,None,iterations=2)
    Redmask = cv2.dilate(Redmask,None,iterations = 2)

    #Yellow
    Yellowmask = cv2.inRange(hsv,yellowLower, yellowUpper)
    Yellowmask = cv2.erode(Yellowmask,None,iterations=2)
    Yellowmask = cv2.dilate(Yellowmask,None,iterations = 2)

    #green
    Greenmask = cv2.inRange(hsv,greenLower, greenUpper)
    Greenmask = cv2.erode(Greenmask,None,iterations=2)
    Greenmask = cv2.dilate(Greenmask,None,iterations = 2)

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
    #yellow
    Yellowcnts = cv2.findContours(Yellowmask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    Yellowcnts = imutils.grab_contours(Yellowcnts)
    #green
    Greencnts = cv2.findContours(Greenmask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    Greencnts = imutils.grab_contours(Greencnts)

    #loop over contours
    #blue contours
    if len(Bluecnts) > 0:
        
        for bc in Bluecnts:
            if cv2.contourArea(bc) <1000:
                continue
            
            #the centroid points
            M = cv2.moments(bc)
            cbx = int(M['m10'] / M['m00'])
            cby = int(M['m01'] / M['m00'])
            Bluecenter = cbx,cby
            #print(cx,cy)
        
            #cv2.drawContours(frame, cnts,-1,(0,255,0),2)
            cv2.circle(frame, (cbx,cby), 7,(255,255,255),-1)
            cv2.putText(frame,"centre",(cbx-20,cby-20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2)
            bx,by,bw,bh = cv2.boundingRect(bc)
            
            cv2.rectangle(frame,(bx,by),(bx+bw,by+bh),(0,255,0),2)

            #Blue adding points
            Bluepts.append(Bluecenter)
            
            for bi in range(1, len(Bluepts)):
                if Bluepts[bi-1] is None or Bluepts[bi] is None:
                    continue
                
                cv2.line(frame,Bluepts[bi-1],Bluepts[bi],(255,0,0),1)

    
    #red contours
    if len(Redcnts) > 0:
        
        for rc in Redcnts:
            if cv2.contourArea(rc) <1000:
                continue
            
            #the centroid points
            M = cv2.moments(rc)
            crx = int(M['m10'] / M['m00'])
            cry = int(M['m01'] / M['m00'])
            Redcenter = crx,cry
            #print(cx,cy)
        
            #cv2.drawContours(frame, cnts,-1,(0,255,0),2)
            cv2.circle(frame, (crx,cry), 7,(255,255,255),-1)
            cv2.putText(frame,"centre",(crx-20,cry-20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2)
            rx,ry,rw,rh = cv2.boundingRect(rc)
            cv2.rectangle(frame,(rx,ry),(rx+rw,ry+rh),(0,255,0),2)

            #Red adding points
            Redpts.append(Redcenter)
            for ri in range(1, len(Redpts)):
                if Redpts[ri-1] is None or Redpts[ri] is None:
                    continue

                cv2.line(frame,Redpts[ri-1],Redpts[ri],(0,0,255),1)

    #yellow contours
    if len(Yellowcnts) > 0:
        
        for yc in Yellowcnts:
            if cv2.contourArea(yc) <1000:
                continue
            
            #the centroid points
            M = cv2.moments(yc)
            cyx = int(M['m10'] / M['m00'])
            cyy = int(M['m01'] / M['m00'])
            Yellowcenter = cyx,cyy
            #print(cx,cy)
        
            #cv2.drawContours(frame, cnts,-1,(0,255,0),2)
            cv2.circle(frame, (cyx,cyy), 7,(255,255,255),-1)
            cv2.putText(frame,"centre",(cyx-20,cyy-20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2)
            yx,yy,yw,yh = cv2.boundingRect(yc)
            cv2.rectangle(frame,(yx,yy),(yx+yw,yy+yh),(0,255,0),2)

            #Yellow adding points
            Yellowpts.append(Yellowcenter)
            for yi in range(1, len(Yellowpts)):
                if Yellowpts[yi-1] is None or Yellowpts[yi] is None:
                    continue

                cv2.line(frame,Yellowpts[yi-1],Yellowpts[yi],(0,255,255),1)
                

    #green contours
    if len(Greencnts) > 0:
        
        for gc in Greencnts:
            if cv2.contourArea(gc) <1000:
                continue
            
            #the centroid points
            M = cv2.moments(gc)
            cgx = int(M['m10'] / M['m00'])
            cgy = int(M['m01'] / M['m00'])
            Greencenter = cgx,cgy
            #print(cx,cy)
        
            #cv2.drawContours(frame, cnts,-1,(0,255,0),2)
            cv2.circle(frame, (cgx,cgy), 7,(255,255,255),-1)
            cv2.putText(frame,"centre",(cgx-20,cgy-20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2)
            gx,gy,gw,gh = cv2.boundingRect(gc)
            cv2.rectangle(frame,(gx,gy),(gx+gw,gy+gh),(0,255,0),2)

            #Green adding points
            Greenpts.append(Greencenter)
            for gi in range(1, len(Greenpts)):
                if Greenpts[gi-1] is None or Greenpts[gi] is None:
                    continue

                cv2.line(frame,Greenpts[gi-1],Greenpts[gi],(0,255,0),1)

            
    #eculidean distance between centre of blue and red
    #D = dist.euclidean((cbx,cby), (crx, cry))

    #if D<=100:
    #cv2.line(frame,(cbx,cby),(crx,cry),(255,0,0),2)


    out.write(frame)
    cv2.imwrite(filename,frame)

    cv2.imshow("Ipwebcam",frame)
    
    key = cv2.waitKey(1)
    if key == 27:
        break
    elif key == ord('q') or key == ord('Q'):
        urllib.request.urlopen(redstop)
        urllib.request.urlopen(greenstop)
        urllib.request.urlopen(bluestop)
        urllib.request.urlopen(yellowstop)
        time.sleep(20)
        

urllib.request.urlopen(redstop)
urllib.request.urlopen(greenstop)
urllib.request.urlopen(bluestop)
urllib.request.urlopen(yellowstop)
vs.release()
out.release()
cv2.destroyAllWindows()




            

    
