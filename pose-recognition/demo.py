import cv2
import json
import torchvision.transforms as transforms
import PIL.Image
import torch
import trt_pose.coco
from torch2trt import TRTModule
from trt_pose.draw_objects import DrawObjects
from trt_pose.parse_objects import ParseObjects


print("[INFO] loading optimized model...")
OPTIMIZED_MODEL = 'resnet18_baseline_att_224x224_A_epoch_249_trt.pth'
model_trt = TRTModule()
model_trt.load_state_dict(torch.load(OPTIMIZED_MODEL))
    
print("[INFO] loading json file describing human pose task...")
with open('human_pose.json', 'r') as f:
    human_pose = json.load(f)

topology = trt_pose.coco.coco_category_to_topology(human_pose)

# define function to preprocess image
mean = torch.Tensor([0.485, 0.456, 0.406]).cuda()
std = torch.Tensor([0.229, 0.224, 0.225]).cuda()
device = torch.device('cuda')

def preprocess(image):
    global device
    device = torch.device('cuda')
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = PIL.Image.fromarray(image)
    image = transforms.functional.to_tensor(image).to(device)
    image.sub_(mean[:, None, None]).div_(std[:, None, None])
    return image[None, ...]


# callable classes to parse objects from neural network and draw parsed objects on image
parse_objects = ParseObjects(topology)
draw_objects = DrawObjects(topology)

# main execution loop
def execute(change):
    image = change['new']
    data = preprocess(image)
    cmap, paf = model_trt(data)
    cmap, paf = cmap.detach().cpu(), paf.detach().cpu()
    counts, objects, peaks = parse_objects(cmap, paf)#, cmap_threshold=0.15, link_threshold=0.15)
    draw_objects(image, counts, objects, peaks)
    cv2.imshow('myCam', image)
    
width=224
height=224
flip=2
# Set up the arduino cam pipeline (parts of pipeline delimited by '!')
# NVIDIA argus camera source 0
camSet=f"""nvarguscamerasrc sensor-id=0 
! video/x-raw(memory:NVMM), width=3264, height=2464, framerate=21/1, format=NV12 
! nvvidconv flip-method={str(flip)} 
! video/x-raw, width={str(width)}, height={str(height)}, format=BGRx 
! videoconvert 
! video/x-raw, format=BGR 
! appsink"""

print("[INFO] starting video stream...")
cam=cv2.VideoCapture(camSet)
while True:
    _, frame = cam.read()
    execute({'new': frame})
    #cv2.moveWindow('myCam',0,0)
    
    if cv2.waitKey(1) == ord('q'):
        break

print("[INFO] freeing resources...")
cam.release() # free the camera
cv2.destroyAllWindows()
