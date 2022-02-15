from typing import Optional

class HTTPResponse:
    status_code: int
    headers: dict
    content_type: Optional[str]
    body: bytes

    def __init__(
        self, 
        status_code: int = 200, 
        headers: dict = None,
        content_type: str = None, 
        body: bytes = b""
    ) -> None:

        if headers is None:
            headers = {}
            
        self.status_code = status_code
        self.content_type = content_type
        self.headers = headers
        self.body = body