from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class LabMetric(BaseModel):
    name: str
    value: float
    unit: str
    is_abnormal: bool = False


class ClinicalInsight(BaseModel):
    visit_date: date
    notes: Optional[str] = None
    diagnoses: list[str] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)
    lab_metrics: list[LabMetric] = Field(default_factory=list)
    overall_risk: Optional[str] = None

    def computed_at(self) -> datetime:
        return datetime.now()


class PatientRecord(BaseModel):
    first_name: str
    last_name: str
    dob: date
    insights: list[ClinicalInsight] = Field(default_factory=list)
