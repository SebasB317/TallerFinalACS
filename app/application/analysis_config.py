from dataclasses import dataclass

from app.config import Settings


@dataclass(frozen=True, slots=True)
class AnalysisRuntimeConfig:
    """Parámetros de la simulación de análisis (workers / Historia #3)."""

    analysis_sleep_min_sec: float
    analysis_sleep_max_sec: float
    simulated_analysis_timeout_probability: float

    @classmethod
    def from_settings(cls, s: Settings) -> "AnalysisRuntimeConfig":
        return cls(
            analysis_sleep_min_sec=s.analysis_sleep_min_sec,
            analysis_sleep_max_sec=s.analysis_sleep_max_sec,
            simulated_analysis_timeout_probability=s.simulated_analysis_timeout_probability,
        )
