https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/getting-started.html
Remember to: export AWS_DEFAULT_REGION=us-east-1
gst-launch-1.0 -v nvarguscamerasrc sensor-id=0 ! 'video/x-raw(memory:NVMM), width=(int)3264, height=(int)2464, framerate=(fraction)21/1, format=(string)NV12' ! nvvidconv flip-method=2 ! omxh264enc ! video/x-h264, format=avc,alignment=au ! h264parse ! kvssink stream-name=RobotCamera1 storage-size=128
