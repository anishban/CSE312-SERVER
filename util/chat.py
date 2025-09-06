import json
import html
from util.response import Response
import uuid
from util.database import *
from util.profile_pic import picture
from util.authentication import *
from util.github import *

def chat_op(request,handler):
        data = json.loads(request.body.decode('UTF-8'))
        content = data.get('content')
        content = html.escape(content)
        author = request.cookies.get('session')
        if author==None:
            author = request.cookies.get('auth_token')
            if author != None:
                author = find_auth(author)
                if author != None:
                    if author.get("access_token") != None and content[0]=='/':
                        chat(request,handler,content,author)
                        return
                    elif author.get("access_token")==None and content[0]=='/':
                        res=Response()
                        res.set_status(400,"Bad Request")
                        res.text("Not Logged in with OAuth")
                        handler.request.sendall(res.to_data())
                        return
                    author=author.get('username')
        
        res=Response()
        res.set_status(200,'OK')
        res.text('message sent')
        session_user = False
        if author == None:
            author = str(uuid.uuid4())
            session_user = True
            res.cookies({'session':author+';Path=/'})
        id = str(uuid.uuid4())
        nick = nickname_collection.find_one({'author':author})
        if nick != None:
            nick = nick.get('nickname')
        prof_pic = None
        user_record = users.find_one({'username': author})
        prof_pic = user_record.get('imageURL') if user_record else None

        if not prof_pic:
            svg_path = f'/public/imgs/profile-pics/{author}.svg'
            if not os.path.exists(svg_path):
                picture(author)
            prof_pic = svg_path
        chat_collection.insert_one({
            'nickname':nick,
            'author':author,
            'imageURL':prof_pic,
            'id':id,
            'content':content,
            'reactions':{},
            'updated':False
        })
        
        
        handler.request.sendall(res.to_data())

def get_chat(request,handler):
    chat_list = list(chat_collection.find({},{'_id':0}))
    resp = {'messages':chat_list}
    res = Response()
    res.json(resp)
    handler.request.sendall(res.to_data())

def delete(request,handler):
    message_id = request.path.rsplit('/',1)[1]
    auth = request.cookies.get('auth_token')
    if auth == None:
        user_request_id=request.cookies.get('session')
    else:
        user = find_auth(auth)
        user_request_id=user.get('username')
    message = chat_collection.find_one({'id':message_id})
    if not message:
        res = Response()
        res.set_status(404,'Not Found')
        handler.request.sendall(res.to_data())
        return
    actual_user_id = message.get('author')
    if actual_user_id == user_request_id:
        chat_collection.delete_one({'id':message_id})
        res = Response()
        res.text('deleted')
        handler.request.sendall(res.to_data())
    else:
        res = Response()
        res.set_status(403,'Forbidden')
        res.text("You cannot delete someone else's message")
        handler.request.sendall(res.to_data())

def update(request,handler):
    message_id = request.path.rsplit('/',1)[1]
    auth = request.cookies.get('auth_token')
    if auth == None:
        print('User not logged in')
        user_request_id = request.cookies.get('session')
    else:
        print('User logged in')
        user = find_auth(auth)
        user_request_id=user.get('username')
        print('User_request_id: ',user_request_id)
    message = chat_collection.find_one({'id':message_id})
    if message == None:
        res = Response()
        res.set_status(404,'Not Found')
        handler.request.sendall(res.to_data())
        return
    actual_user_id = message.get('author')
    if actual_user_id == user_request_id:
        updated_msg = html.escape(json.loads(((request.body).decode('UTF-8'))).get('content'))
        updated_message = {'$set':{
            'content': updated_msg,
            'updated':True}
        }
        chat_collection.update_one({'id':message_id},updated_message)
        res=Response()
        res.text('updated')
        handler.request.sendall(res.to_data())
    else:
        res = Response()
        res.set_status(403,'Forbidden')
        res.text("You cannot modify someone else's message")
        handler.request.sendall(res.to_data())