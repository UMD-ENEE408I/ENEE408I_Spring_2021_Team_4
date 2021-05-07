# Setup

Install OpenCV 4.5.1 from source using [this tutorial](https://github.com/UMD-ENEE408I/ENEE408I_Notes_Examples/blob/main/notes/build_install_opencv_4.5.1_and_contrib_xavier_nx.md).

Be sure to reinstall numpy version 1.16.4 afterwards:
    
    python3 -m pip install numpy==1.16.4

Install trt\_pose and dependencies using the instructions from the [trt\_pose repo](https://github.com/NVIDIA-AI-IOT/trt_pose).
- When installing PyTorch and Torchvision, use the PyTorch **v1.8.0** pip wheel and torchvision **v0.9.0**.

Ensure that your Raspberry Pi camera is in your Xavier NX's CAM0 slot.

Download `resnet18_baseline_att_224x224_A_epoch_249_trt.pth` from [here](https://drive.google.com/open?id=1XYDdCUdiF2xxx4rznmLb62SdOUZuoNbd) and place it in the pose-recognition directory.

# Usage

Create an optimized model for this hardware:

    python3 optimize_model.py

Apply pose recognition to a video stream:

    python3 demo.py

# Yoga

To run the SVM classifier on a camera stream:

    python3 svm_demo.py -f output/features.pickle -c output/svm_classifier.pickle -l output/le.pickle

To run the K-nearest neighbor classifier on a camera stream: 

    python3 knn_demo.py -f output/features.pickle
