# Setup

Install OpenCV 4.5.1 from source using [this tutorial](https://github.com/UMD-ENEE408I/ENEE408I_Notes_Examples/blob/main/notes/build_install_opencv_4.5.1_and_contrib_xavier_nx.md).

Be sure to reinstall numpy version 1.16.4 afterwards:
    
    python3 -m pip install numpy==1.16.4

Install trt\_pose and dependencies using the instructions from the [trt\_pose repo](https://github.com/NVIDIA-AI-IOT/trt_pose).
- When installing PyTorch and Torchvision, use the PyTorch **v1.8.0** pip wheel and torchvision **v0.9.0**.

After installing trt\_pose, move `optimize_model.py`, `benchmark_model.py`, and `demo.py` into `trt_pose/tasks/human_pose/`.

Ensure that your Raspberry Pi camera is in your Xavier NX's CAM0 slot.

# Usage

Create an optimized model for this hardware:

    cd trt_pose/tasks/human_pose
    python3 optimize_model.py

(Optional) Benchmark the model:

    python3 benchmark_model.py

Apply pose recognition to a video stream:

    python3 demo.py
