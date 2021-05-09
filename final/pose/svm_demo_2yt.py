import pkg_resources
import cv2
import argparse
import pickle
import pkg_resources
from sklearn.preprocessing import LabelEncoder
from .yoga_pose import *
import numpy as np # for argmax

resource_package = __name__
features_path = '/'.join(('output', 'features.pickle'))
svm_classifier_path = '/'.join(('output', 'svm_classifier.pickle'))
le_path = '/'.join(('output', 'le.pickle'))

# load the pose features
print("[INFO] loading pose features...")

# load the actual face recognition model along with the label encoder
clf = pickle.loads(pkg_resources.resource_stream(resource_package, svm_classifier_path).read())
le = pickle.loads(pkg_resources.resource_stream(resource_package, le_path).read())

# Authentication for YT stream
yt_key_f=pkg_resources.resource_string(resource_package, "youtube.key").decode("utf-8")
AUTH=yt_key_f.strip()
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

out_width = width*2
out_height = height*2

print(gst_str_rtp)
fps = 21.
print("[INFO] setting up out...")



# main execution loop
def execute(change):
    image = change['new']
    data = preprocess(image)
    cmap, paf = model_trt(data)
    cmap, paf = cmap.detach().cpu(), paf.detach().cpu()
    counts, objects, peaks = parse_objects(cmap, paf) #, cmap_threshold=0.15, link_threshold=0.15)
    draw_objects(image, counts, objects, peaks)
    sample = [0.0]*len(BONES)
    extract_angles(image, counts, objects, peaks, sample)

    preds = clf.predict_proba([sample])[0]
    z = np.argmax(preds)
    proba = preds[z]
    predicted_pose = le.classes_[z]

    image = cv2.resize(image,(out_width,out_height),cv2.INTER_AREA)
    text = "{:.2f}%: {}".format(proba * 100, predicted_pose)
    if proba >= 0.7 and predicted_pose != "unknown":
        cv2.putText(image, text, (0,20),
		    		cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.imshow('cam', image)
    return image


def svm_demo():
    out = cv2.VideoWriter(gst_str_rtp, 0, fps, (out_width, out_height), True)
    cam=cv2.VideoCapture(CAMSET)
    while True:
        _, frame = cam.read()
        image = execute({'new': frame})
        out.write(image)
        if cv2.waitKey(1) == ord('q'):
            break

    print("[INFO] freeing resources...")
    cam.release() # free the camera
    out.release()
    cv2.destroyAllWindows()
