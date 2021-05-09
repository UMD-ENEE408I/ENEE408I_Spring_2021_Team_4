# Setup

Install OpenCV 4.5.1 from source using [this tutorial](https://github.com/UMD-ENEE408I/ENEE408I_Notes_Examples/blob/main/notes/build_install_opencv_4.5.1_and_contrib_xavier_nx.md).

Be sure to reinstall numpy version 1.16.4 afterwards:
    
    python3 -m pip install numpy==1.16.4

Ensure that your Raspberry Pi camera is in your Xavier NX's CAM0 slot.

**Note: python3 must be run with sudo for Arduino communication over USB to work.**

# Usage

To have the robot orient itself towards a named face:

    import face
    name = "leclerc"
    face.find_person(name) # returns after person found and centered
