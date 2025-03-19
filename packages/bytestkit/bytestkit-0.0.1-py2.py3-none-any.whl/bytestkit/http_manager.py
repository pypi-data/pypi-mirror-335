#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import base64
import hashlib
import hmac
import json
import time
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime as dt
from datetime import timezone
from json.decoder import JSONDecodeError
from typing import final

import requests
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from requests import Response

from .exceptions import FailedRequestError
from .logger import get_logger

__all__ = "generate_signature", "_HttpManager"


def generate_signature(secret: str, encrypt_text: str, use_rsa_authentication: bool = False):
    def _generate_hmac():
        h = hmac.new(
            bytes(secret.strip(), "utf-8"),
            encrypt_text.encode("utf-8"),
            hashlib.sha256,
        )
        return h.hexdigest()

    def _generate_rsa():
        h = SHA256.new(encrypt_text.encode("utf-8"))
        encoded_signature = base64.b64encode(PKCS1_v1_5.new(RSA.importKey(secret)).sign(h))
        return encoded_signature.decode()

    return _generate_rsa() if use_rsa_authentication else _generate_hmac()


@dataclass
class _HttpManager(ABC):
    """
    Bybit OpenAPI Http Manager

    *[Usage]
    1. Public Market API
    class MarketReq(_HttpManager):
        def orderbook(self, symbol):
            return self.send_request("GET", "/v5/market/orderbook", {"category": "linear", "symbol": symbol})
    public = MarketReq("https://api.bybit.com")
    public.orderbook(symbol)

    2. Private API
    class TradeReq(_HttpManager):
        def place_order(self, payload):
            return self.send_request("POST", "/v5/order/create", payload)
    private = TradeReq("https://api.bybit.com", "api_key", "api_secret"})
    private.place_order("BTCUSDT", payload)
    """

    base_url: str = field(metadata={"description": "接口请求域名, 格式: https://xxx.xxx.xxx"})
    api_key: str = field(default=None, repr=False, compare=False)
    api_secret: str = field(default=None, repr=False, compare=False)
    recv_window: bool = field(default=10000)
    use_rsa_authentication: bool = field(default=False, metadata={"description": "设置为True, 则表示使用RSA签名"})
    max_retries: bool = field(default=3, metadata={"description": "接口请求最大重试次数"})
    retry_delay: bool = field(default=1, metadata={"description": "接口请求重试间隔"})
    force_retry: bool = field(default=False, metadata={"description": "不论接口请求返回何种错误(如网络错误/JSON反序列化错误等), 始终重试"})
    timeout: int = field(default=5, metadata={"description": "请求超时时间"})
    log_requests: bool = field(default=False, metadata={"description": "设置True, 则会将接口请求体和请求头打印出来, 便于debug"})

    def __post_init__(self):
        self.logger = get_logger(__name__)

        self._format_base_url()
        self._client = requests.Session()
        self._client.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
        self.logger.debug("Initialize HTTP session success.")

    @final
    def _auth(self, payload: dict, timestamp: int):
        if self.api_key is None or self.api_secret is None:
            msg = "访问私有接口, 需要传入API密钥信息"
            self.logger.critical(msg)
            raise PermissionError(msg)

        encrypt_text = str(timestamp) + self.api_key.strip() + str(self.recv_window) + payload
        return generate_signature(self.api_secret, encrypt_text, self.use_rsa_authentication)

    def _format_base_url(self) -> str:
        if "http" not in self.base_url:
            self.logger.warning("传入的域名没有包含Scheme部分, 将自动补全为https")
            self.base_url = "https://" + self.base_url

        if self.base_url.endswith("/"):
            self.base_url = self.base_url[:-1]

    @staticmethod
    def prepare_payload(method, payload):
        """
        Prepares the request payload and validates parameter value types.
        """

        def cast_values():
            string_params = ["qty", "price", "triggerPrice", "takeProfit", "stopLoss"]
            integer_params = ["positionIdx"]
            for key, value in payload.items():
                if key in string_params:
                    if not isinstance(value, str):
                        payload[key] = str(value)
                elif key in integer_params:
                    if not isinstance(value, int):
                        payload[key] = int(value)

        if method == "GET":
            payload = "&".join([str(k) + "=" + str(v) for k, v in sorted(payload.items()) if v is not None])
            return payload

        cast_values()
        return json.dumps(payload)

    @final
    def send_request(self, method: str = None, path: str = None, payload: dict = None, auth: bool = None) -> Response:
        """
        Send the request.

        @usage:
        self.send_request("POST",f"{domain}/v5/position/list",{"category": "linear", "symbol": "XRPUSDT"})
        """
        method = method.upper()
        endpoint = self.base_url + path if path.startswith("/") else f"/{path}"

        if payload is None:
            payload = {}

        recv_window = self.recv_window

        for i in payload.keys():
            if isinstance(payload[i], float) and payload[i] == int(payload[i]):
                payload[i] = int(payload[i])

            payload = {key: value for key, value in payload.items() if value is not None}

        retries_attempted = self.max_retries if self.max_retries >= 1 else 1
        req_params = None

        while True:
            retries_attempted -= 1
            if retries_attempted < 0:
                raise FailedRequestError(
                    request=f"{method} {endpoint}: {req_params}",
                    message=f"Bad Request. 重试超过最大次数[{retries_attempted}]后仍然请求失败.",
                    status_code=400,
                    time=dt.now(timezone.utc).strftime("%H:%M:%S"),
                    resp_headers=None,
                )

            retries_remaining = f"{retries_attempted} retries remain."
            req_params = self.prepare_payload(method, payload)

            headers = {"Content-Type": "application/json"}
            if auth is None:
                auth = False if "/v5/market" in endpoint else True

            if auth:
                timestamp = self.get_server_timestamp()
                signature = self._auth(req_params, timestamp)
                headers.update(
                    {
                        "X-BAPI-API-KEY": self.api_key,
                        "X-BAPI-SIGN": signature,
                        "X-BAPI-SIGN-TYPE": "2",
                        "X-BAPI-TIMESTAMP": str(timestamp),
                        "X-BAPI-RECV-WINDOW": str(recv_window),
                    }
                )

            if method == "GET":
                if req_params:
                    r = self._client.prepare_request(requests.Request(method, endpoint + f"?{req_params}", headers=headers))
                else:
                    r = self._client.prepare_request(requests.Request(method, endpoint, headers=headers))
            else:
                r = self._client.prepare_request(requests.Request(method, endpoint, data=req_params, headers=headers))

            # Log the request.
            if self.log_requests:
                if req_params:
                    self.logger.debug(f"Request -> {method} {endpoint}. Body: {req_params}. " f"Headers: {r.headers}")
                else:
                    self.logger.debug(f"Request -> {method} {endpoint}. Headers: {r.headers}")

            try:
                resp = self._client.send(r, timeout=self.timeout)
            except (
                requests.exceptions.ReadTimeout,
                requests.exceptions.SSLError,
                requests.exceptions.ConnectionError,
            ) as e:
                if self.force_retry:
                    self.logger.error(f"{repr(e)}. {retries_remaining}")
                    time.sleep(self.retry_delay)
                    continue
                raise e

            if resp.status_code != 200:
                if resp.status_code == 403:
                    error_msg = "调用API触发限频或所在区域不允许"
                else:
                    error_msg = f"HTTP status code is not 200: {resp.status_code}"
                raise FailedRequestError(
                    request=f"{method} {endpoint}: {req_params}",
                    message=error_msg,
                    status_code=resp.status_code,
                    time=dt.now(timezone.utc).strftime("%H:%M:%S"),
                    resp_headers=resp.headers,
                )

            try:
                _ = resp.json()
            except JSONDecodeError as e:
                if self.force_retry:
                    self.logger.error(f"{repr(e)}. {retries_remaining}")
                    time.sleep(self.retry_delay)
                    continue
                raise FailedRequestError(
                    request=f"{method} {endpoint}: {req_params}",
                    message=f"响应数据反序列化失败: {resp.text}",
                    status_code=409,
                    time=dt.now(timezone.utc).strftime("%H:%M:%S"),
                    resp_headers=resp.headers,
                ) from e

            return resp

    def get_server_timestamp(self) -> int:
        try:
            url = self.base_url + "/v5/market/time"
            resp = requests.get(url, timeout=3)
            timestamp = int(resp.json()["result"]["timeSecond"])
        except Exception as e:
            self.logger.error(f"从服务器端获取时间戳失败: {repr(e)}, resp: {resp.text}")
            timestamp = int(time.time())

        return timestamp * 10**3
