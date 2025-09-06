import requests
from dotenv import load_dotenv
from util.response import Response
import os
import secrets
import uuid
import hashlib
from util.database import *
from util.profile_pic import *
load_dotenv()
GITHUB_CLIENT_ID=os.getenv("GITHUB_CLIENT_ID","changeMe")
GITHUB_CLIENT_SECRET=os.getenv("GITHUB_CLIENT_SECRET","changeMe")
REDIRECT_URI = os.getenv('REDIRECT_URI',"changeMe")
def login_github(request,handler):
    state=secrets.token_hex(8)
    request_url = "https://github.com/login/oauth/authorize"+"?client_id="+GITHUB_CLIENT_ID+"&redirect_uri="+REDIRECT_URI+"&scope=user:email repo"+"&state="+state
    res=Response()
    res.set_status(302,"Found")
    res.headers({"Location":request_url})
    res.cookies({"state":state+';Max-Age=600'})
    handler.request.sendall(res.to_data())

def callback(request,handler):
    if "code" not in request.path:
        res=Response()
        res.set_status(308,"Permanent Redirect")
        res.headers({"Location":"http://localhost:8080/login"})
        handler.request.sendall(res.to_data())
        return
    code = (request.path).split('code=',1)[1]
    code,state=(code).split('&state=',1)
    if request.cookies.get('state',None) != state:
        res=Response()
        res.set_status(400,"Bad Request")
        res.text("Request is not authenticated")
        handler.request.sendall(res.to_data())
        return
    url = "https://github.com/login/oauth/access_token"
    headers={"Accept":"application/json"}
    data={
        "client_id":GITHUB_CLIENT_ID,
        "client_secret":GITHUB_CLIENT_SECRET,
        "redirect_uri":REDIRECT_URI,
        "code":code
    }
    resp = requests.post(url,headers=headers,data=data)
    resp=resp.json()
    auth_token = str(uuid.uuid4())
    hashed_auth = hashlib.sha256(auth_token.encode('UTF-8'))
    hashed_auth=hashed_auth.hexdigest()

    url = "https://api.github.com/user"
    headers={"Authorization":resp.get("token_type")+" "+resp.get("access_token"),"Accept":"application/json"}
    resp1 = requests.get(url=url,headers=headers)
    resp1 = resp1.json()
    username=resp1.get("login")
    email=resp1.get("email")
    guest_sesh = request.cookies.get('session')
    if guest_sesh != None:
        res=Response()
        res.cookies({"session":"deleted;Max-Age=0;Path=/"})
        updated = {'$set':{
            'author':username
        }}
        chat_collection.update_many({'author':guest_sesh},updated)
        nickname_collection.update_many({'author':guest_sesh},updated)
    if users.find_one({"username":username}):
        updated = {"$set":{"auth_token":hashed_auth,"access_token":resp.get("access_token"),"token_type":resp.get("token_type")}}
        users.update_one({"username":username},updated)
        res=Response()
        res.set_status(302,"Found")
        res.cookies({"auth_token":auth_token+";HttpOnly;Max-Age=3600"})
        res.cookies({"session":"deleted;Max-Age=0;Path=/"})
        res.cookies({"state":"deleted;Max-Age=0"})
        res.headers({"Location":'/'})
        handler.request.sendall(res.to_data())
        return
    id = str(uuid.uuid4())
    user = {
        "id":id,
        "username":username,
        "auth_token":hashed_auth,
        "token_type":str(resp.get("token_type")),
        "access_token":str(resp.get("access_token")),
        "password":None,
        "email":email
    }
    users.insert_one(user)
    
    res=Response()
    res.set_status(302,"Found")
    res.cookies({"auth_token":auth_token+";HttpOnly;Max-Age=3600"})
    res.cookies({"session":"deleted;Max-Age=0;Path=/"})
    res.cookies({"state":"deleted;Max-Age=0"})
    res.headers({"Location":'/'})
    handler.request.sendall(res.to_data())
    return

