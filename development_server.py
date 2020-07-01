# This is a simple HTTP server implementation to serve an Single Page
# Application (SPA).
#
# It works by serving the requested resource if it exists, falling back to the
# index.html file if it does not.
#
# Usage: python3 development_server.py

from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer


class SPAHandler(BaseHTTPRequestHandler):
    def do_GET(s):
        s.send_response(200)
        s.end_headers()

        try:
            with open('.' + s.path, 'rb') as index:
                s.wfile.write(index.read())
        except (IsADirectoryError, FileNotFoundError):
            with open('index.html', 'rb') as index:
                s.wfile.write(index.read())


if __name__ == '__main__':
    PORT = 8000
    with TCPServer(("", PORT), SPAHandler) as httpd:
        print("Serving at port", PORT)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

        httpd.server_close()

