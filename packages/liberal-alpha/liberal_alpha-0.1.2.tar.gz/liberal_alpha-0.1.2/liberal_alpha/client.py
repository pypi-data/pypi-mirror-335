import grpc
import json
import time
import threading
from .config import SDKConfig
from .exceptions import ConnectionError, RequestError

# Import generated gRPC protobuf code
try:
    from proto import service_pb2, service_pb2_grpc
except ImportError:
    raise ImportError(
        "Error: Could not import protobuf modules. Please generate them first."
        "\n  python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/service.proto"
    )


class LiberalAlphaClient:
    """Liberal Alpha SDK Client for sending data via gRPC"""

    def __init__(self, host=None, port=None, rate_limit_enabled=None):
        """Initialize the SDK with given options"""
        
        # 如果参数未提供，则使用默认值
        self.host = host if host is not None else "127.0.0.1"
        self.port = port if port is not None else 8128
        self.rate_limit_enabled = rate_limit_enabled if rate_limit_enabled is not None else True

        self._lock = threading.Lock()

        try:
            # Establish gRPC channel
            self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
            self.stub = service_pb2_grpc.JsonServiceStub(self.channel)

            # Test connection
            grpc.channel_ready_future(self.channel).result(timeout=5)

        except grpc.RpcError as e:
            raise ConnectionError(details=str(e))

    def send_data(self, identifier: str, data: dict, record_id: str):
        """Send data to gRPC server"""
        return self._send_request(identifier, data, "raw", record_id)

    def send_alpha(self, identifier: str, data: dict, record_id: str):
        """Send alpha data to gRPC server"""
        return self._send_request(identifier, data, "raw", record_id)

    def _send_request(self, identifier: str, data: dict, event_type: str, record_id: str):
        """Internal function to send data via gRPC"""
        with self._lock:
            try:
                current_time_ms = int(time.time() * 1000)  # ✅ 使用毫秒级时间戳
                metadata = {
                    "source": "liberal_alpha_sdk",
                    "entry_id": identifier,
                    "record_id": record_id,   
                    "timestamp_ms": str(current_time_ms)  # ✅ 传递 timestamp_ms
                }
                request = service_pb2.JsonRequest(
                    json_data=json.dumps(data),
                    event_type=event_type,
                    timestamp=current_time_ms,  # ✅ 使用毫秒级时间戳
                    metadata=metadata
                )
                
                response = self.stub.ProcessJson(request)  # 发送 gRPC 请求
                
                print(f"📡 gRPC Response: {response}")  # 确保 gRPC 响应被打印
                
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


# Global instance
liberal = None  

def initialize(host=None, port=None, rate_limit_enabled=None):
    """初始化 SDK，支持带参数和默认初始化"""
    global liberal
    
    # 初始化 SDK
    liberal = LiberalAlphaClient(host, port, rate_limit_enabled)
    print(f"✅ SDK 初始化成功: liberal={liberal}")
