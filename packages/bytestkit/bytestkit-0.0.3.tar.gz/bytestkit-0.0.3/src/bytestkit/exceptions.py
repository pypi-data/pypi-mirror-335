#!/usr/bin/env python3
# -*- encoding: utf-8 -*-


class _BaseException(Exception):
    def __init__(self, msg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._msg = msg

    def __str__(self):
        return "<%s, %s>" % (self.__class__.__name__, self._msg)

    def __repr__(self):
        return "<%s, %s>" % (self.__class__.__name__, self._msg)


class ExecuteCommandError(_BaseException):
    def __init__(self, msg: str = None):
        super().__init__(msg=msg if msg else "Failed to execute terminal command")


class InvalidRequestError(Exception):
    """
    Exception raised for returned Bybit errors.

    Attributes:
        request -- The original request that caused the error.
        message -- Explanation of the error.
        status_code -- The code number returned.
        time -- The time of the error.
        resp_headers -- The response headers from API. None, if the request caused an error locally.
    """

    def __init__(self, request, message, status_code, time, resp_headers):
        self.request = request
        self.message = message
        self.status_code = status_code
        self.time = time
        self.resp_headers = resp_headers
        super().__init__(f"{message} (ErrCode: {status_code}) (ErrTime: {time})" f".\nRequest → {request}.")


class FailedRequestError(Exception):
    """
    Exception raised for failed requests.

    Attributes:
        request -- The original request that caused the error.
        message -- Explanation of the error.
        status_code -- The code number returned.
        time -- The time of the error.
        resp_headers -- The response headers from API. None, if the request caused an error locally.
    """

    def __init__(self, request, message, status_code, time, resp_headers):
        self.request = request
        self.message = message
        self.status_code = status_code
        self.time = time
        self.resp_headers = resp_headers
        super().__init__(f"{message} (ErrCode: {status_code}) (ErrTime: {time})" f".\nRequest → {request}.")
