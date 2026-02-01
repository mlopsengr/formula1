import time
from enum import Enum
from dataclasses import dataclass, field

class Recommendation(Enum):
    STAY_OUT = "STAY_OUT"
    BOX_THIS_LAP = "BOX_THIS_LAP"
    BOX_NEXT_LAP = "BOX_NEXT_LAP"

@dataclass
class CircuitBreaker:
    failure_count: int = 0
    last_failure_time: float = 0
    threshold: int = 3
    cooldown_seconds: float = 10.0

    def is_open(self) -> bool:
        if self.failure_count < self.threshold:
            return False
        if time.time() - self.last_failure_time > self.cooldown_seconds:
            self.failure_count = 0  # reset after cooldown
            return False
        return True

    def record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.time()

def rule_based_fallback(lap_number: int, tire_age_laps: int) -> str:
    """Fallback when ML service is unavailable—demanding tech factor: reliability."""
    if tire_age_laps >= 25:
        return Recommendation.BOX_THIS_LAP.value
    if tire_age_laps >= 20 and lap_number > 30:
        return Recommendation.BOX_NEXT_LAP.value
    return Recommendation.STAY_OUT.value

def get_strategy_recommendation(
    lap_number: int,
    tire_age_laps: int,
    primary_service_call=None,  # inject mock or real API
    circuit_breaker: CircuitBreaker = None,
) -> str:
    breaker = circuit_breaker or CircuitBreaker()
    if breaker.is_open():
        return rule_based_fallback(lap_number, tire_age_laps)
    try:
        if primary_service_call:
            return primary_service_call(lap_number, tire_age_laps)
    except Exception:
        breaker.record_failure()
    return rule_based_fallback(lap_number, tire_age_laps)