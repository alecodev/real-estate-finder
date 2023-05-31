import json
import re
from http import HTTPStatus
from typing import Any, Awaitable, Callable, MutableMapping, Tuple
from urllib.parse import parse_qs

Scope = MutableMapping[str, Any]
Message = MutableMapping[str, Any]

Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]


class APIRouter(object):

    _endpoints: dict[re.Pattern[str], dict[str, Tuple[str, Callable]]] = {}

    _type_response = {
        HTTPStatus.OK: {
            'headers': [[b'content-type', b'application/json']],
            'body': HTTPStatus.OK.phrase
        },
        HTTPStatus.CREATED: {
            'headers': [[b'content-type', b'application/json']],
            'body': HTTPStatus.CREATED.phrase
        },
        HTTPStatus.NO_CONTENT: {
            'headers': [[b'content-type', b'text/plain']],
            'body': ''
        },
        HTTPStatus.BAD_REQUEST: {
            'headers': [[b'content-type', b'text/plain']],
            'body': str(HTTPStatus.BAD_REQUEST.value) + ' ' + HTTPStatus.BAD_REQUEST.phrase
        },
        HTTPStatus.NOT_FOUND: {
            'headers': [[b'content-type', b'text/plain']],
            'body': str(HTTPStatus.NOT_FOUND.value) + ' ' + HTTPStatus.NOT_FOUND.phrase
        },
        HTTPStatus.METHOD_NOT_ALLOWED: {
            'headers': [[b'content-type', b'text/plain']],
            'body': str(HTTPStatus.METHOD_NOT_ALLOWED.value) + ' ' + HTTPStatus.METHOD_NOT_ALLOWED.phrase
        },
        HTTPStatus.INTERNAL_SERVER_ERROR: {
            'headers': [[b'content-type', b'text/plain']],
            'body': str(HTTPStatus.INTERNAL_SERVER_ERROR.value) + ' ' + HTTPStatus.INTERNAL_SERVER_ERROR.phrase
        },
    }

    def clear_path(self, path: str) -> str:
        path = re.sub(r"\/\/+", '/', path)
        return re.sub(r"\/$", '', path) + '/'

    def path_to_regex(self, path: str) -> re.Pattern[str]:
        path = re.sub(r"\/+", '\\/', path)
        path = re.sub(r"{[^\}]+}", "([^\\\\/]+)", path)
        return re.compile('^'+path+'$')

    def path_exist_in_endpoints(self, path: str) -> re.Pattern[str] | None:
        search_path = (lambda path_regex: path_regex.search(path) is not None)
        endpoint = next(filter(search_path, self._endpoints.keys()), None)
        return endpoint

    async def read_body(self, receive: Receive) -> bytes:
        body: bytes = b''
        more_body = True

        while more_body:
            message = await receive()
            body += message.get('body', b'')
            more_body = message.get('more_body', False)

        return body

    async def send_response(self, send: Send, status: HTTPStatus, body: str | None = None) -> None:
        assert status in self._type_response

        await send({
            'type': 'http.response.start',
            'status': status,
            'headers': self._type_response[status]['headers'],
        })

        await send({
            'type': 'http.response.body',
            'body': str(body if body is not None else self._type_response[status]['body']).encode('utf-8'),
        })

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        assert scope['type'] == 'http'

        path = self.clear_path(scope['path'])
        path_endpoint = self.path_exist_in_endpoints(path)
        method = scope['method']

        if path_endpoint is None:
            await self.send_response(send, HTTPStatus.NOT_FOUND)
            return

        if method not in self._endpoints[path_endpoint]:
            await self.send_response(send, HTTPStatus.METHOD_NOT_ALLOWED)
            return

        path_parameters_search_name = re.search(
            r"\/{([^\/]+)}\/", self._endpoints[path_endpoint][method][0])
        path_parameters_name = None
        if path_parameters_search_name is not None:
            path_parameters_name = path_parameters_search_name.groups()

        path_parameters_search_value = path_endpoint.search(path)
        path_parameters_value = None
        if path_parameters_search_value is not None:
            path_parameters_value = path_parameters_search_value.groups()

        query_string: dict[Any, list[Any]] = parse_qs(scope['query_string'])
        query_parameters:  dict[str, Any] = {}
        for key, value in query_string.items():
            query_parameters[(key).decode()] = list(
                map(lambda item: item.decode(), value))

        path_parameters: dict[str, Any] = {}
        if path_parameters_value is not None and path_parameters_name is not None:
            path_parameters = dict(
                zip(path_parameters_name, path_parameters_value))

        parameters: dict[str, Any] = {**path_parameters, **query_parameters}

        body_parameters = await self.read_body(receive)
        if body_parameters:
            parameters['body'] = json.loads(body_parameters)

        try:
            code_status, data = self._endpoints[path_endpoint][method][1](
                **parameters)
        except:
            code_status = HTTPStatus.INTERNAL_SERVER_ERROR
            data = None
            raise Exception("Error in the endpoint execution")
        finally:
            await self.send_response(send, code_status, data)

    def set_types_args(self, kwargs: dict[str, Any], annotations: dict[str, Any]) -> dict[str, Any]:
        kwargs_types: dict[str, Any] = {}
        for key, value in kwargs.items():
            kwargs_types[key] = value
            if key in annotations and callable(annotations[key]):
                if type(value) is dict:
                    kwargs_types[key] = annotations[key](**value)
                else:
                    kwargs_types[key] = annotations[key](value)
        return kwargs_types

    def set_routes(self, method: str, path: str):
        path = self.clear_path(path)
        path_regex = self.path_to_regex(path)

        if path_regex in self._endpoints and method in self._endpoints[path_regex]:
            raise Exception("Duplicate endpoint", method, path)

        def decorator(func: Callable):

            def wrapper(*args, **kwargs):
                search_args = (
                    lambda arg: arg not in func.__code__.co_varnames)
                args_error = next(filter(search_args, kwargs.keys()), None)
                if args_error is not None:
                    return HTTPStatus.BAD_REQUEST, None

                kwargs = self.set_types_args(kwargs, func.__annotations__)
                return func(*args, **kwargs)

            if path_regex not in self._endpoints:
                self._endpoints[path_regex] = {}

            if method not in self._endpoints[path_regex]:
                self._endpoints[path_regex][method] = (path, wrapper)
            return wrapper

        return decorator

    def get(self, path):
        return self.set_routes('GET', path)

    def post(self, path: str):
        return self.set_routes('POST', path)

    def put(self, path: str):
        return self.set_routes('PUT', path)

    def patch(self, path: str):
        return self.set_routes('PATCH', path)

    def delete(self, path: str):
        return self.set_routes('DELETE', path)
