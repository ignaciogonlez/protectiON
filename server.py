from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        print("\n=== HEADERS ===")
        print(self.headers)
        print("=== FIRST 256 BYTES OF BODY ===")
        print(body[:256], "…", len(body), "bytes total\n")
        self.send_response(200)
        self.end_headers()

print("Echo-server en http://0.0.0.0:8000")
HTTPServer(('0.0.0.0', 8000), Handler).serve_forever()
