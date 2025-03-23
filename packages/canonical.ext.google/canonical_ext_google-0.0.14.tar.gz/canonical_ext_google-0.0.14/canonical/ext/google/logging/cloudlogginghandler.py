# Copyright (C) 2021-2024 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import os
from typing import Any

import google.cloud.logging


LOGGING_PROJECT: str | None = os.getenv('GOOGLE_LOGGING_PROJECT')


class CloudLoggingHandler(google.cloud.logging.handlers.CloudLoggingHandler):
    _client: google.cloud.logging.Client | None = None

    def __init__(self, **kwargs: Any):
        if LOGGING_PROJECT is None:
            raise TypeError(
                "Set the GOOGLE_LOGGING_PROJECT to define the cloud logging "
                "project."
            )
        if CloudLoggingHandler._client is None:
            CloudLoggingHandler._client = client = google.cloud.logging.Client(
                project=LOGGING_PROJECT
            )
            client.setup_logging() # type: ignore
        super().__init__(client=CloudLoggingHandler._client, **kwargs) # type: ignore