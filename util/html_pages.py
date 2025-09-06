from util.response import Response

def load_html(request,handler,path):
    layout_path = './public/layout/layout.html'
    res = Response()
    MIME='text/html; charset=utf-8'
    with open(path,'rt',encoding='utf-8') as page:
        path_con = page.read()
    with open(layout_path,'rt',encoding='utf-8') as layout:
        layout_con = layout.read()
    fin_data = layout_con.replace('{{content}}',path_con)
    res.headers({'Content-Type':MIME})
    res.text(fin_data)
    handler.request.sendall(res.to_data())


def index_op(request,handler):
    path = './public/index.html'
    load_html(request,handler,path)
def chathtml_op(request,handler):
    path = './public/chat.html'
    load_html(request,handler,path)
def register_html(request,handler):
    path='./public/register.html'
    load_html(request,handler,path)
def login_html(request,handler):
    path = './public/login.html'
    load_html(request,handler,path)
def settings_html(request,handler):
    path = './public/settings.html'
    load_html(request,handler,path)
def search_users_html(request,handler):
    path = './public/search-users.html'
    load_html(request,handler,path)
def avatarhtml(request,handler):
    path='./public/change-avatar.html'
    load_html(request,handler,path)
def videotubehtml(request,handler):
    path='./public/videotube.html'
    load_html(request,handler,path)
def viduploadhtml(request,handler):
    path = './public/upload.html'
    load_html(request,handler,path)
def view_vid_html(request,handler):
    path = './public/view-video.html'
    load_html(request,handler,path)
def thumbnail_html(request,handler):
    path = './public/set-thumbnail.html'
    load_html(request,handler,path)
def testsocket_html(request,handler):
    path = './public/test-websocket.html'
    load_html(request,handler,path)
def drawingBoard_html(request,handler):
    path = './public/drawing-board.html'
    load_html(request,handler,path)
def dm_html(request,handler):
    path = './public/direct-messaging.html'
    load_html(request,handler,path)
def vdcall_html(request,handler):
    path = './public/video-call.html'
    load_html(request,handler,path)
def vdcallroom(request,handler):
    path = './public/video-call-room.html'
    load_html(request,handler,path)