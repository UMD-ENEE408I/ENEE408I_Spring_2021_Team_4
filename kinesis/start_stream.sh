export GST_PLUGIN_PATH=~/amazon-kinesis-video-streams-producer-sdk-cpp
export LD_LIBRARY_PATH=~/amazon-kinesis-video-streams-producer-sdk-cpp/open-source/local/lib
INPUT=Administrator_accessKeys.csv.key 
OLDIFS=$IFS
IFS=','
line=$(sed -n '2p' $INPUT)
read access_key_id secret_access_key <<< "$line"
#export AWS_ACCESS_KEY_ID=$access_key_id
#export AWS_SECRET_ACCESS_KEY=$secret_access_key
#echo $AWS_ACCESS_KEY_ID
#echo $AWS_SECRET_ACCESS_KEY

IFS=$OLDIFS
export AWS_DEFAULT_REGION=us-east-1
[ ! -f $INPUT ] && { echo "$INPUT file not found"; exit 99; }
gst-launch-1.0 -v nvarguscamerasrc sensor-id=0 ! 'video/x-raw(memory:NVMM), width=(int)3264, height=(int)2464, framerate=(fraction)21/1, format=(string)NV12' ! nvvidconv flip-method=2 ! omxh264enc ! video/x-h264, format=avc,alignment=au ! h264parse ! kvssink stream-name=RobotCamera1 storage-size=128
