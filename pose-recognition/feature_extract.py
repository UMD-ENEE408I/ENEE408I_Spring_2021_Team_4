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
ap.add_argument("-d", "--dataset", default="./data/",
	help="path to input dataset dir of pose images")
ap.add_argument("-f", "--features", required=True,
	help="path to output serialized db of pose features")
ap.add_argument("-m", "--manual", action="store_true")
args = vars(ap.parse_args())

width=224
height=224
dim = (width, height)

print("[INFO] starting...")
imagePaths = list(paths.list_images(args["dataset"]))

# initialize our lists of extracted pose features and
# corresponding people names
knownFeatures = []
knownLabels = []

# initialize the total number of poses processed
total = 0

# loop over the image paths
for (i, imagePath) in enumerate(imagePaths):
    # extract the person name from the image path
    print("[INFO] processing image {}/{}".format(i + 1,
        len(imagePaths)))
    pose = imagePath.split(os.path.sep)[-2]

    img = cv2.imread(imagePath, cv2.IMREAD_UNCHANGED)
    # resize image
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    sample, image = execute({'new': resized})
    cv2.putText(image, pose, (0,20),
				cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    if sample != [0.0]*len(yoga.BONES): # if not empty sample
        if args["manual"]:
            cv2.imshow("output", image) # show the output frame
            key = cv2.waitKey(0) & 0xFF
            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break
            elif key == ord("y"): # if the `y` key was pressed, add sample
                knownLabels.append(pose)
                knownFeatures.append(sample)
                total += 1
                # also add flipped sample
                img2 = cv2.flip(resized,1)
                sample2, image2 = execute({'new': img2})
                knownLabels.append(pose)
                knownFeatures.append(sample2)
                total += 1
            elif key == ord("n"): # if the `y` key was pressed, add sample
                os.remove(imagePath)
        else:
            knownLabels.append(pose)
            knownFeatures.append(sample)
            total += 1
            # also add flipped sample
            img2 = cv2.flip(resized,1)
            sample2, image2 = execute({'new': img2})
            knownLabels.append(pose)
            knownFeatures.append(sample2)
            total += 1
	
cv2.destroyAllWindows()

print("[INFO] encoding labels...")
le = LabelEncoder()
labels = le.fit_transform(knownLabels)

print("[INFO] serializing {} encodings...".format(total))
data = {"features": knownFeatures, "labels": knownLabels}
f = open(args["features"], "wb")
f.write(pickle.dumps(data))
f.close()
