from util.request import Request
from util.helper_multipart import *

#I have removed spaces from inbetween headers, like
#form-data; name="uploaded-file"; filename="pngtree-blue became
#form-data;name="uploaded-file";filename="pngtree-blue
def parse_multipart(request):
    con_type = request.headers.get('Content-Type')
    boundary = con_type.split("boundary=")[1]
    parts=[]
    body=request.body
    all_parts = body.split(b"--"+boundary.encode('UTF-8'))
    for i in range(0,len(all_parts)):
        if all_parts[i].startswith(b'\r\nContent-Disposition'):
            break
    for j in range(0,len(all_parts)):
        if all_parts[j].startswith(b'--'):
            break

    while i<j:
        cur_part = all_parts[i]
        cur_part=cur_part.split(b'\r\n',1)[1]
        cur_h, cur_b = cur_part.split(b'\r\n\r\n',1)
        cur_h=cur_h.decode('UTF-8')
        this_headers={}
        headers=cur_h.split('\r\n')
        for header in headers:
            h=header.split(':',1)
            this_headers[h[0]]=h[1].strip()
        content = cur_b.rsplit(b'\r\n',1)[0]
        name = this_headers.get('Content-Disposition')
        name = name.split('name=',1)[1]
        name = name.split(';',1)[0]
        name = name.replace('"','')
        name=name.replace("'","")
        
        part = Part(this_headers,name,content)
        parts.append(part)
        i+=1
    return Boundary(boundary,parts)


    

def test():
    request = b'POST /upload HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nContent-Length: 7534\r\nCache-Control: max-age=0\r\nsec-ch-ua: "Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"\r\nsec-ch-ua-mobile: ?0\r\nsec-ch-ua-platform: "Windows"\r\nOrigin: null\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundarya1Uomm0JbobWAxKa\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7\r\nSec-Fetch-Site: cross-site\r\nSec-Fetch-Mode: navigate\r\nSec-Fetch-User: ?1\r\nSec-Fetch-Dest: document\r\nAccept-Encoding: gzip, deflate, br, zstd\r\nAccept-Language: en-US,en;q=0.9\r\n\r\n------WebKitFormBoundarya1Uomm0JbobWAxKa\r\nContent-Disposition: form-data; name="title"\r\n\r\nSmall Image\r\n------WebKitFormBoundarya1Uomm0JbobWAxKa\r\nContent-Disposition: form-data; name="description"\r\n\r\nThis is a small image\r\n------WebKitFormBoundarya1Uomm0JbobWAxKa\r\nContent-Disposition: form-data; name="uploaded-file"; filename="pngtree-blue-bird-vector-or-color-illustration-png-image_2013004.jpg"\r\nContent-Type: image/jpeg\r\n\r\n/assz/abc/z00\r\n/d/z00\r\n------WebKitFormBoundarya1Uomm0JbobWAxKa--\r\n'
    req = Request(request)
    ret = parse_multipart(req)
    assert ret.boundary == '----WebKitFormBoundarya1Uomm0JbobWAxKa'
    assert len(ret.parts) == 3
    assert(ret.parts[0].name) == 'title'
    assert (ret.parts[2]).content == b'/assz/abc/z00\r\n/d/z00'
    assert (ret.parts[2]).headers.get('Content-Type') == "image/jpeg"
    assert (ret.parts[2]).headers.get('Content-Disposition') == 'form-data; name="uploaded-file"; filename="pngtree-blue-bird-vector-or-color-illustration-png-image_2013004.jpg"'
    assert ret.parts[2].name == "uploaded-file"

if __name__ == "__main__":
    test()