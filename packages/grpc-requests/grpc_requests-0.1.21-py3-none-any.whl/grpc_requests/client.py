import logging
from enum import Enum
from functools import partial
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Union,
)

import grpc
from google.protobuf import descriptor_pb2, message_factory
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf.descriptor import MethodDescriptor, ServiceDescriptor
from google.protobuf.descriptor_pb2 import ServiceDescriptorProto
from google.protobuf.json_format import MessageToDict, ParseDict
from grpc_reflection.v1alpha import reflection_pb2, reflection_pb2_grpc

from .utils import describe_descriptor, load_data

import importlib.metadata
from typing import (
    Protocol,
    TypedDict,  # pylint: disable=no-name-in-module
)


def get_metadata(package_name: str):
    return importlib.metadata.version(package_name)


protobuf_version = get_metadata("protobuf").split(".")
get_message_class_supported = (
    int(protobuf_version[0]) >= 4 and int(protobuf_version[1]) >= 22
)
if get_message_class_supported:
    from google.protobuf.message_factory import GetMessageClass

logger = logging.getLogger(__name__)


class DescriptorImport:
    def __init__(
        self,
    ):
        pass


def make_request(*requests):
    for r in requests:
        yield r


def reflection_request(channel, requests):
    stub = reflection_pb2_grpc.ServerReflectionStub(channel)
    responses = stub.ServerReflectionInfo(make_request(requests))
    try:
        for resp in responses:
            yield resp
    except grpc._channel._Rendezvous as err:
        logger.exception(err)


PathLikeString = str


class CredentialsInfo(TypedDict):
    root_certificates: Union[None, PathLikeString, bytes]
    private_key: Union[None, PathLikeString, bytes]
    certificate_chain: Union[None, PathLikeString, bytes]


class BaseClient:
    def __init__(
        self,
        endpoint,
        symbol_db=None,
        descriptor_pool=None,
        channel_options=None,
        ssl=False,
        compression=None,
        credentials: Optional[CredentialsInfo] = None,
        interceptors=None,
        **kwargs,
    ):
        self.endpoint = endpoint
        self._desc_pool = descriptor_pool or _descriptor_pool.Default()
        self.compression = compression
        self.channel_options = channel_options
        if ssl:
            _credentials = None
            if credentials:
                _credentials = {
                    k: load_data(v) if isinstance(v, str) else v
                    for k, v in credentials.items()
                }

            self._channel = grpc.secure_channel(
                endpoint,
                grpc.ssl_channel_credentials(**_credentials),  # type: ignore
                options=self.channel_options,
                compression=self.compression,
            )
        else:
            self._channel = grpc.insecure_channel(
                endpoint, options=self.channel_options, compression=self.compression
            )

        if interceptors:
            self._channel = grpc.intercept_channel(self._channel, *interceptors)

    @property
    def channel(self):
        return self._channel

    @classmethod
    def get_by_endpoint(cls, endpoint, **kwargs):
        global _cached_clients
        if endpoint not in _cached_clients:
            _cached_clients[endpoint] = cls(endpoint, **kwargs)
        return _cached_clients[endpoint]

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._channel._close()
        except Exception as e:  # pylint: disable=bare-except
            logger.warning("can not close channel", exc_info=e)
        return False

    def __del__(self):
        if self._channel:
            try:
                del self._channel
            except Exception as e:  # pylint: disable=bare-except
                logger.warning("can not delete channel", exc_info=e)


class MessageParsersProtocol(Protocol):
    def parse_request_data(self, request_data, input_type): ...

    def parse_stream_requests(self, stream_requests_data: Iterable, input_type): ...

    def parse_response(self, response): ...

    def parse_stream_responses(self, responses: Iterable): ...


