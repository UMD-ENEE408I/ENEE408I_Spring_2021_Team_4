import cv2
import argparse
from imutils import paths
from sklearn.preprocessing import LabelEncoder
import os
import pickle
import yoga_pose as yoga


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
    return sample, image
    

ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", required=True,
	help="path to output dir for images")
ap.add_argument("-i", "--input", required=True,
	help="path to input video file")
args = vars(ap.parse_args())

width=224
height=224
dim = (width, height)

print("[INFO] starting...")
vidPath = args["input"]
outPath = args["output"]


# initialize the total number of poses processed
total = 0

cap = cv2.VideoCapture(vidPath)

while(cap.isOpened()):
    _, img = cap.read()

    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    sample, image = execute({'new': resized})

    cv2.imshow('frame',image)
    key = cv2.waitKey(0) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("y"): # if the `y` key was pressed, add sample
        cv2.imwrite(f"{outPath}/{total}.jpg", img)
        total += 1

cap.release()
cv2.destroyAllWindows()