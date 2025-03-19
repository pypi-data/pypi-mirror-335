# Copyright 2024 Superlinked, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from json import JSONDecodeError

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from superlinked.framework.common.parser.exception import MissingIdException
from superlinked.framework.online.dag.exception import ValueNotProvidedException

from superlinked.server.configuration.app_config import AppConfig
from superlinked.server.dependency_register import register_dependencies
from superlinked.server.exception.exception_handler import (
    handle_bad_request,
    handle_generic_exception,
)
from superlinked.server.logger import ServerLoggerConfigurator
from superlinked.server.middleware.lifespan_event import lifespan
from superlinked.server.middleware.timing_middleware import add_timing_middleware
from superlinked.server.router.management_router import router as management_router


class ServerApp:
    def __init__(self) -> None:
        self.app = self._create_app()

    def _setup_executor_handlers(self, app: FastAPI) -> None:
        app.add_exception_handler(ValueNotProvidedException, handle_bad_request)
        app.add_exception_handler(MissingIdException, handle_bad_request)
        app.add_exception_handler(JSONDecodeError, handle_bad_request)
        app.add_exception_handler(ValueError, handle_bad_request)
        app.add_exception_handler(Exception, handle_generic_exception)

    def _create_app(self) -> FastAPI:
        app_config = AppConfig()
        logs_to_suppress = ["sentence_transformers"]
        ServerLoggerConfigurator.setup_logger(app_config, logs_to_suppress)

        app = FastAPI(lifespan=lifespan)
        self._setup_executor_handlers(app)
        app.include_router(management_router)

        add_timing_middleware(app)
        app.add_middleware(CorrelationIdMiddleware)  # This must be the last middleware

        register_dependencies()

        return app
