from phi.agent import Agent
from phi.model.groq import groq
from phi.tools.duckduckgo import DuckDuckGo
from ..agents.nlp_agent import NLPAgent
from ..agents.cv_agent import CVAgent   
from ..models.medical_image import MedicalImage
from ..models.patient_record import PatientRecord
from typing import Optional, Iterator
from phi.run.response import RunEvent, RunResponse
from phi.utils.log import logger
import json
from ..models.diagnosis_report import DiagnosisReport

class DiagnosisGenerator:
    def __init__(self):
        self.gen_ai_agent = Agent(
            name="Diagnosis Generator",
            model=groq.Groq(id="llama-3.2-11b-vision-preview"),
            description=(
                "You are an AI-powered Medical Diagnosis and Treatment Generator Agent specializing in analyzing patient records, "
                "symptoms, and medical images to provide an accurate diagnosis, treatment plan, and preventive measures. "
                "Your role is to process extracted symptom data, disease classification, and affected organs (from the cv_agent and nlp_agent) "
                "to generate a comprehensive diagnosis report, including:\n"
                "- Confirmed disease and its severity level\n"
                "- Symptoms and how they align with the detected condition\n"
                "- Affected organs and biological changes\n"
                "- Impact on internal bodily mechanisms\n"
                "- Harmful disease constituents and their effects\n"
                "- Risk factor mechanisms and progression risks\n"
                "- Diagnosis summary and test recommendations\n"
                "- Medication, treatments, and alternative therapies\n"
                "- Preventive measures and lifestyle changes\n"
                "Your goal is to provide a medically accurate, structured, and informative diagnosis that aids healthcare professionals in decision-making and patient treatment planning."
            ),
            instructions=[
                "Analyze medical image classification and symptom extraction results from cv_agent and nlp_agent.",
                "Identify and confirm the detected disease based on symptom patterns and organ impact.",
                "Determine the severity level of the disease (Mild, Moderate, Severe, Critical).",
                "Provide a detailed diagnosis covering:\n"
                "  - Disease name and type (e.g., infectious, autoimmune, genetic)\n"
                "  - Affected organs and biological changes\n"
                "  - Internal functionality impairment and disease progression risks\n"
                "  - Possible harmful constituents of the disease",
                "List recommended medical tests (e.g., MRI, blood tests, biopsies) for further evaluation.",
                "Suggest appropriate medications (including drug types and dosages where applicable).",
                "Outline treatment options (surgical, therapeutic, lifestyle-based).",
                "Provide preventive measures to slow or stop disease progression.",
                "Recommend lifestyle changes (e.g., diet, exercise, stress management) to improve patient well-being.",
                "Ensure that the diagnosis report is detailed, structured, and medically relevant, formatted for easy interpretation by healthcare professionals."
            ],
            tools= [DuckDuckGo()],
            show_tool_calls=True,
            markdown=True
        )
        
    def run(self, image_path: str, use_cache: bool = True) -> Iterator[RunResponse]:
        results : Optional[MedicalImage] = CVAgent.get_disease_label(image_path)
        symptoms : Optional[PatientRecord] = NLPAgent.extract_symptoms(image_path, results)
        diagnosis = self.generate_diagnosis(image_path, results, symptoms)
        if diagnosis is None:
            yield RunResponse(event=RunEvent.workflow_completed, response="No diagnosis generated")
            return

        yield RunResponse(content=diagnosis, event=RunEvent.workflow_completed)
        
    def generate_diagnosis(self, image_path: str, results: MedicalImage, symptoms: PatientRecord) -> DiagnosisReport:
        logger.info("Generating diagnosis report")
        agent_input = json.dumps({"image_path": image_path, "results": results.model_dump(), "symptoms": symptoms.model_dump()}, indent=4)
        diagnosis : RunResponse = self.gen_ai_agent.run(agent_input, use_cache= True)
        if diagnosis is None:
            return None
        self.gen_ai_agent.session_state.setdefault("diagnosis", {})[image_path] = diagnosis
        return diagnosis.content
        
