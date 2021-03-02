import requests

f=open("maker.key","r")
secret_key=f.read()
requests.post("https://maker.ifttt.com/trigger/YourEventName/with/key"+secret_key)    
f.close()
