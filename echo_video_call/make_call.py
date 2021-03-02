import requests

f=open("maker.key","r")
secret_key=f.read().strip()
r=requests.post("https://maker.ifttt.com/trigger/robot_emergency_call/with/key/"+secret_key)    
print(r.text)
f.close()
