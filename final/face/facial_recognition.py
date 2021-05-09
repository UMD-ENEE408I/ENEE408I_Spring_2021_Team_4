import pkg_resources
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import pickle
import time
import cv2
import os
import threading
import serial

# A class to continuously poll the VideoCapture
# object in order to make sure the gstreamer pipeline
# is always empty, this prevents large latencies of
# many seconds
class FrameGrabber(threading.Thread):
    def __init__(self, cam):
        threading.Thread.__init__(self)
        self._cam = cam
        self._frame = None
        self._stop_thread = False

    def run(self):
        while not self._stop_thread:
            _, self._frame = self._cam.read()
        self._cam.release()

    # If your program runs faster than the framerate of the
    # camera this will return duplicate frames
    def get_latest_frame(self):
        return self._frame

    def signal_stop(self):
        self._stop_thread = True

# For Raspberry Pi camera
width=600
height=450
flip=2
camSet=f"""nvarguscamerasrc sensor-id=0 
! video/x-raw(memory:NVMM), width=3264, height=2464, framerate=21/1, format=NV12 
! nvvidconv flip-method={str(flip)} 
! video/x-raw, width={str(width)}, height={str(height)}, format=BGRx 
! videoconvert 
! video/x-raw, format=BGR 
! appsink"""

resource_package = __name__
detector_path = 'face_detection_model'
embedding_model_path = 'openface_nn4.small2.v1.t7'
recognizer_path = '/'.join(('output', 'recognizer.pickle'))
le_path = '/'.join(('output', 'le.pickle'))
confidence_thresh = 0.5 

detector_filename = pkg_resources.resource_filename(resource_package, detector_path)
embedding_model_filename = pkg_resources.resource_filename(resource_package, embedding_model_path)

# load our serialized face detector from disk
print("[INFO] loading face detector...")
protoPath = os.path.sep.join([detector_filename, "deploy.prototxt"])
modelPath = os.path.sep.join([detector_filename,
	"res10_300x300_ssd_iter_140000.caffemodel"])
detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath)

# load our serialized face embedding model from disk
print("[INFO] loading face recognizer...")
embedder = cv2.dnn.readNetFromTorch(embedding_model_filename)

# load the actual face recognition model along with the label encoder
recognizer = pickle.loads(pkg_resources.resource_stream(resource_package, recognizer_path).read())
le = pickle.loads(pkg_resources.resource_stream(resource_package, le_path).read())

print("[INFO] setting up arduino...")
#arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1) # port, baudrate, timeout
turn_time = 0.2 # sec
stop_time = 1.0

def find_person(target):
	# check that target is in label encoder
	if target not in le.classes_:
		print("[ERROR] target person not in face label encoder")
		return
	
	# initialize the video stream, then allow the camera sensor to warm up
	print("[INFO] starting video stream...")
	vs=cv2.VideoCapture(camSet)
	frame_grabber = FrameGrabber(vs)
	frame_grabber.start()

	time.sleep(2.0)

	centered_thresh = 0.2 # parameter for centering bounds
	bound_r = int(600 * (.5 + centered_thresh))
	bound_l = int(600 * (.5 - centered_thresh))
	centered = False
	#print("BOUNDS: {} {}".format(bound_l, bound_r))

	# loop over frames from the video file stream
	while not centered:
		# grab the frame from the threaded video stream
		frame = frame_grabber.get_latest_frame()

		# resize the frame to have a width of 600 pixels (while
		# maintaining the aspect ratio), and then grab the image
		# dimensions
		#frame = imutils.resize(frame, width=600)
		(h, w) = frame.shape[:2]

		# construct a blob from the image
		imageBlob = cv2.dnn.blobFromImage(
			cv2.resize(frame, (300, 300)), 1.0, (300, 300),
			(104.0, 177.0, 123.0), swapRB=False, crop=False)

		# apply OpenCV's deep learning-based face detector to localize
		# faces in the input image
		detector.setInput(imageBlob)
		detections = detector.forward()

		detection = False # whether a face was detected this frame

		# loop over the detections
		for i in range(0, detections.shape[2]):
			# extract the confidence (i.e., probability) associated with
			# the prediction
			confidence = detections[0, 0, i, 2]

			# filter out weak detections
			if confidence > confidence_thresh:
				detection = True
				# compute the (x, y)-coordinates of the bounding box for
				# the face
				box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
				(startX, startY, endX, endY) = box.astype("int")

				# extract the face ROI
				face = frame[startY:endY, startX:endX]
				(fH, fW) = face.shape[:2]

				# ensure the face width and height are sufficiently large
				if fW < 20 or fH < 20:
					continue

				# construct a blob for the face ROI, then pass the blob
				# through our face embedding model to obtain the 128-d
				# quantification of the face
				faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,
					(96, 96), (0, 0, 0), swapRB=True, crop=False)
				embedder.setInput(faceBlob)
				vec = embedder.forward()

				# perform classification to recognize the face
				preds = recognizer.predict_proba(vec)[0]
				j = np.argmax(preds)
				proba = preds[j]
				name = le.classes_[j]

				midX = int((endX + startX) / 2)
				# draw the bounding box of the face along with the
				# associated probability
				text = "{}: {:.2f}%".format(name, proba * 100)
				y = startY - 10 if startY - 10 > 10 else startY + 10
				cv2.rectangle(frame, (startX, startY), (endX, endY),
					(0, 0, 255), 2)
				cv2.putText(frame, text, (startX, y),
					cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

				if name == target: # target found
					if midX >= bound_l and midX <= bound_r:
						centered = True
					elif midX < bound_l:
						# turn left
						#arduino.write(b'l')
						time.sleep(turn_time)
						#arduino.write(b's')
						time.sleep(stop_time)
					else:
						# turn right
						#arduino.write(b'r')
						time.sleep(turn_time)
						#arduino.write(b's')
						time.sleep(stop_time)
				
		# turn if no detection
		if not detection:
			#arduino.write(b'l')
			time.sleep(turn_time)
			#arduino.write(b's')
			time.sleep(stop_time) 

		# show the output frame
		cv2.imshow("cam", frame)
		key = cv2.waitKey(1) & 0xFF

		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break

	# do a bit of cleanup
	frame_grabber.signal_stop()
	frame_grabber.join()
	cv2.destroyAllWindows()
