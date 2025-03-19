from .utils import Lakehouse, Runtime, Util

def get_lakehouse():
    return Lakehouse()

def get_dump(obj: object):
    return Util().dump(obj)

def get_secret_from_keyvault(keyvault_name: str ,secret_name: str):
    return Util().get_secret_from_keyvault(keyvault_name, secret_name)

def get_runtime():
    return Runtime()
