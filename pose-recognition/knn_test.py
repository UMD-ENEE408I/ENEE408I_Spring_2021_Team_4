import cv2
import argparse
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.neighbors import KNeighborsClassifier

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--features", required=True,
	help="path to serialized db of sample pose features")
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

X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=.2)

clf = KNeighborsClassifier(n_neighbors=5)

clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)

print("Accuracy:", metrics.accuracy_score(y_test, y_pred))

