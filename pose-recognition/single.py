import cv2
import argparse
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
    print(sample)
    
    cv2.imshow('output', image)


ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to image")
args = vars(ap.parse_args())

width=224
height=224
dim = (width, height)

print("[INFO] starting...")
img = cv2.imread(args["image"], cv2.IMREAD_UNCHANGED)
# resize image
resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
execute({'new': resized})
cv2.waitKey(0)
print("[INFO] freeing resources...")
cv2.destroyAllWindows()
