class Pretty:
    def Pretty_headers(self,start_headers:str) -> dict:
        headers = {}
        start_headers = start_headers.strip().split("\n")
        for i in start_headers:
            head = i.strip().split(":",1)
            headers[head[0]] = head[1].strip()
        return headers
