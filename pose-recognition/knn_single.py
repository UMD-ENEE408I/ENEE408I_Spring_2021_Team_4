import cv2
import argparse
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
import yoga_pose as yoga

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--features", required=True,
	help="path to serialized db of sample pose features")
ap.add_argument("-i", "--image", required=True,
	help="path to image")
args = vars(ap.parse_args())


# load the pose features
print("[INFO] loading sample pose features...")
data = pickle.loads(open(args["features"], "rb").read())

# encode the labels
print("[INFO] encoding labels...")
le = LabelEncoder()
labels = le.fit_transform(data["labels"])


width=224
height=224
dim = (width, height)

model = KNeighborsClassifier(n_neighbors=5)
model.fit(data["features"], labels)

print("[INFO] reading image...")
img = cv2.imread(args["image"], cv2.IMREAD_UNCHANGED)
image = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

data = yoga.preprocess(image)
cmap, paf = yoga.model_trt(data)
cmap, paf = cmap.detach().cpu(), paf.detach().cpu()
counts, objects, peaks = yoga.parse_objects(cmap, paf) #, cmap_threshold=0.15, link_threshold=0.15)
yoga.draw_objects(image, counts, objects, peaks)
sample = [0.0]*len(yoga.BONES)
yoga.extract_angles(image, counts, objects, peaks, sample)

print("[INFO] classifying...")
z = model.predict([sample])
predicted_pose = le.classes_[z][0]
print(predicted_pose)
cv2.putText(image, predicted_pose, (0,20),
				cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
cv2.imshow('output', image)
cv2.waitKey(0)
#print("[INFO] freeing resources...")
cv2.destroyAllWindows()
