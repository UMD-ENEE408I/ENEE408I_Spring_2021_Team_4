# from pyimagesearch.com/2015/09/14/ball-tracking-with-opencv
# BE SURE TO INSTALL THE imutilts library with:
# $ pip3 install imutils

from collections import deque # list-like data structure with fast appends and pops
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils # this dude's opencv convenience functions
import time

width=800
height=600
flip=2

camSet=f"""nvarguscamerasrc sensor-id=0 
! video/x-raw(memory:NVMM), width=3264, height=2464, framerate=21/1, format=NV12 
! nvvidconv flip-method={str(flip)} 
! video/x-raw, width={str(width)}, height={str(height)}, format=BGRx 
! videoconvert 
! video/x-raw, format=BGR 
! appsink"""

# construct argument parse
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
# parse args
args = vars(ap.parse_args())

# define lower and upper boundaries of the "green"
# ball in the HSV volor space, then initialize the 
# list of tracked points

greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
pts = deque(maxlen=args["buffer"])

# if a video path was not supplied, grab reference
# to the webcam
if not args.get("video", False):
    vs=cv2.VideoCapture(camSet)
    #vs = VideoStream(src=0).start()

# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])
    
# allow the camera or video file to warm up
time.sleep(2.0)

while True:
    # grab current frame
    _, frame = vs.read()

    # handle the frame from VideoCapture or VideoStream
    #frame=frame[1] if args.get("video", False) else frame

    # if we are vieweing a video and we did not grab a frame,
    # then we have reached the end of the video
    if frame is None:
        break
    (w,h,c) = frame.shape
    # resize the frame, blur it, and convert to the HSV color space
    #frame = cv2.resize(frame, (600, h))
    blurred = cv2.GaussianBlur(frame,(11,11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    
    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        # only proceed if the radius meets a minimum size
        if radius > 10:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius),
                    (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
    # update the points queue
    pts.appendleft(center)
    
    # loop over the set of tracked points
    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore
	# them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
	
    # show the frame to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
    vs.stop()

# otherwise, release the camera
else:
    vs.release()

# close all windows
cv2.destroyAllWindows()
