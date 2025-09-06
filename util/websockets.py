import hashlib
import base64
from util.response import Response
from util.request import Request
import json
from util.database import *
from util.authentication import *
import datetime

connections = {}
calls = {}

class wb:
    def __init__(self,fin_bit,opcode,payload_length,payload):
        self.fin_bit = fin_bit
        self.opcode = opcode
        self.payload_length = payload_length
        self.payload=payload

def compute_accept(key:str):
    gu = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    key=(key+gu).encode('UTF-8')
    key = hashlib.sha1(key).digest()
    key = base64.b64encode(key).decode('UTF-8')
    return key

def parse_ws_frame(frame:bytes):
    fin_bit = (frame[0]&128)>>7
    opcode = (frame[0]&15)
    mask = (frame[1]&128)>>7
    first_len = (frame[1]&127)
    actual_len = first_len
    if first_len < 126:
        if mask == 1:
            masking = frame[2:6]
            payload = frame[6:]
            payload = bytes([b ^ masking[i % 4] for i, b in enumerate(payload)])
        else:
            payload = frame[2:]
    elif first_len == 126:
        actual_len = frame[2:4]
        actual_len = int.from_bytes(actual_len,'big')
        if mask == 1:
            masking = frame[4:8]
            payload = frame[8:]
            payload = bytes([b ^ masking[i % 4] for i, b in enumerate(payload)])
        else:
            payload = frame[4:]
    elif first_len == 127:
        actual_len = frame[2:10]
        actual_len = int.from_bytes(actual_len,'big')
        if mask == 1:
            masking = frame[10:14]
            payload = frame[14:]
            payload = bytes([b ^ masking[i % 4] for i, b in enumerate(payload)])
        else:
            payload = frame[10:]
    
    return wb(fin_bit=fin_bit,opcode=opcode,payload_length=actual_len,payload=payload)
    
def generate_ws_frame(input:bytes):
    byte0 = 0b10000001
    length = len(input)
    if length < 126:
        byte1 = length & 0b01111111
        frame = bytes([byte0,byte1])+input
        return frame
    if length>=126 and length<65536:
        byte1 = 126 & 0b01111111
        frame = bytes([byte0,byte1])+length.to_bytes(2,'big')+input
        return frame
    if length >=65536:
        byte1 = 127 & 0b01111111
        frame = bytes([byte0,byte1])+length.to_bytes(8,'big')+input
        return frame

def test1():
    payload = bytes([i for i in range(0,12)])
    leng = len(payload)
    frame_generated = generate_ws_frame(payload)
    result = parse_ws_frame(frame_generated)
    assert result.payload == payload
    assert leng == result.payload_length

    payload = bytes([i for i in range(0,200)])
    leng = len(payload)
    frame_generated = generate_ws_frame(payload)
    result = parse_ws_frame(frame_generated)
    assert result.payload == payload
    assert leng == result.payload_length

    payload = bytes([i % 256 for i in range(0,75536)])
    leng = len(payload)
    frame_generated = generate_ws_frame(payload)
    result = parse_ws_frame(frame_generated)
    assert result.payload == payload
    assert leng == result.payload_length

    print("all tests passed")

if __name__ == '__main__':
    test1()

def websocket(request,handler):
    key = request.headers.get('Sec-WebSocket-Key')
    auth_token = request.cookies.get('auth_token')
    user = find_auth(auth_token)
    username = user.get('username')
    accept = compute_accept(key)
    ret_headers = {'Sec-WebSocket-Accept':accept,'Connection':'Upgrade','Upgrade':'websocket'}
    res=Response()
    res.headers(ret_headers)
    res.set_status(101,'Switching Protocols')
    handler.request.sendall(res.to_data())
    connections[username]=handler.request
    send_list()
    if drawings is not None:
        ret = {'messageType': 'init_strokes'}
        strokes = list(drawings.find({}, {'_id': 0}))
        if strokes:
            ret['strokes'] = strokes
            handler.request.sendall(generate_ws_frame(json.dumps(ret).encode('utf-8')))
    dat = b''
    for_next=b''
    tot_payload = b''
    while True:
            dat=for_next
            dat += handler.request.recv(2048)

            mask = (dat[1]&128)>>7
            first_len = dat[1]&127
            actual_len = first_len
            header_len=2
            if first_len==126:
                actual_len=dat[2:4]
                actual_len=int.from_bytes(actual_len,'big')
                header_len+=2
            elif first_len==127:
                actual_len=dat[2:10]
                actual_len=int.from_bytes(actual_len,'big')
                header_len+=8
            if mask:
                header_len+=4
            frame_end = header_len+actual_len
            while True:
                if len(dat)==frame_end:
                    break
                if len(dat)>frame_end:
                    cdat = dat[:frame_end]
                    for_next=dat[frame_end:]
                    dat=cdat
                    break
                dat += handler.request.recv(2048)
                for_next=b''

            frame = parse_ws_frame(dat)
            tot_payload+=frame.payload
            if frame.opcode==8:
                left(username,handler,request)
                send_list()
                return
            if frame.fin_bit == 0:
                continue
            message = json.loads((tot_payload).decode())
            messageType = message.get('messageType')

            if messageType == 'echo_client':
                text = message.get('text')
                ret_msg = {'messageType':'echo_server'}
                ret_msg['text']=text
                ret_msg = json.dumps(ret_msg).encode('UTF-8')
                handler.request.send(generate_ws_frame(ret_msg))
            
            elif messageType=='drawing':
                drawing(message)
            elif messageType =='get_all_users':
                get_all_users(handler)
            elif messageType == 'direct_message':
                dm(message,username)
            elif messageType == 'select_user':
                dm_history(message,username,handler)
            elif messageType == 'get_calls':
                get_calls(handler)
            elif messageType == 'join_call':
                join_call(username,message,handler,request)
            elif messageType in ['offer','answer','ice_candidate']:
                webrtc(username,message,handler,request)
            tot_payload=b''    

