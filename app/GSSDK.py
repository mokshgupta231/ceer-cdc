from __future__ import unicode_literals
import urllib.request
from urllib.request import (
    build_opener,
    HTTPHandler,
    ProxyHandler,
    install_opener,
    urlopen,
    HTTPSHandler,
)
from http.client import HTTPSConnection, HTTPS_PORT
from urllib.parse import quote_plus, urlparse
import hmac
import time
import calendar
import socket
import ssl
import copy
from hashlib import sha1
from base64 import b64decode, b64encode
from json import loads, dumps as jsonstringify
from re import search
from random import randrange

string_types = str
integer_types = int


class GSException(Exception):
    def __init__(self, value):
        self.errorMessage = value

    def __str__(self):
        return repr(self.value)


class GSRequest:
    DEFAULT_API_DOMAIN = "us1.gigya.com"
    VERSION = "3.5.2"

    _domain = ""
    _path = ""
    _traceLog = []
    _method = ""
    _proxy = ""
    _host = ""

    _apiKey = ""
    _secretKey = ""
    _userKey = ""
    _params = {}
    _useHTTPS = False
    _apiDomain = DEFAULT_API_DOMAIN

    def __init__(
        self,
        apiKey=None,
        secretKey=None,
        apiMethod=None,
        params=None,
        useHTTPS=False,
        userKey=None,
    ):
        if apiMethod is None:
            return

        self._method = apiMethod

        if params is None:
            self._params = {}
        elif isinstance(params, dict):
            self._params = copy.copy(params)
        elif isinstance(params, string_types):
            self._params = Utils.jsonparse(params)
        else:
            self._params = dict([k, v.encode("utf-8")] for k, v in params.items())

        self._domain = self._params.get("_host", self._domain)
        self._useHTTPS = useHTTPS
        self._apiKey = apiKey
        self._secretKey = secretKey
        self._userKey = userKey
        self._traceLog = list()
        self.traceField("apiMethod", apiMethod)
        self.traceField("apiKey", apiKey)

    def setParam(self, param, val):
        self._params[param] = val

    def getParams(self):
        return self._params

    def setAPIDomain(self, apiDomain=None):
        if apiDomain is None:
            self._apiDomain = self.DEFAULT_API_DOMAIN
        else:
            self._apiDomain = apiDomain

    def setProxy(self, proxy):
        self._proxy = proxy
        self.traceField("proxy", proxy)

    def send(self, timeout=None):
        if self._method[0:1] == "/":
            self._method = self._method[1:]

        if self._method.find(".") == -1:
            self._domain = "socialize." + self._apiDomain
            self._path = "/socialize." + self._method
        else:
            tokens = self._method.split(".")
            self._domain = tokens[0] + "." + self._apiDomain
            self._path = "/" + self._method

        format = self._params.get("format", None)

        if format is None:
            format = "json"
            self.setParam("format", format)
        if timeout:
            timeout = float(timeout)
            self.traceField("timeout", timeout)

        if self._method is None or (self._apiKey is None and self._userKey is None):
            return GSResponse(
                self._method, None, self._params, 400002, None, self._traceLog
            )

        try:
            self.setParam("httpStatusCodes", "false")
            self.traceField("apiKey", self._apiKey)
            self.traceField("apiMethod", self._method)
            self.traceField("params", self._params)
            self.traceField("useHTTPS", self._useHTTPS)
            self.traceField("userKey", self._userKey)
            responseStr = self.sendRequest(
                "POST",
                self._host,
                self._path,
                self._params,
                self._apiKey,
                self._secretKey,
                self._useHTTPS,
                timeout,
                self._userKey,
            )

            return GSResponse(self._method, responseStr, None, 0, None, self._traceLog)

        except Exception as ex:
            errCode = 500000
            errMsg = str(ex)
            length = len("Operation timed out")

            if errMsg[0:length] == "Operation timed out":
                errCode = 504002
                errMsg = "Request Timeout"

            return GSResponse(
                self._method, None, self._params, errCode, errMsg, self._traceLog
            )

    def sendRequest(
        self,
        httpMethod,
        domain,
        path,
        params,
        token,
        secret=None,
        useHTTPS=False,
        timeout=None,
        userKey=None,
    ):
        params["sdk"] = "python_" + self.VERSION
        protocol = "https" if (useHTTPS or not secret) else "http"
        resourceURI = protocol + "://" + self._domain + path

        timestamp = calendar.timegm(time.gmtime())
        nonce = str(SigUtils.currentTimeMillis()) + str(randrange(1000))
        httpMethod = "POST"

        if userKey:
            params["userKey"] = userKey

        if secret:
            params["apiKey"] = token
            params["timestamp"] = timestamp
            params["nonce"] = nonce

            signature = self.getOAuth1Signature(
                secret, httpMethod, resourceURI, useHTTPS, params
            )
            params["sig"] = signature
        else:
            params["oauth_token"] = token

        res = self.curl(resourceURI, params, timeout)

        return res

    def curl(self, url, params=None, timeout=None):
        queryString = self.buildQS(params)

        self.traceField("URL", url)
        self.traceField("postData", queryString)

        proto = "https" if self._useHTTPS else "http"

        if self._proxy:
            opener = build_opener(
                HTTPHandler(),
                ValidHTTPSHandler(False),
                ProxyHandler({proto: self._proxy}),
            )
        else:
            opener = build_opener(HTTPHandler(), ValidHTTPSHandler())

        queryString = queryString.encode("utf-8")

        currentOpener = urllib.request._opener
        install_opener(opener)

        if timeout:
            response = urlopen(url, queryString, timeout)
        else:
            response = urlopen(url, queryString)

        install_opener(currentOpener)

        result = response.read()
        result = result.decode("utf-8")

        return result

    def buildQS(self, params):
        queryString = ""
        amp = ""
        keys = list(params.keys())
        keys.sort()
        for key in keys:
            value = params.get(key)
            if value is not None:
                queryString += amp + key + "=" + self.UrlEncode(value)
                amp = "&"

        return queryString

    def getOAuth1Signature(
        self, key, httpMethod, url, isSecureConnection, requestParams
    ):
        baseString = self.calcOAuth1BaseString(
            httpMethod, url, isSecureConnection, requestParams
        )
        self.traceField("baseString", baseString)

        return SigUtils.calcSignature(baseString, key)

    def calcOAuth1BaseString(self, httpMethod, url, isSecureConnection, requestParams):
        normalizedUrl = ""
        u = urlparse(url)

        if isSecureConnection:
            protocol = "https"
        else:
            protocol = u.scheme.lower()

        port = u.port

        normalizedUrl += protocol + "://"
        normalizedUrl += u.hostname.lower()

        if port != None and (
            (protocol == "http" and port != 80) or (protocol == "https" and port != 443)
        ):
            normalizedUrl += ":" + port

        normalizedUrl += u.path

        queryString = self.buildQS(requestParams)

        baseString = (
            httpMethod.upper()
            + "&"
            + self.UrlEncode(normalizedUrl)
            + "&"
            + self.UrlEncode(queryString)
        )

        return baseString

    def UrlEncode(self, value):
        if value is None:
            return value
        elif isinstance(value, integer_types):
            return str(value)
        else:
            if isinstance(value, dict) or isinstance(value, list):
                str_value = jsonstringify(value)
            else:
                str_value = value.encode("utf-8")

            return quote_plus(str_value).replace("+", "%20").replace("%7E", "~")

    def traceField(self, name, value):
        if value:
            self._traceLog.append(str(name) + "=" + repr(value))


