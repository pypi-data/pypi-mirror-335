"""
----------------------------------------------------------------------------------------------------
Written by:
  - Yovany Dominico Girón(y.dominico.giron@elprat.cat)

for Ajuntament del Prat de Llobregat
----------------------------------------------------------------------------------------------------

----------------------------------------------------------------------------------------------------
"""
import os
import sys
import uuid
import time
import json
import socket
import logging

from types import SimpleNamespace
from datetime import datetime, timezone

from pythonjsonlogger.json import JsonFormatter

from nomenclators_archetype.domain.loggers import LOGGER_LEVEL
from nomenclators_archetype.infrastructure.http.auths import APPLICATION_ID, get_user_from_jwt

JSON_LOGGER_ENV_NAME = "JSON_LOGGER_NAME"
JSON_LOGGER_NAME_DEFAULT = "logger_console_json"
JSON_LOGGER_NAME = os.getenv(JSON_LOGGER_ENV_NAME, JSON_LOGGER_NAME_DEFAULT)


logger_console_json = logging.getLogger(JSON_LOGGER_NAME)
logger_console_json.setLevel(getattr(logging, LOGGER_LEVEL, logging.INFO))

logger_console_json_handler = logging.StreamHandler(sys.stdout)

logger_console_json_formatter = JsonFormatter(
    "%(timestamp)s %(client_request_id)s %(server_request_id)s %(application_id)s "
    "%(request_time)s %(entry_time)s %(user)s %(client_session_id)s "
    "%(client_ip)s %(server_ip)s %(server_port)s %(service)s %(http_method)s "
    "%(module)s %(response_code)s %(response_time)s"
)

logger_console_json_handler.setFormatter(logger_console_json_formatter)

if not logger_console_json.hasHandlers():
    logger_console_json.addHandler(logger_console_json_handler)
    logger_console_json.propagate = False


def _retrive_json_data_from_message(log_message):
    """Retrieves the JSON data from a log message"""
    log_message = log_message.replace("'", "\"")

    start_index = log_message.find("{")
    end_index = log_message.rfind("}")

    assert start_index != -1 and end_index != - \
        1, "No se encontró un JSON en log_message"

    log_json = log_message[start_index:end_index + 1]
    return json.loads(log_json)


def _replace_dict_none_with_null(data):
    """Replaces None values with the string 'null' in a dictionary"""

    if isinstance(data, dict):
        return {key: _replace_dict_none_with_null(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_replace_dict_none_with_null(item) for item in data]
    elif data is None:
        return "null"
    return data


async def router_log_requests(request, call_next):
    """Log middlewares for the requests router"""

    start_time = time.time()
    request_time = datetime.now(timezone.utc).isoformat()

    server_request_id = str(uuid.uuid4())
    client_request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    client_session_id = request.headers.get("Authorization", None)
    user = get_user_from_jwt(client_session_id) if client_session_id else None

    client_ip = request.client.host if request.client else None
    server_ip = request.base_url.hostname if request.base_url else socket.gethostbyname(
        socket.gethostname())
    server_port = request.base_url.port if request.base_url else 80
    service = request.url.path
    http_method = request.method

    request.state.trace_info = getattr(request.state, "trace_info", {})
    response = await call_next(request)

    response_code = response.status_code
    trace_info = getattr(request.state, "trace_info", {})
    if isinstance(trace_info, dict):
        trace_info = SimpleNamespace(**trace_info)

    response_time = round(time.time() - start_time, 4)
    response.headers["X-Process-Time"] = str(response_time)

    log_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "client_request_id": client_request_id,
        "request_time": request_time,
        "server_request_id": server_request_id,
        "application_id": APPLICATION_ID,
        "user": user,
        "client_session_id": client_session_id,
        "client_ip": client_ip,
        "server_ip": server_ip,
        "server_port": server_port,
        "service": service,
        "http_method": http_method,
        "response_code": response_code,
        "response_module": getattr(trace_info, "module", None),
        "response_entity": getattr(trace_info, "entity", None),
        "response_id": getattr(trace_info, "identifier", None),
        "response_count": getattr(trace_info, "count", None),
        "response_page": getattr(trace_info, "page", None),
        "response_size": getattr(trace_info, "size", None),
        "response_time": response_time
    }

    logger_console_json.info(_replace_dict_none_with_null(log_data))
    return response
