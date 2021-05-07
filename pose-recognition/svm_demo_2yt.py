import cv2
import argparse
import pickle
from sklearn.preprocessing import LabelEncoder
import yoga_pose as yoga

import numpy as np # for argmax

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--features", required=True,
	help="path to input serialized db of pose features")
ap.add_argument("-c", "--classifier", required=True,
	help="path to model trained to recognize poses")
ap.add_argument("-l", "--le", required=True,
	help="path to label encoder")

args = vars(ap.parse_args())

# load the pose features
print("[INFO] loading pose features...")
data = pickle.loads(open(args["features"], "rb").read())

# load the actual face recognition model along with the label encoder
clf = pickle.loads(open(args["classifier"], "rb").read())
le = pickle.loads(open(args["le"], "rb").read())

# Authentication for YT stream
yt_key_f=open("youtube.key")
AUTH=yt_key_f.read().strip()
print(AUTH)
rtmpUrl = "rtmp://a.rtmp.youtube.com/live2/x/"+AUTH+" app=live2"
#rtmpUrl = "rtmp://a.rtmp.youtube.com/live2/x/"+AUTH

print(rtmpUrl)
#gst_str_rtp = "appsrc ! videoconvert ! 'video/x-raw, width=1280, height=720, framerate=25/1' ! queue ! x264enc bitrate=2000 byte-stream=false key-int-max=60 bframes=0 aud=true tune=zerolatency ! \"video/x-h264,profile=main\" ! flvmux streamable=true name=mux ! rtmpsink location=\""+rtmpUrl+"\"\n audiotestsrc ! volume volume=0 ! level ! voaacenc bitrate=128000 ! mux. "
#gst_str_rtp = "appsrc ! videoconvert ! x264enc bitrate=2000 byte-stream=false key-int-max=60 bframes=0 aud=true tune=zerolatency ! \"video/x-h264,profile=main\" ! flvmux streamable=true name=mux ! rtmpsink location=\""+rtmpUrl+"\"\n audiotestsrc ! volume volume=0 ! level ! voaacenc bitrate=128000 ! mux. "
gst_str_rtp = "appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! flvmux streamable=true name=mux ! rtmpsink location=\""+rtmpUrl+"\" audiotestsrc ! volume volume=0 ! level !voaacenc bitrate=128000 ! mux."

width=224
height=224
dim = (width, height)
fps = 21.

print(gst_str_rtp)
fps = 21.
print("[INFO] setting up out...")
out = cv2.VideoWriter(gst_str_rtp, 0, fps, (width, height), True)


# main execution loop
def execute(change):
    image = change['new']
    data = yoga.preprocess(image)
    cmap, paf = yoga.model_trt(data)
    cmap, paf = cmap.detach().cpu(), paf.detach().cpu()
    counts, objects, peaks = yoga.parse_objects(cmap, paf) #, cmap_threshold=0.15, link_threshold=0.15)
    yoga.draw_objects(image, counts, objects, peaks)
    sample = [0.0]*len(yoga.BONES)
    yoga.extract_angles(image, counts, objects, peaks, sample)

    preds = clf.predict_proba([sample])[0]
    z = np.argmax(preds)
    proba = preds[z]
    predicted_pose = le.classes_[z]

    text = "{:.2f}%: {}".format(proba * 100, predicted_pose)

    if proba >= 0.6 or predicted_pose != "unknown":
        cv2.putText(image, text, (0,20),
		    		cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv2.imshow('ouput', image)
    out.write(image)
    
print("[INFO] starting video stream...")
cam=cv2.VideoCapture(yoga.CAMSET)
while True:
    _, frame = cam.read()
    execute({'new': frame})
        
    if cv2.waitKey(1) == ord('q'):
        break

print("[INFO] freeing resources...")
cam.release() # free the camera
#out.release()
cv2.destroyAllWindows()
