# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""

import grpc

from chalk._gen.chalk.server.v1 import metrics_pb2 as chalk_dot_server_dot_v1_dot_metrics__pb2


class MetricsServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetOverviewSummaryMetrics = channel.unary_unary(
            "/chalk.server.v1.MetricsService/GetOverviewSummaryMetrics",
            request_serializer=chalk_dot_server_dot_v1_dot_metrics__pb2.GetOverviewSummaryMetricsRequest.SerializeToString,
            response_deserializer=chalk_dot_server_dot_v1_dot_metrics__pb2.GetOverviewSummaryMetricsResponse.FromString,
        )


class MetricsServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetOverviewSummaryMetrics(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_MetricsServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "GetOverviewSummaryMetrics": grpc.unary_unary_rpc_method_handler(
            servicer.GetOverviewSummaryMetrics,
            request_deserializer=chalk_dot_server_dot_v1_dot_metrics__pb2.GetOverviewSummaryMetricsRequest.FromString,
            response_serializer=chalk_dot_server_dot_v1_dot_metrics__pb2.GetOverviewSummaryMetricsResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler("chalk.server.v1.MetricsService", rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class MetricsService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetOverviewSummaryMetrics(
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
            "/chalk.server.v1.MetricsService/GetOverviewSummaryMetrics",
            chalk_dot_server_dot_v1_dot_metrics__pb2.GetOverviewSummaryMetricsRequest.SerializeToString,
            chalk_dot_server_dot_v1_dot_metrics__pb2.GetOverviewSummaryMetricsResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
