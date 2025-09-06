import socketserver
from util.request import Request
from util.router import Router
from util.hello_path import hello_path
from util.emoji_reaction import *
from util.nickname import *
from util.chat import *
from util.html_pages import *
from util.public_op import *
from util.authentication import *
from util.search import *
from util.twofa import *
from util.github import *
from util.media import *
from util.websockets import *

class MyTCPHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        self.router = Router()
        self.router.add_route('GET', '/hello', hello_path, True)
        self.router.add_route('GET', '/public',public_op, False)
        self.router.add_route('GET','/',index_op,True)
        self.router.add_route('GET','/chat',chathtml_op,True)
        self.router.add_route('POST','/api/chats',chat_op,True)
        self.router.add_route('GET','/api/chats',get_chat,True)
        self.router.add_route('PATCH','/api/chats/{id}',update,False)
        self.router.add_route('DELETE','/api/chats/{id}',delete,False)
        self.router.add_route('PATCH','/api/reaction/{messageID}',add_emoji,False)
        self.router.add_route('DELETE','/api/reaction/{messageID}',rem_emoji,False)
        self.router.add_route('PATCH', '/api/nickname',nickname,True)
        self.router.add_route('GET','/register',register_html,True)
        self.router.add_route('GET','/login',login_html,True)
        self.router.add_route('GET','/settings',settings_html,True)
        self.router.add_route('GET','/search-users',search_users_html,True)
        self.router.add_route('POST','/register',register,True)
        self.router.add_route('POST','/login',login,True)
        self.router.add_route('GET','/api/users/@me',me,True)
        self.router.add_route('GET','/logout',logout,True)
        self.router.add_route('GET','/api/users/search',user_search,False)
        self.router.add_route('POST','/api/users/settings',settings,True)
        self.router.add_route('POST','/api/totp/enable',enable_totp,True)
        self.router.add_route('GET','/authgithub',login_github,True)
        self.router.add_route('GET','/authcallback',callback,False)
        self.router.add_route('GET',"/change-avatar",avatarhtml, True)
        self.router.add_route('POST','/api/users/avatar',change_avatar, True)
        self.router.add_route('GET','/videotube',videotubehtml,True)
        self.router.add_route('GET','/videotube/upload',viduploadhtml,True)
        self.router.add_route('GET','/videotube/videos',view_vid_html, False)
        self.router.add_route('POST','/api/videos',upload_vid,True)
        self.router.add_route('GET','/api/videos',getvideos,True)
        self.router.add_route('GET','/api/videos',getonevid,False)
        self.router.add_route('GET','/api/transcriptions/',transcribe,False)
        self.router.add_route('GET','/videotube/set-thumbnail',thumbnail_html,False)
        self.router.add_route('PUT','/api/thumbnails/',set_thumbnail,False)
        self.router.add_route('GET','/test-websocket',testsocket_html,True)
        self.router.add_route('GET','/drawing-board',drawingBoard_html,True)
        self.router.add_route('GET','/direct-messaging',dm_html,True)
        self.router.add_route('GET','/video-call',vdcall_html,True)
        self.router.add_route('GET','/video-call/',vdcallroom,False)
        self.router.add_route('GET','/websocket',websocket,True)
        self.router.add_route('POST','/api/video-calls',vid_call,True)
        # TODO: Add your routes here
        super().__init__(request, client_address, server)

    def handle(self):
        received_data = self.request.recv(2048)
        request = Request(received_data)
        while True:
            if len(request.body) == int(request.headers.get("Content-Length",0)):
                break
            new_data= self.request.recv(2048)
            received_data += new_data
            request.body += new_data
        print()
        print(self.client_address)
        print('Path: ',request.path,'\n')
        self.router.route_request(request, self)






def main():
    host = '0.0.0.0'
    port = 8080
    socketserver.ThreadingTCPServer.allow_reuse_address = True

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)

    print('Listening on port ' + str(port))
    server.serve_forever()


if __name__ == '__main__':
    main()