class MessageParsers(MessageParsersProtocol):
    def parse_request_data(self, request_data, input_type):
        _data = request_data or {}
        request = ParseDict(_data, input_type()) if isinstance(_data, dict) else _data
        return request

    def parse_stream_requests(self, stream_requests_data: Iterable, input_type):
        for request_data in stream_requests_data:
            yield self.parse_request_data(request_data or {}, input_type)

    def parse_response(self, response):
        return MessageToDict(response, preserving_proto_field_name=True)

    def parse_stream_responses(self, responses: Iterable):
        for resp in responses:
            yield self.parse_response(resp)


class CustomArgumentParsers(MessageParsersProtocol):
    _message_to_dict_kwargs: Optional[Dict[str, Any]]
    _parse_dict_kwargs: Optional[Dict[str, Any]]

    def __init__(
        self,
        message_to_dict_kwargs: Optional[Dict[str, Any]] = None,
        parse_dict_kwargs: Optional[Dict[str, Any]] = None,
    ):
        self._message_to_dict_kwargs = message_to_dict_kwargs or {}
        self._parse_dict_kwargs = parse_dict_kwargs or {}

    def parse_request_data(self, request_data, input_type):
        _data = request_data or {}
        if isinstance(_data, dict):
            request = ParseDict(_data, input_type(), **self._parse_dict_kwargs)
        else:
            request = _data
        return request

    def parse_stream_requests(self, stream_requests_data: Iterable, input_type):
        for request_data in stream_requests_data:
            yield self.parse_request_data(request_data or {}, input_type)

    def parse_response(self, response):
        return MessageToDict(response, **self._message_to_dict_kwargs)

    def parse_stream_responses(self, responses: Iterable):
        for resp in responses:
            yield self.parse_response(resp)


class MethodType(Enum):
    UNARY_UNARY = "unary_unary"
    STREAM_UNARY = "stream_unary"
    UNARY_STREAM = "unary_stream"
    STREAM_STREAM = "stream_stream"

    @property
    def is_unary_request(self):
        return "unary_" in self.value

    @property
    def is_unary_response(self):
        return "_unary" in self.value


class MethodMetaData(NamedTuple):
    input_type: Any
    output_type: Any
    method_type: MethodType
    handler: Any
    descriptor: MethodDescriptor
    parsers: MessageParsersProtocol

    @property
    def request_parser(self):
        if self.method_type.is_unary_request:
            return self.parsers.parse_request_data
        else:
            return self.parsers.parse_stream_requests

    @property
    def response_parser(self):
        if self.method_type.is_unary_response:
            return self.parsers.parse_response
        else:
            return self.parsers.parse_stream_responses


MethodTypeMatch: Dict[Tuple[bool, bool], MethodType] = {
    (False, False): MethodType.UNARY_UNARY,
    (True, False): MethodType.STREAM_UNARY,
    (False, True): MethodType.UNARY_STREAM,
    (True, True): MethodType.STREAM_STREAM,
}


