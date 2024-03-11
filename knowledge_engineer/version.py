import importlib.metadata
import datetime


def get_version():
    package_name = __name__.split('.')[0]
    result = dict(importlib.metadata.metadata(package_name))
    del result['Description']
    del result['Description-Content-Type']
    result['current_datetime'] = datetime.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
    return result
