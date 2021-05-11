#!/usr/bin/env python3
# Derived from examples in the Flask-Ask repo: https://github.com/johnwheeler/flask-ask

from flask import Flask
from flask_ask import Ask, statement, question
import robot_chat_server
import student
import teacher
import threading
import face
import serial

app = Flask(__name__)
ask = Ask(app, '/')

address="ws://972efb9b711b.ngrok.io" #insert ngrok address for teacher
print("[INFO] Ready.")
@ask.intent('Find')
def find_person(name):
    speech_text = 'Locating '+name
    print("[INTENT] Finding "+name)
    face.find_person(name.lower())
    
    return statement(speech_text).simple_card('My Robot', speech_text)
@ask.intent('YogaTeacher')
def yoga_teacher():
    speech_text = 'Starting class'
    #thread = threading.Thread(target=teacher.start_teacher())
    #thread.daemon=True
    #thread.start()  
    print("[INTENT] Starting class")
    teacher.start_teacher()
    #return statement(speech_text).simple_card('My Robot', speech_text)
@ask.intent('YogaStudent')
def yoga_student():
    global address
    speech_text = 'Connecting to class'
    print("[INTENT] Connecting to class")
    student.create_client(address)
    #return statement(speech_text).simple_card('My Robot', speech_text)
@ask.intent('Wander')
def wander():
    speech_text = 'Wandering'
    print("[INTENT] Wandering")
    #arduino.write(b'w')
    #time.sleep(15.0)
    #arduino.write(b's')
    return statement(speech_text).simple_card('My Robot', speech_text)
@ask.intent('StopWander')
def stop_wander():
    speech_text = 'Stopping wander'
    print("[INTENT] Stopping wander")
    #arduino.write(b's')
    return statement(speech_text).simple_card('My Robot', speech_text)
@ask.launch
def start_skill():
    welcome_message = 'Hello there, Welcome!' 
    return question(welcome_message)
@ask.intent('AMAZON.FallbackIntent')
def fallback():
    speech_text = 'Fallback'
    return statement(speech_text).simple_card('My Robot', speech_text) 

if __name__ == '__main__':
    app.run()
