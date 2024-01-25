from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading


class MyHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(self.collector.deployments()).encode())
        elif self.path == '/health':
            if self.mainThread.is_alive():
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'OK')
            else:
                self.send_response(500)
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Page not found')


class Webserver:
    def __init__(self, mainThread) -> None:
        self.mainThread = mainThread
        pass

    def start(self, port =80):
        httpd = HTTPServer(('0.0.0.0', port), MyHTTPRequestHandler)
        httpd.RequestHandlerClass.mainThread = self.mainThread
        t = threading.Thread(target=httpd.serve_forever)
        t.start()
        # httpd.serve_forever()
        print(f'Server started on http://localhost:{port}')
        pass