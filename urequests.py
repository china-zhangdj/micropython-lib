import usocket

class Response:

    def __init__(self, f):
        self.raw = f
        self.encoding = "utf-8"
        self._cached = None

    def close(self):
        if self.raw:
            self.raw.close()
            self.raw = None
        self._cached = None

    @property
    def content(self):
        if self._cached is None:
            try:
                self._cached = self.raw.read()
            finally:
                self.raw.close()
                self.raw = None
        return self._cached

    @property
    def text(self):
        return str(self.content, self.encoding)

    def json(self):
        import ujson
        return ujson.loads(self.content)


def request(method, url, data=None, json=None, headers={}, stream=None,files={},send_cut_slice=10240,timeout=300):
    '''
    轻量级request请求（Micropython）
    :param method: 请求方法
    :param url: 请求url
    :param data: 请求体
    :param json: json数据
    :param headers: 请求头
    :param stream: None
    :param files: 文件/表单数据
    :param send_cut_slice: 文件发送切片大小
    :return:
    '''
    boundary = 'mccmicropyreqmethod'
    try:
        proto, dummy, host, path = url.split("/", 3)
    except ValueError:
        proto, dummy, host = url.split("/", 2)
        path = ""
    if proto == "http:":
        port = 80
    elif proto == "https:":
        import ussl
        port = 443
    else:
        raise ValueError("Unsupported protocol: " + proto)

    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)

    ai = usocket.getaddrinfo(host, port)
    addr = ai[0][-1]

    s = usocket.socket(timeout=timeout)
    try:
        s.connect(addr)
        if proto == "https:":
            s = ussl.wrap_socket(s, server_hostname=host)
        s.write(b"%s /%s HTTP/1.0\r\n" % (method, path))

        if files != {} :
            headers['Content-Type'] = 'multipart/form-data; boundary={}'.format(boundary)
            dbuff = ""
            files_length = 0
            for key in files.keys() :
                if files[key][0] != None :
                    fname = files[key][0]
                    cont_type = files[key][2]
                    fobj = files[key][1]
                    dbuff += '--{}\r\nContent-Disposition: form-data; name="{}"; filename="{}"\r\nContent-Type: {}\r\n\r\n'.format(boundary,key,fname,cont_type)
                    fobj.seek(0, 2)
                    file_length = fobj.tell()
                    files_length += file_length
                    dbuff += '\r\n'
                else:
                    dbuff += '--{}\r\nContent-Disposition: form-data; name="{}"\r\n\r\n{}\r\n'.format(boundary,key,files[key][1])
            dbuff += '--{}--\r\n'.format(boundary)
            dlength = len(dbuff)
            content_length = dlength + files_length
            headers['Content-Length'] = str(content_length)
        if not "Host" in headers:
            headers['Host'] = host

        if json is not None:
            assert data is None
            import ujson
            data = ujson.dumps(json)
            headers['Content-Type'] = "application/json;charset=utf-8"
        if data:
            headers['Content-Length'] =  str(len(data))


        for k in headers:
            s.write(k)
            s.write(b": ")
            s.write(headers[k])
            s.write(b"\r\n")


        s.write(b"\r\n")

        if data:
            s.write(data)

        if files != {} :
            for key in files.keys() :
                if files[key][0] != None :
                    fname = files[key][0]
                    cont_type = files[key][2]
                    fobj = files[key][1]
                    s.write('--{}\r\nContent-Disposition: form-data; name="{}"; filename="{}"\r\nContent-Type: {}\r\n\r\n'.format(boundary,key,fname,cont_type))
                    fobj.seek(0, 0)

                    read_result = fobj.read(send_cut_slice)
                    s.write(read_result)
                    while read_result != b'' :
                        read_result = fobj.read(send_cut_slice)
                        if read_result != b'' :
                            s.write(read_result)
                    s.write('\r\n')

                else:
                    s.write('--{}\r\nContent-Disposition: form-data; name="{}"\r\n\r\n{}\r\n'.format(boundary,key,files[key][1]))
            s.write('--{}--\r\n'.format(boundary))

        l = s.readline()
        protover, status, msg = l.split(None, 2)
        status = int(status)
        while True:
            l = s.readline()
            if not l or l == b"\r\n":
                break
            if l.startswith(b"Transfer-Encoding:"):
                if b"chunked" in l:
                    raise ValueError("Unsupported " + l)
            elif l.startswith(b"Location:") and not 200 <= status <= 299:
                raise NotImplementedError("Redirects not yet supported")
    except OSError:
        s.close()
        raise

    resp = Response(s)

    resp.status_code = status
    resp.reason = msg.rstrip()
    return resp


def head(url, **kw):
    return request("HEAD", url, **kw)

def get(url, **kw):
    return request("GET", url, **kw)

def post(url, **kw):
    return request("POST", url, **kw)

def put(url, **kw):
    return request("PUT", url, **kw)

def patch(url, **kw):
    return request("PATCH", url, **kw)

def delete(url, **kw):
    return request("DELETE", url, **kw)

