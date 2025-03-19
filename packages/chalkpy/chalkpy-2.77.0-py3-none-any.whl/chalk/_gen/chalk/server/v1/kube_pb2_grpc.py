# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""

import grpc

from chalk._gen.chalk.server.v1 import kube_pb2 as chalk_dot_server_dot_v1_dot_kube__pb2


class KubeServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetPodStackTraceDump = channel.unary_unary(
            "/chalk.server.v1.KubeService/GetPodStackTraceDump",
            request_serializer=chalk_dot_server_dot_v1_dot_kube__pb2.GetPodStackTraceDumpRequest.SerializeToString,
            response_deserializer=chalk_dot_server_dot_v1_dot_kube__pb2.GetPodStackTraceDumpResponse.FromString,
        )
        self.GetKubernetesEvents = channel.unary_unary(
            "/chalk.server.v1.KubeService/GetKubernetesEvents",
            request_serializer=chalk_dot_server_dot_v1_dot_kube__pb2.GetKubernetesEventsRequest.SerializeToString,
            response_deserializer=chalk_dot_server_dot_v1_dot_kube__pb2.GetKubernetesEventsResponse.FromString,
        )
        self.GetKubernetesPersistentVolumes = channel.unary_unary(
            "/chalk.server.v1.KubeService/GetKubernetesPersistentVolumes",
            request_serializer=chalk_dot_server_dot_v1_dot_kube__pb2.GetKubernetesPersistentVolumesRequest.SerializeToString,
            response_deserializer=chalk_dot_server_dot_v1_dot_kube__pb2.GetKubernetesPersistentVolumesResponse.FromString,
        )


class KubeServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetPodStackTraceDump(self, request, context):
        """GetPodStackTraceDump gets the stack trace dump from a single process running in a pod
        The process can be specified either by name or process ID
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetKubernetesEvents(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")

    def GetKubernetesPersistentVolumes(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_KubeServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "GetPodStackTraceDump": grpc.unary_unary_rpc_method_handler(
            servicer.GetPodStackTraceDump,
            request_deserializer=chalk_dot_server_dot_v1_dot_kube__pb2.GetPodStackTraceDumpRequest.FromString,
            response_serializer=chalk_dot_server_dot_v1_dot_kube__pb2.GetPodStackTraceDumpResponse.SerializeToString,
        ),
        "GetKubernetesEvents": grpc.unary_unary_rpc_method_handler(
            servicer.GetKubernetesEvents,
            request_deserializer=chalk_dot_server_dot_v1_dot_kube__pb2.GetKubernetesEventsRequest.FromString,
            response_serializer=chalk_dot_server_dot_v1_dot_kube__pb2.GetKubernetesEventsResponse.SerializeToString,
        ),
        "GetKubernetesPersistentVolumes": grpc.unary_unary_rpc_method_handler(
            servicer.GetKubernetesPersistentVolumes,
            request_deserializer=chalk_dot_server_dot_v1_dot_kube__pb2.GetKubernetesPersistentVolumesRequest.FromString,
            response_serializer=chalk_dot_server_dot_v1_dot_kube__pb2.GetKubernetesPersistentVolumesResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler("chalk.server.v1.KubeService", rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class KubeService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetPodStackTraceDump(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/chalk.server.v1.KubeService/GetPodStackTraceDump",
            chalk_dot_server_dot_v1_dot_kube__pb2.GetPodStackTraceDumpRequest.SerializeToString,
            chalk_dot_server_dot_v1_dot_kube__pb2.GetPodStackTraceDumpResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GetKubernetesEvents(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/chalk.server.v1.KubeService/GetKubernetesEvents",
            chalk_dot_server_dot_v1_dot_kube__pb2.GetKubernetesEventsRequest.SerializeToString,
            chalk_dot_server_dot_v1_dot_kube__pb2.GetKubernetesEventsResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )

    @staticmethod
    def GetKubernetesPersistentVolumes(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/chalk.server.v1.KubeService/GetKubernetesPersistentVolumes",
            chalk_dot_server_dot_v1_dot_kube__pb2.GetKubernetesPersistentVolumesRequest.SerializeToString,
            chalk_dot_server_dot_v1_dot_kube__pb2.GetKubernetesPersistentVolumesResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