class BaseGrpcClient(BaseClient):
    def __init__(
        self,
        endpoint,
        symbol_db=None,
        descriptor_pool=None,
        lazy=False,
        ssl=False,
        compression=None,
        skip_check_method_available=False,
        message_parsers: Optional[MessageParsersProtocol] = None,
        **kwargs,
    ):
        super().__init__(
            endpoint,
            symbol_db,
            descriptor_pool,
            ssl=ssl,
            compression=compression,
            **kwargs,
        )
        self._service_names: Optional[List] = None
        self._lazy = lazy
        self.has_server_registered = False
        self._skip_check_method_available = skip_check_method_available
        self._message_parsers = message_parsers if message_parsers else MessageParsers()
        self._service_methods_meta: Dict[str, Dict[str, MethodMetaData]] = {}

    def _get_service_names(self):
        raise NotImplementedError()

    def check_method_available(
        self, service, method, method_type: Optional[MethodType] = None
    ):
        if self._skip_check_method_available:
            return True
        if not self.has_server_registered:
            self.register_all_service()
        logger.debug(service)
        methods_meta = self._service_methods_meta.get(service)
        logger.debug(methods_meta)
        if not methods_meta:
            raise ValueError(
                f"{self.endpoint} server doesn't support {service}. Available services {self.service_names}"
            )

        if method not in methods_meta:
            raise ValueError(
                f"{service} doesn't support {method} method. Available methods {methods_meta.keys()}"
            )
        if method_type and method_type != methods_meta[method].method_type:
            raise ValueError(
                f"{method} is {methods_meta[method].method_type.value} not {method_type.value}"
            )
        return True

    def _register_methods(
        self, service_descriptor: ServiceDescriptor
    ) -> Dict[str, MethodMetaData]:
        svc_desc_proto = ServiceDescriptorProto()
        service_descriptor.CopyToProto(svc_desc_proto)
        service_full_name = service_descriptor.full_name
        metadata: Dict[str, MethodMetaData] = {}
        for method_proto in svc_desc_proto.method:
            method_name = method_proto.name
            method_desc: MethodDescriptor = service_descriptor.methods_by_name[
                method_name
            ]

            if get_message_class_supported:
                input_type = GetMessageClass(method_desc.input_type)
                output_type = GetMessageClass(method_desc.output_type)
            else:
                msg_factory = message_factory.MessageFactory(self._desc_pool)
                input_type = msg_factory.GetPrototype(method_desc.input_type)
                output_type = msg_factory.GetPrototype(method_desc.output_type)

            method_type = MethodTypeMatch[
                (method_proto.client_streaming, method_proto.server_streaming)
            ]

            method_register_func = getattr(self.channel, method_type.value)
            handler = method_register_func(
                method=self._make_method_full_name(service_full_name, method_name),
                request_serializer=input_type.SerializeToString,
                response_deserializer=output_type.FromString,
            )
            metadata[method_name] = MethodMetaData(
                method_type=method_type,
                input_type=input_type,
                output_type=output_type,
                handler=handler,
                descriptor=method_desc,
                parsers=self._message_parsers,
            )
        return metadata

    def register_service(self, service_name):
        logger.debug(f"start {service_name} registration")
        try:
            svc_desc = self.get_service_descriptor(service_name)
            self._service_methods_meta[service_name] = self._register_methods(svc_desc)
        except KeyError:
            logger.debug(
                f"{service_name} not found in descriptor pool, methods will not be registered"
            )
        logger.debug(f"end {service_name} registration")

    def register_all_service(self):
        for service in self.service_names:
            self.register_service(service)
        self.has_server_registered = True

    @property
    def service_names(self):
        if self._service_names is None:
            self._service_names = self._get_service_names()
        return self._service_names

    def get_methods_meta(self, service_name: str):
        if (
            self._lazy
            and service_name in self.service_names
            and service_name not in self._service_methods_meta
        ):
            self.register_service(service_name)

        try:
            return self._service_methods_meta[service_name]
        except KeyError as err:
            raise ValueError(f"{service_name} service not found on server") from err

    @staticmethod
    def _make_method_full_name(service, method):
        return f"/{service}/{method}"

    def _request(self, service, method, request, raw_output=False, **kwargs):
        # does not check request is available
        method_meta = self.get_method_meta(service, method)

        _request = method_meta.request_parser(request, method_meta.input_type)
        result = method_meta.handler(_request, **kwargs)

        if raw_output:
            return result
        else:
            return method_meta.response_parser(result)

    def request(self, service, method, request=None, raw_output=False, **kwargs):
        self.check_method_available(service, method)
        return self._request(service, method, request, raw_output, **kwargs)

    def unary_unary(self, service, method, request=None, raw_output=False, **kwargs):
        self.check_method_available(service, method, MethodType.UNARY_UNARY)
        return self._request(service, method, request, raw_output, **kwargs)

    def unary_stream(self, service, method, request=None, raw_output=False, **kwargs):
        self.check_method_available(service, method, MethodType.UNARY_STREAM)
        return self._request(service, method, request, raw_output, **kwargs)

    def stream_unary(self, service, method, requests, raw_output=False, **kwargs):
        self.check_method_available(service, method, MethodType.STREAM_UNARY)
        return self._request(service, method, requests, raw_output, **kwargs)

    def stream_stream(self, service, method, requests, raw_output=False, **kwargs):
        self.check_method_available(service, method, MethodType.STREAM_STREAM)
        return self._request(service, method, requests, raw_output, **kwargs)

    def get_service_descriptor(self, service):
        """
        Retrieve the service descriptor for a given service name.

        :param service: The name of the service to retrieve the descriptor for.
        :return: The service descriptor.
        :throws KeyError: If the service is not found in the descriptor pool.
        """
        return self._desc_pool.FindServiceByName(service)

    def describe_request(self, service, method):
        return describe_descriptor(
            self.get_method_descriptor(service, method).input_type
        )

    def describe_response(self, service, method):
        return describe_descriptor(
            self.get_method_descriptor(service, method).output_type
        )

    def get_method_descriptor(self, service, method):
        svc_desc = self.get_service_descriptor(service)
        return svc_desc.FindMethodByName(method)

    def get_method_meta(self, service: str, method: str) -> MethodMetaData:
        # add lazy mode & exception
        return self._service_methods_meta[service][method]

    def make_handler_argument(self, service: str, method: str):
        data_type = self.get_method_meta(service, method)
        return {
            "method": self._make_method_full_name(service, method),
            "request_serializer": data_type.input_type.SerializeToString,
            "response_deserializer": data_type.output_type.FromString,
        }

    def service(self, name):
        if name in self.service_names:
            return ServiceClient(client=self, service_name=name)
        else:
            raise ValueError(
                f"{name} is not a supported service. Available services are {self.service_names}"
            )