def chat(request,handler,content,author):
    command = (content[1:]).split(' ')
    access_token = author.get("access_token")
    token_type=author.get("token_type")
    token_type=token_type.capitalize()
    f=False
    if command[0]=="star":
        headers={"Accept":"application/vnd.github+json","Content-Length":"0","Authorization":token_type+" "+access_token}
        repo = command[1]
        url=" https://api.github.com/user/starred/"+repo
        resp = requests.put(url=url,headers=headers)
        res=Response()
        print(resp.status_code)
        if resp.status_code == 204:
            content = "https://github.com/"+repo
            content=f'<a href="https://github.com/{repo}" target="_blank">{repo}</a>'
            content=f'Succesfully starred {content}'
            f=True
        if resp.status_code == 304:
            res.set_status(400,"Bad Request")
            res.text("Not Modified")
            handler.request.sendall(res.to_data())
            return
        if resp.status_code == 401:
            res.set_status(400,"Cad Request")
            res.text("Requires Authentication")
            handler.request.sendall(res.to_data())
            return
        if resp.status_code == 403:
            res.set_status(400,"Dad Request")
            res.text("Forbidden")
            handler.request.sendall(res.to_data())
            return
        if resp.status_code == 404:
            res.set_status(400,"Ead Request")
            res.text("Resource Not Found")
            handler.request.sendall(res.to_data())
            return
            
    if command[0]=="repos":
        headers={"Accept":"application/vnd.github+json","Content-Length":"0","Authorization":token_type+" "+access_token}
        user=command[1]
        url="https://api.github.com/users/"+user+"/repos"
        resp=requests.get(url=url,headers=headers)
        res=Response()
        if resp.status_code==304:
            res.set_status(400,"Bad Request")
            res.text("Not Modified")
            handler.request.sendall(res.to_data())
            return
        if resp.status_code==422:
            res.set_status(400,"Bad Request")
            res.text("Validation Failed or Endpoint has been Spammed")
            handler.request.sendall(res.to_data())
            return
        if resp.status_code==200:
            repos=resp.json()[:50]
            content="".join([f'<a href="{repo["html_url"]}" target="_blank">{repo["name"]} </a>' for repo in repos])
            content=f'Here are the repos for {user}: {content}'
            f=True
    if command[0]=="createissue":
        repo=command[1]
        title=command[2]
        url="https://api.github.com/repos/"+repo+"/issues"
        headers={"Accept":"application/vnd.github+json","Content-Length":"","Content-Type":"application/json","Authorization":token_type+" "+access_token}
        body={"title":title}
        headers['Content-Length']=str(len(body))
        resp=requests.post(url=url,headers=headers,json=body)
        res=Response()
        if resp.status_code == 400:
            res.set_status(400,"Bad Request")
            res.text("No Content")
            handler.request.sendall(res.to_data())
            return
        if resp.status_code == 401:
            res.set_status(400,"Bad Request")
            res.text("Requires Authentication")
            handler.request.sendall(res.to_data())
            return
        if resp.status_code == 403:
            res.set_status(400,"Bad Request")
            res.text("Forbidden")
            handler.request.sendall(res.to_data())
            return
        if resp.status_code == 404:
            res.set_status(400,"Bad Request")
            res.text("Resource Not Found")
            handler.request.sendall(res.to_data())
            return
        if resp.status_code == 410:
            res.set_status(400,"Bad Request")
            res.text("Gone")
            handler.request.sendall(res.to_data())
            return
        if resp.status_code==422:
            res.set_status(400,"Bad Request")
            res.text("Validation Failed or Endpoint has been Spammed")
            handler.request.sendall(res.to_data())
            return
        if resp.status_code==503:
            res.set_status(400,"Bad Request")
            res.text("Service Unavailable")
            handler.request.sendall(res.to_data())
            return
        if resp.status_code==201:
            html_url=resp.json()
            html_url=html_url.get("html_url")
            content=f'<a href="{html_url}" target="_blank">{repo}</a>'
            content = f'Issue created for {content}'
            f=True
    if f == False:
        res=Response()
        res.set_status(400,"Bad Request")
        res.text("Something went wrong")
        handler.request.sendall(res.to_data())
        return
    

        


    id = str(uuid.uuid4())
    nick = nickname_collection.find_one({'author':author.get('username')})
    if nick != None:
        nick = nick.get('nickname')

    prof_pic = author.get('imageURL') 

    if not prof_pic:
        svg_path = f'/public/imgs/profile-pics/{author}.svg'
        if not os.path.exists(svg_path):
            picture(author)
        prof_pic = svg_path

    chat_collection.insert_one({
        'nickname':nick,
        'author':author.get('username'),
        'imageURL':prof_pic,
        'id':id,
        'content':content,
        'reactions':{},
        'updated':False
        })
    res=Response()
    res.set_status(200,"OK")
    handler.request.sendall(res.to_data())
    return

        
