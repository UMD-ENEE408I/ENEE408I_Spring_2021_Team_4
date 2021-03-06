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


width=224
height=224
dim = (width, height)


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


    image = cv2.resize(image,(448,448),cv2.INTER_AREA)
    if proba >= 0.7 and predicted_pose != "unknown":
        cv2.putText(image, text, (10,40),
		    		cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.imshow('ouput', image)
    
print("[INFO] starting video stream...")
cam=cv2.VideoCapture(yoga.CAMSET)
while True:
    _, frame = cam.read()
    execute({'new': frame})
        
    if cv2.waitKey(1) == ord('q'):
        break

print("[INFO] freeing resources...")
cam.release() # free the camera
cv2.destroyAllWindows()