class ReflectionClient(BaseGrpcClient):
    def __init__(
        self,
        endpoint,
        symbol_db=None,
        descriptor_pool=None,
        lazy=False,
        ssl=False,
        compression=None,
        **kwargs,
    ):
        super().__init__(
            endpoint,
            symbol_db,
            descriptor_pool,
            ssl=ssl,
            lazy=lazy,
            compression=compression,
            **kwargs,
        )
        self.reflection_stub = reflection_pb2_grpc.ServerReflectionStub(self.channel)
        if not self._lazy:
            self.register_all_service()

    def _reflection_request(self, *requests):
        responses = self.reflection_stub.ServerReflectionInfo((r for r in requests))
        return responses

    def _reflection_single_request(self, request):
        results = list(self._reflection_request(request))
        if len(results) != 1:
            raise ValueError("response has more than one result")
        return results[0]

    def _get_service_names(self):
        request = reflection_pb2.ServerReflectionRequest(list_services="")
        resp = self._reflection_single_request(request)
        services = tuple([s.name for s in resp.list_services_response.service])
        return services

    def get_file_descriptors_by_name(self, name):
        request = reflection_pb2.ServerReflectionRequest(file_by_filename=name)
        result = self._reflection_single_request(request)
        return [
            descriptor_pb2.FileDescriptorProto.FromString(proto)
            for proto in result.file_descriptor_response.file_descriptor_proto
        ]

    def get_file_descriptors_by_symbol(self, symbol):
        request = reflection_pb2.ServerReflectionRequest(file_containing_symbol=symbol)
        result = self._reflection_single_request(request)
        return [
            descriptor_pb2.FileDescriptorProto.FromString(proto)
            for proto in result.file_descriptor_response.file_descriptor_proto
        ]

    def _is_descriptor_registered(self, filename):
        try:
            self._desc_pool.FindFileByName(filename)
            logger.debug(f"{filename} already registered")
            return True
        except KeyError:
            return False

    def register_file_descriptors(
        self, file_descriptors: List[descriptor_pb2.FileDescriptorProto]
    ):
        """
        Iterate over descriptors for registration, including returned descriptors as possible dependencies.
        This is necessary as while in practice descriptors appear to be returned in an order that works for dependency
        registration, this is not guaranteed in the reflection specification.
        :param file_descriptors: List of FileDescriptorProto to register
        """
        for file_descriptor in file_descriptors:
            self._register_file_descriptor(file_descriptor, file_descriptors)

    def _register_file_descriptor(self, file_descriptor, file_descriptors):
        if not self._is_descriptor_registered(file_descriptor.name):
            logger.debug(f"start {file_descriptor.name} register")
            dependencies = list(file_descriptor.dependency)
            logger.debug(
                f"found {len(dependencies)} dependencies for {file_descriptor.name}"
            )
            for dep_file_name in dependencies:
                if not self._is_descriptor_registered(dep_file_name):
                    # First look for dependency in the passed descriptors
                    dep_desc = next(
                        (x for x in file_descriptors if x.name == dep_file_name), None
                    )
                    # Otherwise get it from the client
                    if not dep_desc:
                        dep_descs = self.get_file_descriptors_by_name(dep_file_name)
                        if not dep_descs:
                            raise ValueError(
                                f"Required dependency {dep_file_name} not available."
                            )
                        dep_desc = dep_descs[0]
                        if len(dep_descs) > 1:
                            file_descriptors += dep_descs[1:]
                    # Remove the one we are looking for and use the rest as dependencies
                    self._register_file_descriptor(dep_desc, file_descriptors)
            try:
                self._desc_pool.Add(file_descriptor)
            except TypeError:
                logger.debug(
                    f"{file_descriptor.name} already present in pool. Skipping."
                )
            logger.debug(f"{file_descriptor.name} registration complete")

    def _is_service_registered(self, service_name):
        try:
            self.get_service_descriptor(service_name)
            logger.debug(f"{service_name} already registered")
            return True
        except KeyError:
            return False

    def register_service(self, service_name):
        if not self._is_service_registered(service_name):
            logger.debug(f"start {service_name} registration")
            file_descriptors = self.get_file_descriptors_by_symbol(service_name)
            self.register_file_descriptors(file_descriptors)
            logger.debug(f"{service_name} registration complete")
        super(ReflectionClient, self).register_service(service_name)


