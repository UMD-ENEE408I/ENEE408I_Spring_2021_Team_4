# Setup

## IFTTT

Create an account: https://ifttt.com/home

Add AlexaActions and Webhooks to your account:

* https://ifttt.com/AlexaActionsByMkzense
* https://ifttt.com/maker_webhooks
## Setup Alexa skill

https://mkzense.com/iftttrigger

Add the following skill to your echo: https://www.amazon.com/gp/product/B08M496VGB

In the communicate tab of the Alexa app, click the "Add New" button to create a new group.

Select the contacts that you would like to add to the emergency group and name the group "robot"

Create a new routine in the Alexa app. In the when field, choose a trigger from AlexaActions. In the actions add "Call robot" as a custom action.

## Setup maker webhook

Go to your maker webhook settings (https://ifttt.com/maker_webhooks/settings) and follow the link provided to get your key

Write this key into a file `maker.key` in this folder

## Complete IFTTT

Create an applet with the trigger as your maker webhook with event "robot_emergency_call" and the action as the AlexaAction you linked to the routine

# Running

Run the program `make_call.py` in python3: `python3 make_call.py`

