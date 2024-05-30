import firebase_admin
from firebase_admin import credentials,db

cred = credentials.Certificate("testkey.json")
name = firebase_admin.initialize_app(cred,
    {'databaseURL' : 'https://stftmonitoring-default-rtdb.firebaseio.com/'
     })

root = db.reference()
state = root.child('state')
state.child('변수').set(12)

print(name)

ref = db.reference('/') #최상위 경로 값
print(ref.get()['state'])

