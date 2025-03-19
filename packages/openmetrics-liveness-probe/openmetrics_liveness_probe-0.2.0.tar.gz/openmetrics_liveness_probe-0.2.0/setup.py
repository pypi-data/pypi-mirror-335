# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openmetrics_liveness_probe']

package_data = \
{'': ['*']}

install_requires = \
['prometheus-client>=0.9', 'pydantic>=1.8,<3.0']

setup_kwargs = {
    'name': 'openmetrics-liveness-probe',
    'version': '0.2.0',
    'description': 'Library for getting the time when the service was last considered alive.',
    'long_description': '[![PyPI pyversions](https://img.shields.io/pypi/pyversions/openmetrics-liveness-probe.svg)](https://pypi.python.org/pypi/openmetrics-liveness-probe/) [![PyPI license](https://img.shields.io/pypi/l/openmetrics-liveness-probe.svg)](https://pypi.python.org/pypi/openmetrics-liveness-probe/) [![PyPI version fury.io](https://badge.fury.io/py/openmetrics-liveness-probe.svg)](https://pypi.python.org/pypi/openmetrics-liveness-probe/) [![build](https://github.com/Usetech/openmetrics-liveness-probe/actions/workflows/ci.yml/badge.svg)](https://github.com/Usetech/openmetrics-liveness-probe/actions/workflows/ci.yml?branch=main)\n\n\nopenmetrics-liveness-probe\n============\n\nБиблиотека для получения времени, когда сервис в последний раз считался живым.\nРезультат экспортируется в формате OpenMetrics. Пример вывода:\n\n```\n# HELP liveness_probe_unixtime Unixtime последней liveness probe\n# TYPE liveness_probe_unixtime gauge\nliveness_probe_unixtime{service="test"} 1.659455742252334e+09\n```\n\nВ многопоточном режиме:\n```\n# HELP liveness_probe_unixtime Multiprocess metric\n# TYPE liveness_probe_unixtime gauge\nliveness_probe_unixtime{pid="12821",service="example"} 1.6596198592194734e+09\nliveness_probe_unixtime{pid="13521",service="example"} 1.6796198592194734e+09\n```\n\nДля начала необходимо объявить переменные окружения:\n```\nOPENMETRICS_LIVENESS_PROBE_ENABLED=True\nOPENMETRICS_LIVENESS_PROBE_HOST=0.0.0.0\nOPENMETRICS_LIVENESS_PROBE_PORT=8000\nOPENMETRICS_LIVENESS_PROBE_SERVICE_NAME=example\nOPENMETRICS_LIVENESS_PROBE_NAME_POSTFIX=liveness_probe_unixtime\nOPENMETRICS_LIVENESS_PROBE_ENABLE_DEFAULT_PROMETHEUS_METRICS=False\nPROMETHEUS_MULTIPROC_DIR=None\n```\n\nВсе переменные по-умолчанию будут равны значениям, указанным в списке выше, Но переменная окружения ``SERVICE_NAME`` должна быть обязательно изменена.\n\nПеременная окружения ``ENABLE_DEFAULT_PROMETHEUS_METRICS`` включает метрики по-умолчанию доступные в ``prometheus_client``: \n``PROCESS_COLLECTOR``, ``PLATFORM_COLLECTOR``, ``GC_COLLECTOR``.    \nПо-умолчанию их отображение выключено.\n\nПеременная окружения ``PROMETHEUS_MULTIPROC_DIR`` позволяет запускать prometheus сервер в многопоточном режиме. По умолчанию эта переменная равна ``None.`` Для активации этого режима нужно задать путь для переменной окружения ``PROMETHEUS_MULTIPROC_DIR``, например: ``/tmp``.\n\n# Содержание\n\n- [Установка](#Установка)\n\n<a name=\'Установка\'></a>\n## Установка\n\nОписание установки\n- pip \n```\npip install openmetrics_liveness_probe\n```\n',
    'author': 'Daniil Nikitin',
    'author_email': 'dnikitin@usetech.ru',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/Usetech/openmetrics-liveness-probe',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
