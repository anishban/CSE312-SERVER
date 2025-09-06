from util.response import *
from util.authentication import find_auth
from util.database import *
import pyotp
def enable_totp(request,handler):
    auth = request.cookies.get("auth_token")
    user = find_auth(auth)
    secret = pyotp.random_base32()
    di = {"secret":secret}
    res=Response()
    res.json(di)
    updated = {"$set":{"secret":secret}}
    users.update_one({"username":user.get("username")},updated)
    handler.request.sendall(res.to_data())