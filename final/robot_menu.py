#!/usr/bin/env python3
# Derived from examples in the Flask-Ask repo: https://github.com/johnwheeler/flask-ask

from flask import Flask
from flask_ask import Ask, statement, question
import robot_chat_server
import student
import teacher

app = Flask(__name__)
ask = Ask(app, '/')

address="" #insert ngrok address for teacher

@ask.intent('Find')
def find_person(name):
    speech_text = 'Locating '+name
    return statement(speech_text).simple_card('My Robot', speech_text)
@ask.intent('YogaTeacher')
def yoga_teacher():
    speech_text = 'Starting class'
    try:
        teacher.start_teacher()
    except:
        print("starting failed")
    return statement(speech_text).simple_card('My Robot', speech_text)
@ask.intent('YogaStudent')
def yoga_student():
    global address
    speech_text = 'Connecting to class'
    student.create_client(address)
    return statement(speech_text).simple_card('My Robot', speech_text)
@ask.intent('wander')
def wander():
    speech_text = 'Wandering'
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
