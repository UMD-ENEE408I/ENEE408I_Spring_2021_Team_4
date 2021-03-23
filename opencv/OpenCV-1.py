import cv2
print(cv2.__version__)

width=800
height=600
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
#camSet="nvarguscamerasrc sensor-id=0 ! video/x-raw(memory:NVMM), width=3264, height=2464, framerate=21/1, format=NV12 ! nvvidconv flip-method="+str(flip)+" ! video/x-raw, width="+str(width)+", height="+str(height)+", format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink"
#camSet='nvarguscamerasrc1' # NVIDIA argus camera source 1

cam=cv2.VideoCapture(camSet)

while True:
    _, frame = cam.read()
    cv2.imshow('myCam', frame)
    cv2.moveWindow('myCam',0,0)
    if cv2.waitKey(1) == ord('q'):
        break

cam.release() # free the camera
cv2.destroyAllWindows()
