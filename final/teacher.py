from robot_chat_client import RobotChatClient
from robot_chat_server import start_server_func
from pose.pose_rec_obj import PoseRecognition

client=""
def test_callback(message_dict):
    if message_dict['type'] == 'pose':
        print('Value of field pose: {}'.format(message_dict['pose']))

   
def send_message(message):
    global client
    client.send({'type':'pose',
        'pose':message})

# Run this script directly to invoke this test sequence
def start_teacher():
    start_server_func()
    print('Creating RobotChatClient object')
    global client
    client = RobotChatClient('ws://localhost:5001', callback=test_callback) #ngrok server
    pr=PoseRecognition(callback=send_message)


    


