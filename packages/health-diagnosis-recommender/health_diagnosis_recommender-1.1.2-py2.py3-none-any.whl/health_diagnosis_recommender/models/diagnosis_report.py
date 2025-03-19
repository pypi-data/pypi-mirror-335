from pydantic import BaseModel, Field
from typing import List, Optional

class DiagnosisReport(BaseModel):
    disease_detected: str = Field(description="Disease detected in the patient")
    symptoms_captured: str = Field(description="Symptoms captured from the patient")
    organs_affected: str = Field(description="Organs affected by the disease")
    biological_changes: str = Field(description="Biological changes observed")
    internal_working_mechanism_functionality_impact : str = Field(description="Internal working mechanism and functionality impact")
    severity_level: str = Field(description="Severity level of the disease")
    harmful_disease_constituents: str = Field(description="Harmful disease constituents")
    risk_factor_working_mechanisms : str = Field(description="Risk factor working mechanisms")
    diagnosis: str = Field(description="Diagnosis of the patient")
    tests_performed: str = Field(description="Tests performed on the patient")
    medications_used: str = Field(description="Medication for the patient")
    hormonal_level_measures: List[int] = Field(description="Hormonal level measures")
    treatment: str = Field(description="Treatment of the patient")
    preventive_measures: str = Field(description="Preventive measures")
    lifestyle_changes: str = Field(description="Lifestyle changes")
    additional_info: Optional[str] = Field(description="Additional information")
