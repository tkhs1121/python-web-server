import os
import re
import traceback
from socket import socket
from typing import Tuple
from threading import Thread
from datetime import datetime

from henango.http.request import HTTPRequest
from henango.http.response import HTTPResponse
from henango.urls.resolver import URLResolver
import settings

class Worker(Thread):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    STATIC_ROOT = os.path.join(BASE_DIR, "static")

    MIME_TYPES = {
        "html": "text/html; charset=UTF-8",
        "css": "text/css",
        "png": "image/png",
        "jpg": "image/jpg",
        "gif": "image/gif",
    }

    STATUS_LINES = {
        200: "200 OK",
        404: "404 Not Found",
        405: "405 Method Not Allowed",
    }

    def __init__(self, client_socket: socket, address: Tuple[str, int]):
        super().__init__()

        self.client_socket = client_socket
        self.client_address = address

    def run(self) -> None:
        try:
            request_bytes = self.client_socket.recv(4096)

            with open('server_recv.txt', 'wb') as f:
                f.write(request_bytes)

            request = self.parse_http_request(request_bytes)

            view = URLResolver().resolve(request)

            response = view(request)

            if isinstance(response.body, str):
                response.body = response.body.encode()

            response_line = self.build_response_line(response)
            response_header = self.build_response_header(response, request)
            response_bytes = (response_line + response_header + "\r\n").encode() + response.body

            self.client_socket.send(response_bytes)
        
        except Exception:
            print("=== Woker: リクエストの処理中にエラーが発生しました ===")
            traceback.print_exc()

        finally:
            print(f"=== Woker: クライエントの通信を終了します remote_address: {self.client_address} ===")
            self.client_socket.close()

    def parse_http_request(self, request: bytes) -> HTTPRequest:

        request_line, remain = request.split(b"\r\n", maxsplit=1)
        request_header, request_body = remain.split(b"\r\n\r\n", maxsplit=1)

        method, path, http_version = request_line.decode().split(" ")

        headers = {}
        for header_now in request_header.decode().split("\r\n"):
            key, value = re.split(r": *", header_now, maxsplit=1)
            headers[key] = value

        return HTTPRequest(method=method, path=path, http_version=http_version, headers=headers, body=request_body)
    
    def get_static_file_content(self, path: str) -> bytes:

        default_static_root = os.path.join(os.path.dirname(__file__), "../../static")
        static_root = getattr(settings, "STATIC_ROOT", default_static_root)

        relative_path = path.lstrip("/")
        static_file_path = os.path.join(static_root, relative_path)

        with open(static_file_path, "rb") as f:
            return f.read()

    def build_response_header(self, response: HTTPResponse, request: HTTPRequest) -> str:

        if response.content_type is None:
            if "." in request.path:
                ext = request.path.rsplit(".", maxsplit=1)[-1]

                response.content_type = self.MIME_TYPES.get(ext, "application/octet-stream")
            else:
                response.content_type = "text/html; charset=UTF-8"
    
        response_header = ""
        response_header += f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M %S GMT')}\r\n"
        response_header += "HOST: HenaServer/0.1\r\n"
        response_header += f"Content-Length: {len(response.body)}\r\n"
        response_header += "Connection: Close\r\n"
        response_header += f"Content-Type: {response.content_type}\r\n"

        return response_header
    
    def build_response_line(self, response: HTTPResponse) -> str:
        status_line = self.STATUS_LINES[response.status_code]
        return f"HTTP/1.1 {status_line}"