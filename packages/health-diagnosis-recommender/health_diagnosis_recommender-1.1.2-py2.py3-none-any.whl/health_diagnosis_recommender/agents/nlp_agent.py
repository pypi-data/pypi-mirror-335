from phi.agent import Agent
from phi.model.groq import groq
from phi.tools.duckduckgo import DuckDuckGo
from phi.utils.log import logger
from .cv_agent import CVAgent
from ..models.medical_image import MedicalImage
from ..models.patient_record import PatientRecord
from typing import Optional, Iterator
from phi.run.response import RunEvent, RunResponse

class NLPAgent:
    def __init__(self):
        self.nlp_agent = Agent(
            name="Symptom Extractor",
            model=groq.Groq(id="llama-3.2-11b-vision-preview"),
            description=(
                "You are an advanced Medical NLP Agent specializing in analyzing medical image reports and extracting crucial diagnostic details. "
                "Your role is to process medical image classifications (provided by the CV Agent) and extract relevant symptoms, affected organs, risk factors, "
                "severity levels, biological changes, and potential causes of the detected condition. Your analysis will help in:\n"
                "- Identifying key symptoms associated with the detected condition\n"
                "- Assessing severity levels based on the detected abnormality\n"
                "- Determining affected organs and predicting functional impairment\n"
                "- Understanding biological changes caused by the disease\n"
                "- Recognizing potential risk factors (genetic, lifestyle, environmental)\n"
                "- Describing how the disease impacts the internal working mechanism of the body\n"
                "Your insights will be passed to the Diagnosis Generator Agent (gen_ai_agent), which will generate a comprehensive diagnosis and treatment plan for the patient."
            ),
            instructions=[
                "Analyze the medical image classification results provided by the cv_agent.",
                "Extract and list key symptoms associated with the detected disease.",
                "Identify affected organs and explain how the disease impairs their function.",
                "Determine the severity level (Mild, Moderate, Severe, Critical).",
                "Examine and list biological changes (e.g., cell mutation, tissue damage, inflammation).",
                "Identify risk factors (e.g., genetics, lifestyle, environmental exposure) that may have contributed to the disease.",
                "Explain the internal working mechanism impact, describing how the disease disrupts normal bodily functions.",
                "Ensure the output is structured and well-organized, as it will be used by the Diagnosis Generator Agent to provide treatment recommendations.",
                "If no symptoms are identified, state 'No significant symptoms detected,' but provide any relevant observations."
            ],
            tools= [DuckDuckGo()],
            show_tool_calls=True,
            markdown=True
        )
        
    def run(self, image_path: str, use_cache: bool = True) -> Iterator[RunResponse]:
        results = CVAgent.get_disease_label(image_path)
        symptoms = self.extract_symptoms(image_path, results)
        if symptoms is None:
            yield RunResponse(event=RunEvent.workflow_completed, response="No symptoms found")
            return
        
    def extract_symptoms(self, image_path: str, results: MedicalImage) -> Optional[PatientRecord]:
        logger.info("Extracting symptoms from the image")
        results = self.nlp_agent.run(image_path, use_cache= True)
        if results is None:
            return None
        self.nlp_agent.session_state.setdefault("symptoms", {})[image_path] = results
        return results
        