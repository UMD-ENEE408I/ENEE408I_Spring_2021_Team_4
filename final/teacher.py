from robot_chat_client import RobotChatClient
from robot_chat_server import start_server_func
from pose.pose_rec_obj import PoseRecognition
import threading

#def test_callback(message_dict):
#    if message_dict['type'] == 'pose':
#        print('Value of field pose: {}'.format(message_dict['pose']))

   
#def send_message(message):
#    global client
#    client.send({'type':'pose',
#        'pose':message})

# Run this script directly to invoke this test sequence
def start_teacher():
    print("START SERVER FUNC")
    server_thread = threading.Thread(target=start_server_func)
    #server_thread.daemon=True
    #start_server_func()
    server_thread.start()
    print('Creating PoseRecognition object')
    pr=PoseRecognition()
    while True:
        pass

    