class GSResponse:
    errorCode = 0
    errorMessage = None
    rawData = ""
    data = {}
    params = None
    method = None
    traceLog = []
    errorMsgDic = {}
    errorMsgDic[400002] = "Required parameter is missing"
    errorMsgDic[500000] = "General server error"

    def getErrorCode(self):
        return self.errorCode

    def getErrorMessage(self):
        if self.errorMessage:
            return self.errorMessage
        else:
            if (self.errorCode == 0) or (not self.errorMsgDic.get(self.errorCode)):
                return ""
            else:
                return self.errorMsgDic.get(self.errorCode)

    def getResponseText(self):
        if type(self.rawData) == "bytes":
            self.rawData = self.rawData.decode(encoding="utf-8", errors="strict")
        return self.rawData

    def getData(self):
        if type(self.data) == "bytes":
            self.data = self.data.decode(encoding="utf-8", errors="strict")
        return self.data

    def getObject(self, key):
        return self.data.get(key)

    def traceField(self, name, value):
        if value:
            self.traceLog.append(str(name) + "=" + repr(value))

    def __init__(
        self,
        method,
        responseText=None,
        params=None,
        errorCode=None,
        errorMessage=None,
        traceLog=None,
    ):
        self.traceLog = traceLog
        self.method = method

        if params:
            self.params = params
        else:
            self.params = {}

        if responseText:
            self.traceField("responseText", responseText)

            self.rawData = responseText.encode("utf-8")

            if responseText.lstrip().find("{") != -1:
                self.data = Utils.jsonparse(responseText)

                if self.data:
                    self.errorCode = self.data.get("errorCode")
                    self.errorMessage = self.data.get("errorMessage")

            else:
                matches = search(r"<errorCode>([^>]+)</errorCode>", self.rawData)
                if matches:
                    errCodeStr = matches.group(1)
                    if errCodeStr:
                        self.errorCode = int(errCodeStr)
                        matches = search(
                            r"<errorMessage>([^>]+)</errorMessage>", self.rawData
                        )
                        if matches:
                            self.errorMessage = matches.group(1)

        else:
            self.errorCode = errorCode
            self.errorMessage = (
                errorMessage if errorMessage != None else self.getErrorMessage()
            )
            self.populateClientResponseText()
            self.traceField("responseText", self.rawData)

    def populateClientResponseText(self):
        if self.params.get("format") == "json":
            self.rawData = (
                "{errorCode:"
                + str(self.errorCode)
                + ',errorMessage:"'
                + self.errorMessage
                + '"}'
            )
        else:
            sb = [
                '<?xml version="1.0" encoding="utf-8"?>',
                "<"
                + self.method
                + 'Response xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:com:gigya:api http://socialize-api.gigya.com/schema" xmlns="urn:com:gigya:api">',
                "<errorCode>" + str(self.errorCode) + "</errorCode>",
                "<errorMessage>" + self.errorMessage + "</errorMessage>",
                "</" + self.method + "Response>",
            ]
            self.rawData = "\r\n".join(sb)

    def getLog(self):
        return ", ".join(self.traceLog)

    def __str__(self):
        sb = ""
        sb += "\terrorCode:"
        sb += str(self.errorCode)
        sb += "\n\terrorMessage:"
        sb += self.errorMessage
        sb += "\n\tdata:"
        sb += str(self.data)
        return sb


