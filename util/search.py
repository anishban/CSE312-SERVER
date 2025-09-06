from util.request import Request
from util.response import Response
from util.database import *
def user_search(request,handler):
    path=request.path
    query=path.split('?user=')[1]
    if query=='':
        res=Response()
        res.json({'users':[]})
        handler.request.sendall(res.to_data())
        return
    user_list=[]
    for user in users.find():
        if (user.get('username')).startswith(query):
            dict={'id':user.get('id'),'username':user.get('username')}
            user_list.append(dict)
    fin_d={'users':user_list}
    res=Response()
    res.json(fin_d)
    handler.request.sendall(res.to_data())
