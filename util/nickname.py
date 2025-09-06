from util.database import chat_collection
from util.database import nickname_collection
from util.response import Response
import html
import json

def nickname(request,handler):
    user_id = request.cookies.get('session')
    nick = html.escape(json.loads(((request.body).decode('UTF-8'))).get('nickname'))
    updated ={'$set':{
        'nickname':nick
    }}
    chat_collection.update_many({'author':user_id},updated)
    a=nickname_collection.find_one({'author':user_id})
    if a==None:
        nickname_collection.insert_one({'author':user_id,'nickname':nick})
    else:
        updated={'$set':{'nickname':nick}}
        nickname_collection.update_one({'author':user_id},updated)
    res=Response()
    res.text('Nickname Updated')
    handler.request.sendall(res.to_data())