class ValidHTTPSConnection(HTTPSConnection):
    default_port = HTTPS_PORT

    def __init__(self, *args, **kwargs):
        HTTPSConnection.__init__(self, *args, **kwargs)
        self._context = kwargs.get("context")

    def connect(self):
        sock = socket.create_connection(
            (self.host, self.port), self.timeout, self.source_address
        )

        if self._tunnel_host:
            self.sock = sock
            self._tunnel()

        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)


class ValidHTTPSHandler(HTTPSHandler):
    def __init__(self, enable_host_check=True):
        super().__init__()
        self._enableHostCheck = enable_host_check

    def https_open(self, req):
        return self.do_open(self.get_connection, req)

    def get_connection(self, host, timeout):
        return ValidHTTPSConnection(
            host, timeout=timeout, context=self.create_context()
        )

    def create_context(self):
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = self._enableHostCheck
        return context


class SigUtils:
    @staticmethod
    def validateUserSignature(UID, timestamp, secret, signature, expiration=None):
        baseString = timestamp + "_" + UID
        expectedSig = SigUtils.calcSignature(baseString, secret)
        if expiration is None:
            return expectedSig == signature
        else:
            expired = SigUtils.signatureTimestampExpired(timestamp, expiration)
            return not expired and expectedSig == signature

    @staticmethod
    def validateUserSignatureWithExpiration(
        UID, timestamp, secret, signature, expiration
    ):
        expired = SigUtils.signatureTimestampExpired(timestamp, expiration)
        signatureValidated = SigUtils.validateUserSignature(
            UID, timestamp, secret, signature
        )
        return not expired and signatureValidated

    @staticmethod
    def validateFriendSignature(
        UID, timestamp, friendUID, secret, signature, expiration=None
    ):
        baseString = timestamp + "_" + friendUID + "_" + UID
        expectedSig = SigUtils.calcSignature(baseString, secret)
        if expiration is None:
            return expectedSig == signature
        else:
            expired = SigUtils.signatureTimestampExpired(timestamp, expiration)
            return not expired and expectedSig == signature

    @staticmethod
    def validateFriendSignatureWithExpiration(
        UID, timestamp, friendUID, secret, signature, expiration
    ):
        expired = SigUtils.signatureTimestampExpired(timestamp, expiration)
        signatureValidated = SigUtils.validateFriendSignature(
            UID, timestamp, friendUID, secret, signature
        )
        return not expired and signatureValidated

    @staticmethod
    def getDynamicSessionSignature(gltCookie, timeoutInSeconds, secret):
        expirationTimeUnixMS = calendar.timegm(time.gmtime()) + timeoutInSeconds
        expirationTimeUnixString = str(expirationTimeUnixMS)
        unsignedExpString = gltCookie + "_" + expirationTimeUnixString
        signedExpString = SigUtils.calcSignature(unsignedExpString, secret)
        ret = expirationTimeUnixString + "_" + signedExpString
        return ret

    @staticmethod
    def getDynamicSessionSignatureUserSigned(
        gltCookie, timeoutInSeconds, userKey, secret
    ):
        expirationTimeUnixMS = calendar.timegm(time.gmtime()) + timeoutInSeconds
        expirationTimeUnixString = str(expirationTimeUnixMS)
        unsignedExpString = gltCookie + "_" + expirationTimeUnixString + "_" + userKey
        signedExpString = SigUtils.calcSignature(unsignedExpString, secret)
        ret = expirationTimeUnixString + "_" + userKey + "_" + signedExpString
        return ret

    @staticmethod
    def calcSignature(baseString, key):
        encodedBase = baseString.encode("utf-8")
        encodedKey = key.encode("utf-8")
        rawHmac = hmac.new(b64decode(encodedKey), encodedBase, sha1).digest()
        signature = b64encode(rawHmac)
        signature = signature.decode("utf-8")

        return signature

    @staticmethod
    def currentTimeMillis():
        return int(round(time.time() * 1000))

    @staticmethod
    def signatureTimestampExpired(signatureTimestampExpired, expiration):
        now = int(round(time.time()))
        timestamp = int(signatureTimestampExpired)
        return abs(now - timestamp) > expiration


class Utils:
    @staticmethod
    def jsonparse(source):
        return loads(source)
