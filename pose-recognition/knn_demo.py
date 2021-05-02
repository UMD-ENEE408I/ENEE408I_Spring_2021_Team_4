import cv2
import argparse
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
import yoga_pose as yoga

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--features", required=True,
	help="path to input serialized db of pose features")
args = vars(ap.parse_args())

# load the pose features
print("[INFO] loading pose features...")
data = pickle.loads(open(args["features"], "rb").read())

# encode the labels
print("[INFO] encoding labels...")
le = LabelEncoder()
labels = le.fit_transform(data["poses"])


width=224
height=224
dim = (width, height)

model = KNeighborsClassifier(n_neighbors=3)
model.fit(data["features"], labels)


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
    z = model.predict([sample])
    predicted_pose = le.classes_[z][0]
    cv2.putText(image, predicted_pose, (0,20),
				cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
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
