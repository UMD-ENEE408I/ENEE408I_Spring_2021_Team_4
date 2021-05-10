import pkg_resources
import cv2
import json
import torchvision.transforms as transforms
import PIL.Image
import torch
import trt_pose.coco
from torch2trt import TRTModule
from trt_pose.draw_objects import DrawObjects
from trt_pose.parse_objects import ParseObjects
from .extract_angles import ExtractAngles
from .draw_objects import DrawObjects

resource_package = __name__
HUMAN_POSE_JSON = pkg_resources.resource_filename(resource_package, '/'.join(('human_pose', 'human_pose.json')))
OPTIMIZED_MODEL = pkg_resources.resource_filename(resource_package, '/'.join(('human_pose', 'resnet18_baseline_att_224x224_A_epoch_249_trt.pth')))

CAMSET = """nvarguscamerasrc sensor-id=0 
! video/x-raw(memory:NVMM), width=3264, height=2464, framerate=21/1, format=NV12 
! nvvidconv flip-method=2 
! video/x-raw, width=224, height=224, format=BGRx 
! videoconvert 
! video/x-raw, format=BGR 
! appsink"""

BONES = [
    (14,16), # r calf
    (13,15), # l calf
    (12,14), # r thigh
    (11,13), # l thigh
    (11,12), # hip
    (12,17), # r body
    (11,17), # l body
    (0,17), # nose-neck
    (6,17), # r shoulder
    (5,17), # l shoulder
    (6,8), # r arm upper
    (5,7), # l arm upper
    (8,10), # r arm lower
    (7,9), # l arm lower
]

print("[INFO] loading optimized model...")
model_trt = TRTModule()
model_trt.load_state_dict(torch.load(OPTIMIZED_MODEL))

print("[INFO] loading json file describing human pose task...")
with open(HUMAN_POSE_JSON, 'r') as f:
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
extract_angles = ExtractAngles(topology, BONES)