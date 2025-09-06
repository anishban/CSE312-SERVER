from util.response import Response
class Router:

    def __init__(self):
        self.routes = []

    def add_route(self, method, path, action, exact_path=False):
        route ={
            'method':method,
            'path':path,
            'action':action,
            'exact_path':exact_path
        }
        self.routes.append(route)

    def route_request(self, request, handler):
        for i in self.routes:
            if i['method'] == request.method and i['exact_path'] == True and i['path'] == request.path:
                i['action'](request,handler)
                return
            elif i['method']==request.method and i['exact_path']==False and (request.path).startswith(i['path']):  
                i['action'](request,handler)
                return
            elif request.method == 'DELETE' and i['method'] == 'DELETE' and (request.path.rsplit('/',1))[0] == (i['path'].rsplit('/',1))[0]:
                i['action'](request,handler)
                return
            elif request.method == 'PATCH' and i['method'] == 'PATCH' and (request.path.rsplit('/',1))[0] == (i['path'].rsplit('/',1))[0]:
                i['action'](request,handler)
                return
        res = Response()
        res.set_status(404,'Not Found')
        res.text('Router Problem')
        handler.request.sendall(res.to_data())

        
