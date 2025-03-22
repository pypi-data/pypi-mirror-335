import grpc
from .grpc.wafer_pb2_grpc import WaferServiceStub
from .grpc.reticle_pb2_grpc import ReticleServiceStub
from .grpc.die_pb2_grpc import DieServiceStub
from .grpc.circuit_pb2_grpc import CircuitServiceStub
from .grpc.spectrum_pb2_grpc import SpectrumServiceStub
from .grpc.result_pb2_grpc import ResultServiceStub


class TrimmingSdk:
    def __init__(self, grpc_channel: grpc.Channel):
        self.grpc_channel = grpc_channel

    @property
    def wafer(self):
        return WaferServiceStub(self.grpc_channel)

    @property
    def reticle(self):
        return ReticleServiceStub(self.grpc_channel)

    @property
    def die(self):
        return DieServiceStub(self.grpc_channel)

    @property
    def circuit(self):
        return CircuitServiceStub(self.grpc_channel)

    @property
    def result(self):
        return ResultServiceStub(self.grpc_channel)

    @property
    def spectrum(self):
        return SpectrumServiceStub(self.grpc_channel)
