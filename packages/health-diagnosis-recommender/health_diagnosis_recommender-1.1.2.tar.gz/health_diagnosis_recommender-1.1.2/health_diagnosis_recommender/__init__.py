"""Health Diagnosis Recommender - AI-powered healthcare diagnosis system"""

# You can import necessary modules here if needed

from .models.medical_image import MedicalImage
from .models.patient_record import PatientRecord
from .models.diagnosis_report import DiagnosisReport

from .agents.cv_agent import CVAgent
from .agents.nlp_agent import NLPAgent
from .agents.diagnosis_generator import DiagnosisGenerator

from .workflow.healthcare_diagnosis_workflow import HealthcareDiagnosisWorkflow

from .utils.cache import CacheManager
from .utils.logger import LoggerManager

__version__ = "1.0.0"
__author__ = "Dibyojit Ghoshal"
__description__ = "An AI-powered Healthcare Diagnosis and Treatment Planner Recommendation System"

__all__ = [
    "MedicalImage",
    "PatientRecord",
    "DiagnosisReport",
    "CVAgent",
    "NLPAgent",
    "DiagnosisGenerator",
    "HealthcareDiagnosisWorkflow",
    "CacheManager",
    "LoggerManager"
]