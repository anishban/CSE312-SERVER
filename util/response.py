import json


class Response:
    def __init__(self):
        self.code=200
        self.msg='OK'
        self.header_dict={'Content-Type':'text/plain; charset=utf-8',
                          'X-Content-Type-Options':'nosniff'}
        self.cookie_dict={}
        self.data=b''

    def set_status(self, code:int, text:str):
        self.code = code
        self.msg = text
        return self

    def headers(self, headers:dict):
        for i in headers.keys():
            self.header_dict[i]=headers[i]
        return self

    def cookies(self, cookies:dict):
        for i in cookies.keys():

            self.cookie_dict[i]=cookies[i]
        return self

    def bytes(self, data:bytes):
        self.data=self.data+data
        return self

    def text(self, data:str):
        self.data=self.data+data.encode('UTF-8')
        return self

    def json(self, data:json):
        self.data = json.dumps(data).encode('UTF-8')
        self.header_dict['Content-Type']= 'application/json'
        return self

    def to_data(self):
        response = 'HTTP/1.1'+' '+str(self.code)+' '+self.msg+'\r\n'
        content_len = str(len(self.data))
        for key,value in self.header_dict.items():
            response+=key+': '+value+'\r\n'
        for key,value in self.cookie_dict.items():
            response+='Set-Cookie: '+key+'='+value+'\r\n'
        response+='Content-Length: '+content_len+'\r\n\r\n'
        return response.encode('UTF-8')+self.data


def test1():
    res = Response()
    res.text('hello')
    expected = b'HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: 5\r\n\r\nhello'
    actual = res.to_data()


if __name__ == '__main__':
    test1()
