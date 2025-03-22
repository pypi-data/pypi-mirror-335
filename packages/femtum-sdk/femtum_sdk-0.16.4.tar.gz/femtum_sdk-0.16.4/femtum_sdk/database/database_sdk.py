import time
from femtum_sdk.database.trimming_sdk import TrimmingSdk
import grpc
from .grpc.health_pb2_grpc import HealthServiceStub
from .grpc.health_pb2 import HealthDto
from google.protobuf.empty_pb2 import Empty


class FemtumDatabaseSdk:
    def __init__(self, hostUrl: str = "localhost:5208"):
        self.hostUrl = hostUrl

    def __enter__(self):
        self.grpc_channel = self.__create_grpc_channel()
        self.grpc_channel.__enter__()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.grpc_channel.__exit__(exc_type, exc_val, exc_tb)

    @property
    def health(self):
        return HealthServiceStub(self.grpc_channel)

    @property
    def trimming(self) -> TrimmingSdk:
        return TrimmingSdk(self.grpc_channel)

    def is_up(self):
        try:
            health: HealthDto = self.health.GetHealth(Empty())
            return health.status == "Up"
        except Exception:
            return False

    def wait_until_up(self, timeout=5):
        start_time = time.time()
        while not self.is_up():
            if time.time() - start_time > timeout:
                raise TimeoutError(
                    "API server did not start within the timeout period."
                )
            time.sleep(0.1)

    def close(self):
        self.grpc_channel.close()

    def __create_grpc_channel(self):
        return grpc.insecure_channel(self.hostUrl)
