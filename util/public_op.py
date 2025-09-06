from util.response import Response
import os
def public_op(request,handler):
        f_path = '.'+request.path
        if not os.path.exists(f_path):
            res = Response()
            res.set_status(404,'Not Found')
            handler.request.sendall(res.to_data())
            return
        res = Response()
        MIMES={
            '.html': 'text/html; charset=utf-8',
            '.css': 'text/css; charset=utf-8',
            '.js': 'application/javascript; charset=utf-8',
            '.jpg': 'image/jpeg',
            '.ico': 'image/x-icon',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.svg':'image/svg+xml',
            '.png':'image/png',
            '.mp4':'video/mp4',
            '.m3u8':'application/vnd.apple.mpegurl',
            '.ts':'video/MP2T'
        }
        extension = '.'+((request.path.split('.'))[1])
        MIME = MIMES.get(extension)
        with open(f_path, 'rb') as file:
            data_con = file.read()
        
        res.headers({'Content-Type':MIME})
        res.bytes(data_con)
        handler.request.sendall(res.to_data())