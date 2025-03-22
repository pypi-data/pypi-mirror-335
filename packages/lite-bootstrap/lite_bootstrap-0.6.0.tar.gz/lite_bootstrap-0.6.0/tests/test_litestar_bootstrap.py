import structlog
from litestar import status_codes
from litestar.config.app import AppConfig
from litestar.testing import TestClient
from opentelemetry.sdk.trace.export import ConsoleSpanExporter

from lite_bootstrap import (
    LitestarBootstrapper,
    LitestarHealthChecksInstrument,
    LitestarLoggingInstrument,
    LitestarOpenTelemetryInstrument,
    LitestarSentryInstrument,
    ServiceConfig,
)
from tests.conftest import CustomInstrumentor


logger = structlog.getLogger(__name__)


def test_litestar_bootstrap(service_config: ServiceConfig) -> None:
    app_config = AppConfig()
    bootstrapper = LitestarBootstrapper(
        bootstrap_object=app_config,
        service_config=service_config,
        instruments=[
            LitestarOpenTelemetryInstrument(
                endpoint="otl",
                instrumentors=[CustomInstrumentor()],
                span_exporter=ConsoleSpanExporter(),
            ),
            LitestarSentryInstrument(
                dsn="https://testdsn@localhost/1",
            ),
            LitestarHealthChecksInstrument(
                path="/health/",
            ),
            LitestarLoggingInstrument(logging_buffer_capacity=0),
        ],
    )
    application = bootstrapper.bootstrap()
    logger.info("testing logging", key="value")

    try:
        with TestClient(app=application) as async_client:
            response = async_client.get("/health/")
            assert response.status_code == status_codes.HTTP_200_OK
            assert response.json() == {
                "health_status": True,
                "service_name": "microservice",
                "service_version": "2.0.0",
            }
    finally:
        bootstrapper.teardown()
