import re

from medstruct_ai.core.schemas import LabMetric

METRIC_PATTERN = re.compile(
    r"([A-Za-z][A-Za-z\s/]+?)\s*[:\-]?\s*(\d+\.?\d*)\s*(mg/dL|mmol/L|mmHg|g/dL|%|IU/L|mEq/L|ng/mL|pg/mL)",
    re.IGNORECASE,
)


def parse_lab_metrics(text: str) -> list[LabMetric]:
    metrics = []
    for match in METRIC_PATTERN.finditer(text):
        name = match.group(1).strip().lower().title()
        try:
            value = float(match.group(2))
        except ValueError:
            continue
        unit = match.group(3).lower()

        try:
            from core.logic import evaluate_metric_risk

            risk = evaluate_metric_risk(name, value)
            is_abnormal = risk not in ("Normal", "Unknown")
        except Exception:
            is_abnormal = False

        metrics.append(
            LabMetric(name=name, value=value, unit=unit, is_abnormal=is_abnormal)
        )
    return metrics
