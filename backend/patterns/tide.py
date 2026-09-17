"""Tide phase from a sea-level time series. No Django imports."""


def tide_phase(previous_m, current_m, day_min_m, day_max_m) -> str | None:
    if current_m is None:
        return None
    span = None
    if day_min_m is not None and day_max_m is not None:
        span = float(day_max_m) - float(day_min_m)

    standing = "mid"
    if span is not None and span >= 0.05:
        position = (float(current_m) - float(day_min_m)) / span
        if position >= 0.7:
            standing = "high"
        elif position <= 0.3:
            standing = "low"

    direction = None
    if previous_m is not None:
        delta = float(current_m) - float(previous_m)
        if delta > 0.02:
            direction = "incoming"
        elif delta < -0.02:
            direction = "outgoing"
        else:
            direction = "slack"

    if standing in {"high", "low"}:
        return standing
    return direction or standing


def tide_matches(phase: str | None, preference: str) -> bool:
    if not preference or preference == "any":
        return True
    if phase is None:
        return False
    return phase == preference


def daily_range(levels):
    nums = [float(value) for value in levels if value is not None]
    if not nums:
        return None, None
    return min(nums), max(nums)
