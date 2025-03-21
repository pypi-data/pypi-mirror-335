# Copyright 2022 Semaphore Solutions
# ---------------------------------------------------------------------------
import atexit
import gzip
import logging
import os
import sys
from typing import Any, Optional

import ddtrace
import requests
from ddtrace import Span
from ddtrace.filters import TraceFilter
from pythonjsonlogger import jsonlogger  # type: ignore
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

log = logging.getLogger(__name__)


# Prevents tracing of SysExit, so unecessary error doesn't show in trace logs
class SysExitFilter(TraceFilter):
    def process_trace(self, trace: list[Span]) -> Optional[list[Span]]:
        return [span for span in trace if span.resource != 'function-invoke']


class FaasUtils:
    @staticmethod
    def get_file_content(file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError("This function expects a file to be provided at path: %s", file_path)

        if file_path.endswith('.gz'):
            with gzip.open(file_path, mode="rb") as zf:
                log.info("The provided file is an archive. It will be unzipped. %s", file_path)
                file_content = zf.read().decode("utf-8-sig")
        else:
            with open(file_path, mode="r", encoding="utf-8-sig") as f:
                file_content = f.read()

        return file_content

    @staticmethod
    def get_logging_configuration() -> dict[str, Any]:
        level = FaasUtils.get_env_var("LOG_LEVEL", "INFO")
        json_formatter = jsonlogger.JsonFormatter(timestamp=True)

        logging_handler_out = logging.StreamHandler(sys.stdout)
        logging_handler_out.setFormatter(json_formatter)
        logging_handler_out.setLevel(logging.getLevelName(level))

        logging_handler_err = logging.StreamHandler(sys.stderr)
        logging_handler_err.setFormatter(json_formatter)
        logging_handler_err.setLevel(logging.ERROR)
        config = {
            "level": level,
            "handlers": [logging_handler_out, logging_handler_err]
        }
        return config

    @staticmethod
    def write_function_output(output: str, working_dir: str) -> None:
        with open(os.path.join(working_dir, 'output.json'), 'w', encoding='UTF-8') as f:
            f.write(output)

    @staticmethod
    def initialize() -> Any:
        """Setup to allow for asynchronous invokes.

        The act of initializing simply allows this function to be run
        asynchronously.  It can still be invoked in a synchronous manner
        as required.

        In order to be run asynchronously a function needs to signal the
        notify system when it completes.

        Additionally, tracing is activated here.
        """

        # just signal ourselves.  no IPC!
        atexit.register(FaasUtils._notify_faas)
        FaasUtils._activate_tracing()

        return ddtrace.tracer.trace('function-invoke')

    @staticmethod
    def _activate_tracing() -> None:
        trace_id = FaasUtils.get_env_var("NOMAD_META_DATADOG_TRACE_ID", default_value="None")
        parent_id = FaasUtils.get_env_var("NOMAD_META_DATADOG_PARENT_ID", default_value="None")
        sampling_priority = FaasUtils.get_env_var("NOMAD_META_DATADOG_SAMPLING_PRIORITY", default_value="1")
        if trace_id != "None" and parent_id != "None":
            # Enable tracing throughout the function.
            # Tracing details are added to any `requests`
            # or `boto3` based web requests as well has
            # tracing details being added to log lines.
            ddtrace.patch(requests=True)
            ddtrace.patch(logging=True)
            ddtrace.patch(botocore=True)

            context = ddtrace.context.Context(
                trace_id=int(trace_id),
                span_id=int(parent_id),
                sampling_priority=float(sampling_priority)
            )
            # And then configure it with
            ddtrace.tracer.configure(settings={'FILTERS': [SysExitFilter()]})
            ddtrace.tracer.context_provider.activate(context)

    @staticmethod
    def _notify_faas() -> None:
        auth_token = FaasUtils.get_env_var("ACCESS_TOKEN", hide_value=True)
        environment = FaasUtils.get_env_var("ENVIRONMENT_NAME")
        headers = {
            "Authorization": "Bearer " + auth_token,
            "x-s4-env": environment
        }

        data = {
            "success": True,
            "message": "Function execution complete"
        }

        complete_url = FaasUtils.get_env_var("COMPLETE_URL")

        retry_strategy = Retry(
          total=3,
          status_forcelist=[429, 500, 502, 503, 504],
          allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http = requests.Session()
        http.mount("https://", adapter)
        http.mount("http://", adapter)

        response = http.post(complete_url, json=data, headers=headers)
        log.info(f"Complete signal response status: {response.status_code}")
        
    @staticmethod
    def get_env_var(name: str, default_value: Optional[str] = None, hide_value: Optional[bool] = False) -> str:
        value = os.environ.get(name)

        if value:
            log.debug("Environment variable %s found. Using value: %s", name, "[Hidden]" if hide_value else value)
        else:
            if default_value is None:
                raise ValueError(f"A required environment variable was not found: {name}")
            log.debug("Environment variable %s not found. Using default value: %s", name, default_value)
            value = default_value

        return value
