from robot_chat_client import RobotChatClient


def test_callback(message_dict):
   
    if message_dict['type'] == 'pose':
        print('Value of field pose: {}'.format(message_dict['pose']))

   
# Run this script directly to invoke this test sequence
if __name__ == '__main__':
    print('Creating RobotChatClient object')
    client = RobotChatClient('', callback=test_callback) #ngrok server goes in here

    