class StubClient(BaseGrpcClient):
    def __init__(
        self,
        endpoint,
        service_descriptors: List[ServiceDescriptor],
        symbol_db=None,
        lazy=False,
        descriptor_pool=None,
        ssl=False,
        compression=None,
        **kwargs,
    ):
        super().__init__(
            endpoint,
            symbol_db,
            descriptor_pool,
            ssl=ssl,
            compression=compression,
            lazy=lazy,
            **kwargs,
        )
        self.service_descriptors = service_descriptors

        if not self._lazy:
            self.register_all_service()

    def _get_service_names(self):
        svcs = [service.full_name for service in self.service_descriptors]
        return svcs


class ServiceClient:
    _method_names: Tuple[str, ...]
    _methods_meta: Dict[str, MethodMetaData]
    client: BaseGrpcClient
    name: str

    def __init__(self, client: BaseGrpcClient, service_name: str):
        self.client = client
        self.name = service_name
        self._methods_meta = self.client.get_methods_meta(self.name)
        self._method_names = tuple(self._methods_meta.keys())
        self._register_methods()

    def _register_methods(self):
        for method in self._method_names:
            setattr(self, method, partial(self.client.request, self.name, method))

    @property
    def method_names(self):
        return self._method_names

    @property
    def methods_meta(self):
        return self._methods_meta


Client = ReflectionClient

_cached_clients: Dict[str, Union[StubClient, ReflectionClient]] = {}


def get_by_endpoint(endpoint: str, service_descriptors=None, **kwargs) -> Client:
    global _cached_clients
    if endpoint not in _cached_clients:
        if service_descriptors:
            _cached_clients[endpoint] = StubClient(
                endpoint, service_descriptors=service_descriptors, **kwargs
            )
        else:
            _cached_clients[endpoint] = ReflectionClient(endpoint, **kwargs)
    return _cached_clients[endpoint]  # type: ignore[return-value]


def reset_cached_client(endpoint=None):
    global _cached_clients
    if endpoint:
        if endpoint in _cached_clients:
            del _cached_clients[endpoint]
    else:
        _cached_clients = {}
