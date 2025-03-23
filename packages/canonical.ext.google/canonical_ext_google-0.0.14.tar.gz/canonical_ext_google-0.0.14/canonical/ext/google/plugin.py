# Copyright (C) 2022-2025 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from google.cloud import logging # type: ignore
from libcanonical.runtime import LOGGING_CONFIG

from .environ import GOOGLE_LOGGING_PROJECT


GOOGLE_PROJECT: str | None = GOOGLE_LOGGING_PROJECT


def setup():
    if GOOGLE_PROJECT:
        LOGGING_CONFIG['formatters']['google-cloud'] = {
            '()': "libcanonical.utils.logging.JSONFormatter",
            'datefmt': '%Y-%m-%d %H:%M:%S.%f'
        }
        LOGGING_CONFIG['handlers']['google-cloud'] = {
            'class': 'google.cloud.logging.handlers.CloudLoggingHandler',
            'client': logging.Client(
                project=GOOGLE_PROJECT
            ),
            'level': 'INFO',
            'formatter': 'google-cloud',
            'labels': {
                'kind': 'service'
            }
        }