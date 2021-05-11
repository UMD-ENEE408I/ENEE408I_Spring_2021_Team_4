import pkg_resources
import cv2
import argparse
import pickle
import pkg_resources
from sklearn.preprocessing import LabelEncoder
from .yoga_pose import *
import numpy as np # for argmax
import threading
import asyncio
from collections import deque
from .robot_chat_client import RobotChatClient

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

def test_callback(message_dict):
    if message_dict['type'] == 'pose':
        print('Value of field pose: {}'.format(message_dict['pose']))

class PoseRecognition:
    def __init__(self):
        #print("INIT")

        resource_package = __name__
        features_path = '/'.join(('output', 'features.pickle'))
        svm_classifier_path = '/'.join(('output', 'svm_classifier.pickle'))
        le_path = '/'.join(('output', 'le.pickle'))

        # load the pose features
        print("[INFO] loading pose features...")

        # load the actual face recognition model along with the label encoder
        self.clf = pickle.loads(pkg_resources.resource_stream(resource_package, svm_classifier_path).read())
        self.le = pickle.loads(pkg_resources.resource_stream(resource_package, le_path).read())

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

        self.client = RobotChatClient('ws://localhost:5001', callback=test_callback)

        self.width=224
        self.height=224
        self.dim = (self.width, self.height)
        self.out_width = self.width*2
        self.out_height = self.height*2

        queue_len = 50
        self.prev_thresh = int(queue_len*0.8)
        self.color = (0, 0, 255) # color for skeleton
        self.history = deque(maxlen=queue_len)
        self.prev = -1 # last identified pose index
        self.sent = False # whether identified pose has already been sent

        print(gst_str_rtp)
        print("[INFO] setting up out...")

        self.out = cv2.VideoWriter(gst_str_rtp, 0, 21.0, (self.out_width, self.out_height), True)

        #print("GET OR CREATE EVENT LOOP")    
        #self.event_loop=get_or_create_eventloop()
        #print("AFTER GET OR CREATE EVENT LOOP")    
        thread = threading.Thread(target=self.svm_demo)
        #thread.daemon=True
        thread.start()
        thread.join()

    def send_message(self, message):
        self.client.send({'type':'pose',
        'pose':message})

    # main execution loop
    def execute(self, change):
        image = change['new']
        data = preprocess(image)
        cmap, paf = model_trt(data)
        cmap, paf = cmap.detach().cpu(), paf.detach().cpu()
        counts, objects, peaks = parse_objects(cmap, paf) #, cmap_threshold=0.15, link_threshold=0.15)
        sample = [0.0]*len(BONES)
        extract_angles(image, counts, objects, peaks, sample)

        preds = self.clf.predict_proba([sample])[0]
        z = np.argmax(preds)
        proba = preds[z]
        predicted_pose = self.le.classes_[z]
        
        self.history.append(z)
        self.prev_count = self.history.count(self.prev)
        if self.prev_count < self.prev_thresh: # reset
            self.prev=-1
            self.color = (0,0,255)
            self.sent = False

        draw_objects(image, counts, objects, peaks, self.color)
        image = cv2.resize(image,(self.out_width,self.out_height),cv2.INTER_AREA)
        text = "{:.2f}%: {}".format(proba * 100, predicted_pose)
        if proba >= 0.7 and predicted_pose != "unknown":
            if self.prev != z and self.prev_count < self.prev_thresh:
                self.prev = z # set new prev
                self.sent = False
            elif self.prev == z and self.prev_count >= self.prev_thresh and not self.sent:
                self.color = (0,255,0)
                print("[INFO] Pose detected: "+ predicted_pose)
                self.send_message(predicted_pose)
                self.sent = True
            cv2.putText(image, text, (20,30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow('cam', image)
        self.out.write(image)
        


    def svm_demo(self):
        #asyncio.set_event_loop(event_loop)
           
        cam=cv2.VideoCapture(CAMSET)
        try:
            while True:
                _, frame = cam.read()
                self.execute({'new': frame})
                    
                if cv2.waitKey(1) == ord('q'):
                    break
        except Exception as e:
            print(e)
        print("[INFO] freeing resources...")
        cam.release() # free the camera
        self.out.release()
        cv2.destroyAllWindows()
