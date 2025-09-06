class Request:

    def __init__(self, request: bytes):
        # TODO: parse the bytes of the request and populate the following instance variables
        ar = request.split(b'\r\n\r\n',1)
        ar[0]= ar[0].decode('ASCII')
        ar1=ar[0].split('\r\n')
        ar2=ar1[0].split(' ')

        self.body = ar[1]
        self.method = ar2[0]
        self.path = ar2[1]
        self.http_version = ar2[2]
        self.headers = {}
        self.cookies = {}


        headarr = ar1[1:]
        f=False
        for s in headarr:
            s=s.strip()
            elem = s.split(':',1)
            self.headers[elem[0].strip()] = elem[1].strip()
            if (elem[0]=='Cookie'):
                elem1 = elem[1].split(';')
                f=True
        if(f):
            for s in elem1:
                a1 = s.split('=')
                self.cookies[a1[0].strip()]=a1[1].strip()
        

        

def test1():
    request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\n\r\n')
    assert request.method == 'GET'
    assert 'Host' in request.headers
    assert request.headers['Host'] == 'localhost:8080'  # note: The leading space in the header value must be removed
    assert request.body == b''  # There is no body for this request.
    # When parsing POST requests, the body must be in bytes, not str

    # This is the start of a simple way (ie. no external libraries) to test your code.
    # It's recommended that you complete this test and add others, including at least one
    # test using a POST request. Also, ensure that the types of all values are correct

def test2():
    request = Request(b'GET /home HTTP/1.1\r\nHost:localhost:8080\r\nConnection: keep-alive\r\nCookie: id=123456789;visit=3600\r\n\r\n')
    assert request.method == 'GET'
    assert 'Cookie' in request.headers
    assert request.headers['Connection'] == 'keep-alive'
    assert request.headers['Cookie'] == 'id=123456789;visit=3600'
    assert request.cookies['id']=='123456789'
    assert request.cookies['visit']=='3600'
    assert request.body == b''


def test3():
    request = Request(b'POST /path HTTP/1.1\r\nContent-Type: text/plain\r\nContent-Length: 5\r\n\r\nhello world')
    assert request.method == 'POST'
    assert request.path == '/path'
    assert request.http_version == 'HTTP/1.1'
    assert 'Content-Type' in request.headers
    assert request.headers['Content-Type'] == 'text/plain'
    assert 'Content-Length' in request.headers
    assert request.headers['Content-Length'] == '5'
    assert request.body == b'hello world'
    print('passed')

if __name__ == '__main__':
    test1()
    test2()
    test3()