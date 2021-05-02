#!/bin/sh

YT_SERVER="rtmp://a.rtmp.youtube.com/live2"
AUTH=`cat stream.key`
# Needs AUTH, which is the "Stream Name" from Ingestion Settings > Main Camera

# apt-get install --assume-yes gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools



# https://bugzilla.gnome.org/show_bug.cgi?id=731352#c6

#gst-launch-1.0 -v nvarguscamerasrc sensor-id=0 ! 'video/x-raw(memory:NVMM), width=(int)3264, height=(int)2464, framerate=(fraction)21/1, format=(string)NV12' ! nvvidconv flip-method=2 ! omxh264enc ! video/x-h264, format=avc,alignment=au ! h264parse ! kvssink stream-name=RobotCamera1 storage-size=128
gst-launch-1.0 -v nvarguscamerasrc sensor-id=0 ! 'video/x-raw(memory:NVMM), width=(int)3264, height=(int)2464, framerate=(fraction)21/1, format=(string)NV12' ! nvvidconv flip-method=2 \
        ! x264enc bitrate=2000 byte-stream=false key-int-max=60 bframes=0 aud=true tune=zerolatency ! "video/x-h264,profile=main" \
        ! flvmux streamable=true name=mux \
        ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/x/${AUTH} app=live2" \
	audiotestsrc \
	! volume volume=0 ! level \
	! voaacenc bitrate=128000 \
	! mux.
