from pydantic import BaseModel, Field

class PatientRecord(BaseModel):
    name: str = Field(description="Name of the patient")
    age: int = Field(description="Age of the patient")
    gender: str = Field(description="Gender of the patient")
    symptoms: str = Field(description="Symptoms of the patient")