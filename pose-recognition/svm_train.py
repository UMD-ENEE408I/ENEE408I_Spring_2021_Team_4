import cv2
import argparse
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn import svm

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--features", required=True,
	help="path to serialized db of sample pose features")
ap.add_argument("-c", "--classifier", required=True,
	help="path to output model trained to recognize poses")
ap.add_argument("-l", "--le", required=True,
	help="path to output label encoder")
args = vars(ap.parse_args())


# load the pose features
print("[INFO] loading sample pose features...")
data = pickle.loads(open(args["features"], "rb").read())

# encode the labels
print("[INFO] encoding labels...")
le = LabelEncoder()
labels = le.fit_transform(data["labels"])
features = data["features"]

width=224
height=224
dim = (width, height)

print("[INFO] training model...")
clf = svm.SVC(kernel="linear", probability=True) # classifier
clf.fit(features, labels)

# write the actual pose recognition model to disk
f = open(args["classifier"], "wb")
f.write(pickle.dumps(clf))
f.close()

# write the label encoder to disk
f = open(args["le"], "wb")
f.write(pickle.dumps(le))
f.close()


