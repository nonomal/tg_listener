import asyncio
import threading
from datetime import datetime
from typing import Any

from web3 import AsyncHTTPProvider
from web3._utils.request import async_make_post_request
from web3.types import RPCEndpoint, RPCResponse


class AsyncConcurrencyHTTPProvider(AsyncHTTPProvider):
    endpoints = [
        "https://bsc-dataseed.binance.org/",
        "https://bsc-dataseed1.binance.org/",
        "https://bsc-dataseed2.binance.org/",
        "https://bsc-dataseed3.binance.org/",
        "https://bsc-dataseed4.binance.org/",
        "https://bsc-dataseed1.defibit.io/",
        "https://bsc-dataseed2.defibit.io/",
        "https://bsc-dataseed3.defibit.io/",
        "https://bsc-dataseed4.defibit.io/",
        # "https://bsc-dataseed1.ninicoin.io/",
        # "https://bsc-dataseed2.ninicoin.io/",
        # "https://bsc-dataseed3.ninicoin.io/",
        # "https://bsc-dataseed4.ninicoin.io/",
    ]
    last_time = {}
    lock = threading.Lock()
    interval = 0.2

    async def pick_endpoint(self):
        while True:
            with self.lock:
                for endpoint_uri in self.endpoints:
                    last_time: datetime = self.last_time.get(endpoint_uri, datetime.fromtimestamp(0))
                    diff = datetime.now() - last_time
                    # self.logger.debug(f"{endpoint_uri}, {diff}, {last_time}")
                    if diff.total_seconds() > self.interval:
                        self.last_time[endpoint_uri] = datetime.now()
                        return endpoint_uri
            # self.logger.debug('---- waiting: no endpoint available')
            await asyncio.sleep(0.2)

    async def make_request(self, method: RPCEndpoint, params: Any) -> RPCResponse:
        self.endpoint_uri = await self.pick_endpoint()

        self.logger.debug("Making request HTTP. URI: %s, Method: %s",
                          self.endpoint_uri, method)
        request_data = self.encode_rpc_request(method, params)
        raw_response = await async_make_post_request(
            self.endpoint_uri,
            request_data,
            **self.get_request_kwargs()
        )
        response = self.decode_rpc_response(raw_response)
        self.logger.debug("Getting response HTTP. URI: %s, "
                          "Method: %s, Response: %s",
                          self.endpoint_uri, method, response)
        return response
