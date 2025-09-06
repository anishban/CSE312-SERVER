from util.request import Request
import html
def extract_credentials(request):
    body = request.body
    body = body.decode('UTF-8')
    usr,pas=body.split('&',1)
    totp=None
    if "&totpCode=" in pas:
        pas,totp=pas.split('&totpCode=',1)

    charac_dict ={
        '%21':'!',
        '%40':'@',
        '%23':'#',
        '%24':'$',
        '%25':'%',
        '%5E':'^',
        '%26':'&',
        '%28':'(',
        '%29':')',
        '%2D':'-',
        '%5F':'_',
        '%3D':'=',
    }   
    usr = usr.split('=',1)[1]
    pas = pas.split('=',1)[1]
    usr = html.escape(usr)
    i=0
    new_pas=''
    while(i<len(pas)):
        if pas[i] == '%':
            enc = pas[i:i+3]
            i=i+3
            if enc in charac_dict:
                new_pas+=charac_dict[enc]
            else:
                new_pas+=enc
            continue
        new_pas+=pas[i]
        i=i+1
    return [usr,new_pas,totp]



def validate_password(password):
    spc = ['!','@','#','$','%','^','&','(',')','-','_','=']
    if len(password)<8:
        return False
    lower=False
    upper=False
    special=False
    digit=False
    for c in password:
        if c.islower():
            lower=True
        elif c.isupper():
            upper=True
        elif c.isdigit():
            digit=True
        elif c in spc:
            special = True
        else:
            return False
    return lower and upper and digit and special

    
def test():
    pas = 'alltoowell?1'
    assert validate_password(pas)==False
    pas = 'Alltoowell?1'
    assert validate_password(pas)==False
    pas = 'Alltoowell?'
    assert validate_password(pas)==False
    pas = 'hi'
    assert validate_password(pas)==False
    pas='hi!1'
    assert validate_password(pas)==False
    pas = 'Hi!1'
    assert validate_password(pas)==False
    pas = 'HI!12345678'
    assert validate_password(pas)==False
    pas = 'hi!12345678'
    assert validate_password(pas)==False
    pas = 'Hi'
    assert validate_password(pas)==False
    pas = 'helloworld'
    assert validate_password(pas)==False
    pas = 'helloworld1'
    assert validate_password(pas)==False
    pas = 'helloworld!'
    assert validate_password(pas)==False
    pas='HelloWorld1'
    assert validate_password(pas)==False
    pas='HelloWorld!'
    assert validate_password(pas)==False
    pas = 'Hello!1'
    assert validate_password(pas)==False

    request = Request(b'POST /path HTTP/1.1\r\nContent-Type: text/plain\r\nContent-Length: 5\r\n\r\nusername=test&password=%25%252')
    ext= extract_credentials(request)
    usr=ext[0]
    pas=ext[1]
    assert usr=='test'
    assert pas=='%%2'
    
    request= Request(b'POST /path HTTP/1.1\r\nContent-Type: text/plain\r\nContent-Length: 5\r\n\r\nusername=test&password=pass%3Dword%3D123')
    ext=extract_credentials(request)
    usr=ext[0]
    pas=ext[1]
    assert pas=='pass=word=123'

    request=Request(b'POST /path HTTP/1.1\r\nContent-Type: text/plain\r\nContent-Length: 5\r\n\r\nusername=test&password=')
    usr,pas,totp=extract_credentials(request)
   
    assert usr=='test'
    assert pas==''
    assert totp==None







if __name__ == '__main__':
    test()



        