def webrtc(username,message,handler,request):
    to_socketID = message.get('socketId')
    message['socketId']=str(id(handler.request))
    message['username']=username
    for cid, call in calls.items():
        for participant in call['handles']:
            if participant['username'] == username:
                for target in call['handles']:
                    if target.get('socketId') == to_socketID:
                        try:
                            target['handle'].sendall(generate_ws_frame(json.dumps(message).encode('utf-8')))
                        except:
                            pass
                        return
        

def join_call(username,message,handler,request):
    cid = message.get('callId')
    socketID = str(id(handler.request))
    ret = {'messageType':'call_info','name':calls[cid].get('name')}
    handler.request.sendall(generate_ws_frame(json.dumps(ret).encode('utf-8')))

    call = calls[cid]
    participants = call.get('participants')
    ret = {'messageType':'existing_participants','participants':participants}
    handler.request.sendall(generate_ws_frame(json.dumps(ret).encode('utf-8')))

    ret = {'messageType':'user_joined','socketId':socketID,'username':username}
    for i in calls[cid]['handles']:
        i['handle'].sendall(generate_ws_frame(json.dumps(ret).encode('utf-8')))

    participant = {'socketID':socketID,'username':username}
    calls[cid]['participants'].append(participant)
    d = {'username':username,'socketId':socketID,'handle':handler.request}
    calls[cid]['handles'].append(d)
    return

def get_calls(handler):
    l=[]
    for key, val in calls.items():
        l.append({'id':val['id'],'name':val['name']})
    ret = {'messageType':'call_list','calls':l}
    handler.request.sendall(generate_ws_frame(json.dumps(ret).encode('utf-8')))
    return



def dm_history(message,from_username,handler):
    to_username = message.get('targetUser')
    all_msgs = dms.find({
        'messageType': 'direct_message',
        '$or': [
            {'fromUser': from_username, 'targetUser': to_username},
            {'fromUser': to_username, 'targetUser': from_username}
        ]
    },{'_id':0,'messageType':0}).sort('time', 1)
    all_msgs=list(all_msgs)
    ret = {'messageType':'message_history','messages':all_msgs}
    handler.request.sendall(generate_ws_frame(json.dumps(ret).encode('utf-8')))
    return



def dm(message,from_username):
    time = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    to_username = message.get('targetUser')
    text=message.get('text')
    msg = {'messageType':'direct_message','fromUser':from_username, 'targetUser':to_username, 'text':text, 'time':time}
    dms.insert_one(msg)
    ret = {'messageType':'direct_message','text':text}
    
    ret['fromUser'] = from_username
    to_handler=connections.get(to_username)
    from_handler=connections.get(from_username)
    if to_handler != None:
        to_handler.sendall(generate_ws_frame(json.dumps(ret).encode('utf-8')))
    ret['targetUser'] = to_username
    if from_handler != None:
        from_handler.sendall(generate_ws_frame(json.dumps(ret).encode('utf-8')))
    return

def get_all_users(handler):
    all_users = list(users.find({},{'username':1,'_id':0}))
    ret_msg = {'messageType':'all_users_list','users':all_users}
    print(ret_msg)
    handler.request.sendall(generate_ws_frame(json.dumps(ret_msg).encode('utf-8')))
    return

def left(username,handler,request):
    socket_id = str(id(handler.request))
    for cid, cdata in list(calls.items()):
        cdata['participants'] = [p for p in cdata['participants'] if p['username'] != username]
        new_handles = []
        for h in cdata['handles']:
            if h['username'] != username:
                new_handles.append(h)
        cdata['handles'] = new_handles
        msg = {'messageType': 'user_left','socketId': socket_id}
        for i in cdata['handles']:
            if i['handle'] != None:
                i['handle'].sendall(generate_ws_frame(json.dumps(msg).encode('utf-8'))) 

    connections[username]=None
    return


def send_list():
    ret = {'messageType':'active_users_list'}
    users = []
    for user,check in connections.items():
        if check != None:
            users.append({'username':user})
    ret['users']=users
    frame = generate_ws_frame(json.dumps(ret).encode())
    for key,i in connections.items():
        try:
            if i != None:
                i.sendall(frame)
        except:
            connections[key]=None
            send_list()
    return

def drawing(message):
    startX = message.get('startX')
    startY = message.get('startY')
    endX = message.get('endX')
    endY = message.get('endY')
    color = message.get('color')

    draw = {'startX':startX,'startY':startY,'endX':endX,'endY':endY,'color':color}
    drawings.insert_one(draw)
    to_broadcast = {'messageType':'drawing','startX':startX,'startY':startY,'endX':endX,'endY':endY,'color':color}
    ret_frame=generate_ws_frame((json.dumps(to_broadcast)).encode())
    for key,i in connections.items():
        try:
            if i != None:
                i.sendall(ret_frame)
        except:
            connections[key]=None
            send_list()
    return

def vid_call(request,handler):
    body = request.body
    body = body.decode('utf-8')
    body = json.loads(body)
    name = body.get('name')
    id = str(uuid.uuid4())
    res=Response()
    ret = {'id':id}
    res.json(ret)

    handler.request.sendall(res.to_data())

    calls[id]={'name':name,'id':id,'participants':[],'handles':[]}
    return
                







