from robot_chat_client import RobotChatClient
import pyttsx3
import teacher



engine = pyttsx3.init()

rate = engine.getProperty('rate')
engine.setProperty('rate', rate-40)

'''
engine.say('This is a test')
engine.say('The current yoga pose is...')
engine.say('The quick brown fox jumped over the lazy dog.')
engine.runAndWait()
'''

def test_callback(message_dict):
    global engine
    if message_dict['type'] == 'pose':
        print('Value of field pose: {}'.format(message_dict['pose']))
        engine.say(message_dict['pose'])
        engine.runAndWait()

def create_client(address):
    client=RobotChatClient(address, callback=test_callback)

