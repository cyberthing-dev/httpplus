
from dataclasses import dataclass
from json import loads

@dataclass
class Method:
    GET:str="GET"
    HEAD:str="HEAD"
    POST:str="POST"
    PUT:str="PUT"
    DELETE:str="DELETE"
    CONNECT:str="CONNECT"
    OPTIONS:str="OPTIONS"
    TRACE:str="TRACE"
    PATCH:str="PATCH"

@dataclass
class Status:
    # 1XX
    CONTINUE:int=100
    SWITCHING_PROTOCOLS:int=101
    PROCESSING:int=102
    EARLY_HINTS:int=103
    # 2XX
    OK:int=200
    CREATED:int=201
    ACCEPTED:int=202
    NON_AUTHORITATIVE_INFORMATION:int=203
    NO_CONTENT:int=204
    RESET_CONTENT:int=205
    PARTIAL_CONTENT:int=206
    MULTI_STATUS:int=207
    ALREADY_REPORTED:int=208
    IM_USED:int=226
    # 3XX
    MULTIPLE_CHOICES:int=300
    MOVED_PERMANENTLY:int=301
    FOUND:int=302
    SEE_OTHER:int=303
    NOT_MODIFIED:int=304
    USE_PROXY:int=305
    SWITCH_PROXY:int=306
    TEMPORARY_REDIRECT:int=307
    PERMANENT_REDIRECT:int=308
    # 4XX
    BAD_REQUEST:int=400
    UNAUTHORIZED:int=401
    PAYMENT_REQUIRED:int=402
    FORBIDDEN:int=403
    NOT_FOUND:int=404
    METHOD_NOT_ALLOWED:int=405
    NOT_ACCEPTABLE:int=406
    PROXY_AUTHENTICATION_REQUIRED:int=407
    REQUEST_TIMEOUT:int=408
    CONFLICT:int=409
    GONE:int=410
    LENGTH_REQUIRED:int=411
    PRECONDITION_FAILED:int=412
    PAYLOAD_TOO_LARGE:int=413
    URI_TOO_LONG:int=414
    UNSUPPORTED_MEDIA_TYPE:int=415
    RANGE_NOT_SATISFIABLE:int=416
    EXPECTATION_FAILED:int=417
    IM_A_TEAPOT:int=418
    MISDIRECTED_REQUEST:int=421
    UNPROCESSABLE_ENTITY:int=422
    LOCKED:int=423
    FAILED_DEPENDENCY:int=424
    TOO_EARLY:int=425
    UPGRADE_REQUIRED:int=426
    PRECONDITION_REQUIRED:int=428
    TOO_MANY_REQUESTS:int=429
    REQUEST_HEADER_FIELDS_TOO_LARGE:int=431
    UNAVAILABLE_FOR_LEGAL_REASONS:int=451
    # 5XX
    INTERNAL_SERVER_ERROR:int=500
    NOT_IMPLEMENTED:int=501
    BAD_GATEWAY:int=502
    SERVICE_UNAVAILABLE:int=503
    GATEWAY_TIMEOUT:int=504
    HTTP_VERSION_NOT_SUPPORTED:int=505
    VARIANT_ALSO_NEGOTIATES:int=506
    INSUFFICIENT_STORAGE:int=507
    LOOP_DETECTED:int=508
    NOT_EXTENDED:int=510
    NETWORK_AUTHENTICATION_REQUIRED:int=511
    NETWORK_CONNECT_TIMEOUT_ERROR:int=599

class Headers:
    def __init__(self, headers:list[bytes]):
        for header in headers:
            k,v=header.split(b":")[:2]
            self.__setattr__(k.decode().lower().replace("-","_"), v.decode().strip())

    def get(self, header:str):
        return self.__getattribute__(header)

class Request:
    def __init__(self, raw:bytes):
        self.raw=raw
        self.method:Method
        self.status:Status
        self.headers=Headers(raw.split(b"\r\n\r")[0].split(b"\r\n")[1:])

class Body:
    def __init__(self, raw:bytes):
        self.raw=raw
    
    @property
    def text(self): return str(self)
    @property
    def json(self): return dict(self)

    def __str__(self):
        return self.raw.decode()
    
    def __bytes__(self):
        return self.raw
    
    def __dict__(self):
        return loads(self.raw.decode())
