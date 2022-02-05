import os
import socket
from datetime import datetime
import traceback

class WebServer:

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_ROOT = os.path.join(BASE_DIR, "static")

    MIME_TYPES = {
        "html": "text/html",
        "css": "text/css",
        "png": "image/png",
        "jpg": "image/jpg",
        "gif": "image/gif",
    }

    def serve(self):
        print('===サーバを起動します===')

        try:
            server_socket = socket.socket()
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            server_socket.bind(('localhost', 8080))
            server_socket.listen(10)

            while True:
                print('===クライアントからの接続を待ちます===')
                (client_socket, address) = server_socket.accept()
                print(f'=== クライアントの接続が完了しました remote_address: {address} ===')

                try:
                    request = client_socket.recv(4096)

                    with open('server_recv.txt', 'wb') as f:
                        f.write(request)
                    
                    request_line, remain = request.split(b"\r\n", maxsplit=1)
                    request_header, request_body = remain.split(b"\r\n\r\n", maxsplit=1)

                    method, path, http_version = request_line.decode().split(" ")

                    relative_path = path.lstrip("/")

                    static_file_path = os.path.join(self.STATIC_ROOT, relative_path).replace(os.sep, "/")

                    try:
                        with open(static_file_path, "rb") as f:
                            response_body = f.read()
                        
                        response_line = "HTTP/1.1 200 OK \r\n"
                    
                    except OSError:
                        response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
                        response_line = "HTTP/1.1 404 Found\r\n"
                    
                    if "." in path:
                        ext = path.rsplit(".", maxsplit=1)[-1]
                    else:
                        ext = ""

                    content_type = self.MIME_TYPES.get(ext, "application/octet-stream")
        
                    response_header = ""
                    response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M %S GMT')}\r\n"
                    response_header += "HOST: HenaServer/0.1\r\n"
                    response_header += f"Content-Length: {len(response_body)}\r\n"
                    response_header += "Connection: Close\r\n"
                    response_header += f"Content-Type: {content_type}\r\n"

                    response = (response_line + response_header + "\r\n").encode() + response_body
                    
                    client_socket.send(response)
                    
                except Exception:
                    print("=== リクエストの処理中にエラーが発生しました ===")
                    traceback.print_exc()
                
                finally:
                    client_socket.close()
                    
        finally:
            print('=== サーバーを停止します。 ===')

if __name__ == '__main__':
    server = WebServer()
    server.serve()