# liberal_alpha/client.py
import grpc
import json
import time
import threading
import logging
import asyncio

from .config import SDKConfig
from .exceptions import ConnectionError, RequestError
from .proto import service_pb2, service_pb2_grpc
from .subscriber import main_async  # 从 subscriber 模块引入
from .crypto import get_public_key_from_private

logger = logging.getLogger(__name__)

class LiberalAlphaClient:
    """Liberal Alpha SDK Client for sending data via gRPC and subscribing to WebSocket data."""
    
    def __init__(self, host=None, port=None, rate_limit_enabled=None):
        self.host = host if host is not None else "127.0.0.1"
        self.port = port if port is not None else 8128
        self.rate_limit_enabled = rate_limit_enabled if rate_limit_enabled is not None else True
        self._lock = threading.Lock()
        try:
            self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
            self.stub = service_pb2_grpc.JsonServiceStub(self.channel)
            grpc.channel_ready_future(self.channel).result(timeout=5)
        except grpc.RpcError as e:
            raise ConnectionError(details=str(e))
    
    def send_data(self, identifier: str, data: dict, record_id: str):
        return self._send_request(identifier, data, "raw", record_id)
    
    def send_alpha(self, identifier: str, data: dict, record_id: str):
        return self._send_request(identifier, data, "raw", record_id)
    
    def _send_request(self, identifier: str, data: dict, event_type: str, record_id: str):
        with self._lock:
            try:
                current_time_ms = int(time.time() * 1000)
                metadata = {
                    "source": "liberal_alpha_sdk",
                    "entry_id": identifier,
                    "record_id": record_id,
                    "timestamp_ms": str(current_time_ms)
                }
                request = service_pb2.JsonRequest(
                    json_data=json.dumps(data),
                    event_type=event_type,
                    timestamp=current_time_ms,
                    metadata=metadata
                )
                response = self.stub.ProcessJson(request)
                logger.info(f"gRPC Response: {response}")
                return {
                    "status": response.status,
                    "message": response.message,
                    "result": json.loads(response.result_json) if response.result_json else None,
                    "error": response.error if response.error else None
                }
            except grpc.RpcError as e:
                raise RequestError(
                    message="Failed to send gRPC request",
                    code=e.code().value if e.code() else None,
                    details=str(e.details())
                )
    
    def subscribe_data(self, api_key, base_url="http://34.143.214.250:8080", wallet=None, private_key=None, record_id=None, max_reconnect=5):
        if private_key:
            try:
                pub_info = get_public_key_from_private(private_key)
                logger.info(f"Detected private key; using wallet address: {pub_info['address']}")
            except Exception as e:
                logger.error(f"Error processing private key: {e}")
                private_key = None
        try:
            asyncio.run(
                main_async(api_key=api_key, base_url=base_url, wallet_address=wallet, private_key=private_key, record_id=record_id, max_reconnect=max_reconnect)
            )
        except KeyboardInterrupt:
            logger.info("Subscription interrupted by user")
        except Exception as e:
            logger.error(f"Error during subscription: {e}")

liberal = None

def initialize(host=None, port=None, rate_limit_enabled=None):
    global liberal
    liberal = LiberalAlphaClient(host, port, rate_limit_enabled)
    logger.info(f"SDK initialized: liberal={liberal}")
