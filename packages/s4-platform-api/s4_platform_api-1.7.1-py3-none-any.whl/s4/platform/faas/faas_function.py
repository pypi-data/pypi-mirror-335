# Copyright 2023 Semaphore Solutions
# ---------------------------------------------------------------------------
import abc
import logging
import os

import pyjson5
from pythonjsonlogger import jsonlogger  # type: ignore
from s4.platform.api import Api
from s4.platform.connection import Connection
from s4.platform.faas.custom_errors import ClientError
from s4.platform.faas.faas_utils import FaasUtils
from s4.platform.prospective_task.prospective_task import ProspectiveTaskSchema, ProspectiveTask


log = logging.getLogger(__name__)


class FaasFunction:

    @staticmethod
    def get_prospective_task(api: Api, input_file_content: str) -> ProspectiveTask:
        prospective_task_id = pyjson5.loads(input_file_content)['taskId']
        return api.prospective_task_by_id(prospective_task_id)

    @staticmethod
    def pt_to_string(prospective_task: ProspectiveTask) -> str:
        schema = ProspectiveTaskSchema()
        return schema.dumps(prospective_task)

    @abc.abstractmethod
    def main(self, api: Api, input_file_content: str) -> str:
        pass

    def execute(self) -> int:
        with FaasUtils.initialize():
            logging.basicConfig(**FaasUtils.get_logging_configuration())

            # if this is executed by NOMAD then a task directory will be provided via env variable
            working_dir = FaasUtils.get_env_var("NOMAD_TASK_DIR")

            gateway_url = FaasUtils.get_env_var("GATEWAY_URL", "http://localhost:8080")
            environment_name = FaasUtils.get_env_var("ENVIRONMENT_NAME", None)

            input_file_name = FaasUtils.get_env_var("INPUT_FILE_NAME", "input.gz")
            input_file_path = os.path.join(working_dir, input_file_name)

            result: str

            try:
                connection = Connection(gateway_url, environment_name=environment_name)
                api = Api(connection)

                input_file_content = FaasUtils.get_file_content(input_file_path)

                log.info("Starting function. Processing file: %s", input_file_path)
                result = self.main(api, input_file_content)
                log.info("Completed function. Processed file: %s", input_file_path)
                # HTTP response is 200 OK
                return 0
            except ClientError as e:
                log.error(e, exc_info=True)
                result = str(e)
                # ClientError response is HTTP 400
                return 1
            except Exception as e:
                log.error(e, exc_info=True)
                result = str(e)
                # HTTP response is 500
                return 101
            finally:
                if result is not None:
                    FaasUtils.write_function_output(result, working_dir)
