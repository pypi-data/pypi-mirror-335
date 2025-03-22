import dataclasses
import typing

from lite_bootstrap.bootstrappers.base import BaseBootstrapper
from lite_bootstrap.instruments.logging_instrument import LoggingInstrument
from lite_bootstrap.instruments.opentelemetry_instrument import OpenTelemetryInstrument
from lite_bootstrap.instruments.sentry_instrument import SentryInstrument
from lite_bootstrap.service_config import ServiceConfig


@dataclasses.dataclass(kw_only=True, slots=True, frozen=True)
class FreeBootstrapper(BaseBootstrapper[None, None]):
    bootstrap_object: None = None
    instruments: typing.Sequence[OpenTelemetryInstrument | SentryInstrument | LoggingInstrument]
    service_config: ServiceConfig

    def _prepare_application(self) -> None:
        return self.bootstrap_object
