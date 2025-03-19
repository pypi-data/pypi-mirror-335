from .logger import Logger, LakeHouseLogger

def get_logger(dd_api_key, dd_customer, environment, log_level):
    return Logger(dd_api_key, dd_customer, environment, log_level)

def get_lakehouse_logger(environment, location):
    return LakeHouseLogger(environment, location)
