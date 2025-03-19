import json
import logging
import time
import requests
from datetime import datetime
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StringType, TimestampType, StructType, StructField
import uuid


from firestart_utils.utils import get_runtime

DISABLED = 99
CRITICAL = 50
ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10
NOTSET = 0
METRIC_URL = "https://api.datadoghq.eu/api/v2/series"
LOG_URL = "https://http-intake.logs.datadoghq.eu/api/v2/logs"

nameToLevel = {
    "CRITICAL": CRITICAL,
    "ERROR": ERROR,
    "WARNING": WARNING,
    "INFO": INFO,
    "DEBUG": DEBUG,
    "NOTSET": NOTSET,
    "DISABLED": DISABLED,
}


class Logger:
    def __init__(self, dd_api_key, dd_customer, environment, level):
        self.dd_api_key = dd_api_key
        self.dd_customer = dd_customer
        self.environment = environment
        self.level = self.checkLevel(level)
        self.log_int = logging.getLogger("firestart_int")

    def debug(self, message):
        self.log_int.debug(message)
        self.handleLogging(self.is_extern_logging("DEBUG", message))

    def info(self, message):
        self.log_int.info(message)
        self.handleLogging(self.is_extern_logging("INFO", message))

    def warning(self, message):
        self.log_int.warning(message)
        self.handleLogging(self.is_extern_logging("WARNING", message))

    def error(self, message):
        self.log_int.error(message)
        self.handleLogging(self.is_extern_logging("ERROR", message))

    def critical(self, message):
        self.log_int.critical(message)
        self.handleLogging(self.is_extern_logging("CRITICAL", message))

    def failed(self):
        body = self.generate_metric_log_body(False)
        self.send_log(body, METRIC_URL)

    def success(self):
        body = self.generate_metric_log_body(True)
        self.send_log(body, METRIC_URL)

    def generate_log_body(self, level, message):
        return {
            "ddsource": f"Horizon - {get_runtime().current_workspace_name()}",
            "ddtags": f"env:{self.environment},customer:{self.dd_customer}",
            "hostname": f"Fabric - {self.dd_customer}",
            "message": f"{level}: {message}",
            "service": f"{get_runtime().current_notebook_name()}",
            "status": f"{level}",
        }

    def generate_metric_log_body(self, successful):
        metric = (
            "azure.datafactory_factories.pipeline_succeeded_runs"
            if successful
            else "azure.datafactory_factories.pipeline_failed_runs"
        )
        return {
            "series": [
                {
                    "metric": metric,
                    "type": 1,
                    "points": [{"timestamp": f"{int(time.time())}", "value": 1}],
                    "tags": [
                        "customer:{0}".format(self.dd_customer),
                        "environment:{0}".format(self.environment),
                        "name:{0}".format(get_runtime().current_notebook_name()),
                        "resource_group:{0}".format(
                            get_runtime().current_workspace_name()
                        ),
                    ],
                }
            ]
        }

    def is_extern_logging(self, level, message):
        if self.level <= nameToLevel[level]:
            return self.generate_log_body(level, message)
        else:
            return None

    def send_log(self, body, url):
        headers = {
            "Content-Type": "application/json",
            "DD-API-KEY": self.dd_api_key,
            "Accept": "application/json",
        }
        json_data = json.dumps(body)
        response = requests.post(url, data=json_data, headers=headers)
        self.log_int.debug(f"Status Code: {response.status_code}")
        self.log_int.debug(f"Response Body: {response.text}")

    def setLevel(self, level):
        self.level = self.checkLevel(level)

    def checkLevel(self, level):
        if isinstance(level, int):
            rv = level
        elif str(level) == level:
            if level not in nameToLevel:
                raise ValueError("Unknown level: %r" % level)
            rv = nameToLevel[level]
        else:
            raise TypeError("Level not an integer or a valid string: %r" % (level,))
        return rv

    def handleLogging(self, body):
        if body:
            self.send_log(body, LOG_URL)
        else:
            self.log_int.debug("No log sent")


logger_construct = {
    "notebook_name": StringType(),
    "notebook_id": StringType(),
    "trigger_run_uuid": StringType(),
    "environment": StringType(),
    "timestamp": TimestampType(),
    "status": StringType(),
    "level": StringType(),
    "message": StringType(),
}

"""
    Example usage:
        logger = LakeHouseLogger("DEV", "dbfs:/mnt/...")
        logger.debug("This is a debug message", "SUCCESS")
        logger.info("This is an info message", "SUCCESS")
        logger.warning("This is a warning message", "SUCCESS")
        logger.error("This is an error message", "SUCCESS")
        logger.critical("This is a critical message", "SUCCESS")
        logger.print_schema()
        logger.get_location()
"""


class LakeHouseLogger:
    def __init__(self, environment: str, location: str):
        self.environment: str = environment
        self.location: str = location
        self.spark: SparkSession | None = SparkSession.getActiveSession()
        self.logger_struct_data: StructType = StructType(
            [
                StructField(
                    const,
                    logger_construct[const],
                    True if const == "trigger_run_uuid" else False,
                )
                for const in logger_construct
            ]
        )

    def debug(self, message: str, status: str):
        self.__log_to_lakehouse__("DEBUG", message, status)

    def info(self, message: str, status: str):
        self.__log_to_lakehouse__("INFO",  message, status)

    def warning(self, message: str, status: str):
        self.__log_to_lakehouse__("WARNING", message, status)

    def error(self, message: str, status: str): 
        self.__log_to_lakehouse__("ERROR", message, status)

    def critical(self, message: str, status: str):
        self.__log_to_lakehouse__("CRITICAL", message, status)

    def print_schema(self) -> str | None:
        return self.spark.createDataFrame(
            data=[], schema=self.logger_struct_data
        ).printSchema()

    def get_location(self) -> str:
        return self.location

    def set_trigger_run_uuid(self, trigger_run_uuid: str):
        self.trigger_run_uuid = trigger_run_uuid 

    def __log_to_lakehouse__(
        self,
        level: str,
        message: str,
        status: str,
    ):
        if self.trigger_run_uuid is None:
            raise ValueError("Parent UUID is not set")

        parameters = {
            "notebook_name": get_runtime().current_notebook_name(),
            "notebook_id": get_runtime().current_notebook_id(),
            "trigger_run_uuid": self.trigger_run_uuid,
            "environment": self.environment,
            "timestamp": datetime.utcnow(),
            "status": status,
            "level": level,
            "message": message,
        }

        df_logging_row: DataFrame = self.spark.createDataFrame(
            [parameters], self.logger_struct_data
        )

        df_logging_row.write.mode("append").format("delta").option(
            "path", self.location
        ).save()
