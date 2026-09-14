import time


class SimpleMiddleware:
    def __init__(self,app):
        self.app = app  

    def __call__(self,environ,start_response):
        start = time.time()
        print(">>> Midlleware: request entered")
        print("METHOD:", environ["REQUEST_METHOD"])
        print("PATH:", environ["PATH_INFO"])
        def custom_start_response(status,headers,exc_info=None):
            #print("ORIGINAL STATUS:",status)
            #status = "403 FORBIDDEN"
            #print("CHANGED STATUS:",status)
            headers.append(("X-My-Middleware","CandyMiddleware"))
            return start_response(status,headers,exc_info)

        response = self.app(environ,start_response)
        end = time.time()
        print("<<<MIddleware: response returned")
        print("TIME:",end-start,"Seconds")
        return response

class SecondMiddleware:
    def __init__(self,app):
        self.app = app 
    def __call__(self,environ,start_response):
        print(">>> SECOND: request entered")
        response = self.app(environ,start_response)
        print("<<< SECOND: request returned")
        return response