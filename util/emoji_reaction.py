from util.database import chat_collection
from util.response import Response
import html
import json

def add_emoji(request,handler):
    message_id = request.path.rsplit('/',1)[1]
    user_id = request.cookies.get('session')
    message = chat_collection.find_one({'id':message_id})
    reaction = html.escape(json.loads(((request.body).decode('UTF=8'))).get('emoji'))
    old_reac = message.get('reactions')
    if reaction in old_reac:
        user_list = old_reac[reaction]
        if user_id in user_list:
            res = Response()
            res.set_status(403,'Forbidden')
            res.text('You cannot react to the same message twice with the same reaction')
            handler.request.sendall(res.to_data())
            return
        user_list.append(user_id)
        old_reac[reaction] = user_list
        updated = {'$set':{
            'reactions':old_reac
        }}
        chat_collection.update_one({'id':message_id},updated)
        res=Response()
        handler.request.sendall(res.to_data())
        return
    old_reac[reaction] = list([user_id])
    updated = {'$set':{
        'reactions':old_reac
    }}
    chat_collection.update_one({'id':message_id},updated)
    res=Response()
    handler.request.sendall(res.to_data())




def rem_emoji(request,handler):
    message_id = request.path.rsplit('/',1)[1]
    user_id = request.cookies.get('session')
    message = chat_collection.find_one({'id':message_id})
    reaction = html.escape(json.loads(((request.body).decode('UTF=8'))).get('emoji'))
    old_reac = message.get('reactions')
    if reaction in old_reac:
        user_list = old_reac[reaction]
        if user_id in user_list:
            user_list.remove(user_id)
            old_reac[reaction] = user_list
            if old_reac[reaction] == []:
                old_reac.pop(reaction)
            updated = {'$set':{
                'reactions':old_reac
            }}
            chat_collection.update_one({'id':message_id},updated)
            res=Response()
            handler.request.sendall(res.to_data())
            return
        else:
            res = Response()
            res.set_status(403,'Forbidden')
            res.text('You cannot remove a reaction you did not react')
            handler.request.sendall(res.to_data())
            return
    else:
        res=Response()
        res.set_status(404,'Not Found')
        res.text('Specified reaction not found')
        handler.request.sendall(res.to_data())
        return


