from util.response import Response
from util.request import Request
import pyotp
import html
from util.auth import *
import bcrypt
from util.database import *
import uuid
import hashlib

def find_auth(auth_token:str):
    auth_token = auth_token.encode('UTF-8')
    hash = hashlib.sha256(auth_token)
    user = users.find_one({"auth_token":hash.hexdigest()})
    return user

def register(request,handler):
    usr, pas, totp = extract_credentials(request)
    if users.find_one({'username':usr}) != None:
        res=Response()
        res.set_status(400,'Bad Request')
        res.text('Username is taken')
        handler.request.sendall(res.to_data())
        return
    if not validate_password(pas):
        res = Response()
        res.set_status(400,'Bad Request')
        res.text('Password invalid')
        handler.request.sendall(res.to_data())
        return
    bytes_pass = pas.encode('UTF-8')
    salt = bcrypt.gensalt()
    hashed_pass = bcrypt.hashpw(bytes_pass,salt)
    hashed_pass=hashed_pass.decode('UTF-8')
    registration_id = str(uuid.uuid4())

    user = {
        'id':registration_id,
        'username':usr,
        'password':hashed_pass
    }

    users.insert_one(user)
    res=Response()
    res.set_status(200,'OK')
    res.text('Registration Succesfull')
    handler.request.sendall(res.to_data())
    return

def login(request,handler):
    usr,pas,totpp = extract_credentials(request)
    user = users.find_one({'username':usr})
    if user == None:
        res=Response()
        res.set_status(400,'Bad Request')
        res.text('Username not found')
        handler.request.sendall(res.to_data())
        return
    secret = user.get("secret")
    if secret != None:
        if totpp == None:
            res=Response()
            res.set_status(401,"No TOTP")
            handler.request.sendall(res.to_data())
            
        secret = user.get("secret")
        actual_totp=pyotp.TOTP(secret)
        if actual_totp.verify(totpp)==False:
            res=Response()
            res.set_status(400,"Bad Request")
            res.text("OTP does not match")
            handler.request.sendall(res.to_data())
            return

        
    hashed_pass = (user.get('password')).encode('UTF-8')
    if bcrypt.checkpw(pas.encode('UTF-8'),hashed_pass) == False:
        res = Response()
        res.set_status(400,'Bad Request')
        res.text('Wrong Password')
        handler.request.sendall(res.to_data())
        return
    auth_token = str(uuid.uuid4())
    hashed_auth = hashlib.sha256(auth_token.encode('UTF-8'))
    hashed_auth=hashed_auth.hexdigest()
    updated = {'$set':{'auth_token':hashed_auth}}
    users.update_one({'username':usr},updated)
    res = Response()
    res.set_status(200,'OK')
    res.cookies({'auth_token':auth_token+';Max-Age=100000;HttpOnly'})
    guest_sesh = request.cookies.get('session')
    if guest_sesh != None:
        res.cookies({"session":"deleted;Max-Age=0;Path=/"})
        updated = {'$set':{
            'author':usr
        }}
        chat_collection.update_many({'author':guest_sesh},updated)
        nickname_collection.update_many({'author':guest_sesh},updated)
    handler.request.sendall(res.to_data())

    
    return

def logout(request,handler):
    auth_token = request.cookies.get('auth_token')
    user = find_auth(auth_token)
    if user==None:
        res=Response()
        res.set_status(404,'Not Found')
        res.text('User not logged in')
        handler.request.sendall(res.to_data())
        return
    updated = {'$set':{'auth_token':None}}
    res=Response()
    res.set_status(302,"Found")
    res.headers({'Location':'/'})
    res.cookies({'auth_token':'0; Max-Age=0'})
    users.update_one({'username':user.get('username')},updated)
    res.text('Logged Out')
    handler.request.sendall(res.to_data())
    return


def me(request,handler):
    auth_token = request.cookies.get('auth_token')
    if auth_token == None:
        res=Response()
        res.set_status('401','Bad Request')
        res.json({})

        handler.request.sendall(res.to_data())
        return
    user = find_auth(auth_token)
    if user==None:
        res=Response()
        res.set_status(404,'Not Found')
        res.json({})

        handler.request.sendall(res.to_data())
        return
    ret = {}
    ret['id']=user.get('id')
    ret['username']=user.get('username')
    ret['imageURL']=user.get('imageURL')
    res=Response()
    res.json(ret)

    handler.request.sendall(res.to_data())
    return

def settings(request,handler):
    usr,pas,totp=extract_credentials(request)
    auth_token = request.cookies.get('auth_token')
    user = find_auth(auth_token)
    updated = {'$set':{}}
    if pas != '':
        if not validate_password(pas):
            res=Response()
            res.set_status(400,'Bad Request')
            res.text('Invalid Password')
            handler.request.sendall(res.to_data())
            return
        pas=pas.encode('UTF-8')
        hashed_pas = bcrypt.hashpw(pas,bcrypt.gensalt())
        (updated['$set'])['password']=hashed_pas.decode('UTF-8')
    if not user.get('username')==usr:
        if users.find_one({'username':usr}):
            res=Response()
            res.set_status(400,'Bad Request')
            res.text('Modified username already exists')
            handler.request.sendall(res.to_data())
            return
        else:
            (updated['$set'])['username']=usr
    users.update_one({'username':user.get('username')},updated)
    res=Response()
    res.set_status(200,"OK")
    handler.request.sendall(res.to_data())
    return
    

    