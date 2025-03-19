from typing import Optional, Iterator
from phi.run.response import RunEvent, RunResponse
from phi.utils.log import logger
from phi.agent import Agent
from phi.tools.duckduckgo import DuckDuckGo
from phi.model.groq import groq
from ..models.medical_image import MedicalImage
from ..utils.cache import CacheManager

class CVAgent:
    def __init__(self):
        self.cv_agent = Agent(
            name="Image Classifier",
            model=groq.Groq(id="llama-3.2-11b-vision-preview"),
            description=(
                "You are an advanced Medical Image Classifier Agent. Your role is to analyze and classify medical images, "
                "identifying potential diseases, abnormalities, and medical conditions. You process X-rays, CT scans, MRIs, "
                "ultrasounds, and histopathological images, providing a detailed classification of the detected conditions. "
                "Additionally, you provide an explanation of the detected disease, highlighting the affected organs, "
                "possible symptoms, and risk factors. You use deep learning-based vision models to extract insights from the images, "
                "focusing on:\n"
                "- Disease classification (e.g., Pneumonia, Tumors, Fractures, Cardiovascular issues)\n"
                "- Affected organs and tissues (e.g., Lungs, Liver, Brain, Heart)\n"
                "- Severity levels (e.g., Mild, Moderate, Severe)\n"
                "- Potential causes (e.g., Genetic, Lifestyle, Infection-based)\n"
                "- Abnormal biological patterns (e.g., Tumor growth, Inflammation, Tissue damage)\n"
                "Your output serves as crucial input for the NLP agent, which further extracts text-based symptoms, "
                "risk factors, and treatment options."
            ),
            instructions=[
                "Load the provided medical image and perform pre-processing if necessary (e.g., grayscale conversion, contrast enhancement).",
                "Analyze the image using deep learning models to detect and classify medical conditions.",
                "Identify potential diseases or abnormalities present in the image.",
                "Provide a detailed label and explanation for the detected disease, including:\n"
                "  - Name of the disease\n"
                "  - Affected organs\n"
                "  - Severity level\n"
                "  - Possible causes\n"
                "  - Potential symptoms\n"
                "  - Risk factors",
                "If no disease is detected, clearly state 'No abnormalities found' but still highlight potential areas of interest.",
                "Ensure that the output is structured and clear, as it will be used by the NLP agent for further processing."
            ],
            tools= [DuckDuckGo()],
            show_tool_calls=True,
            markdown=True
        )
        
    def run(self, image_path: str, use_cache: bool = True) -> Iterator[RunResponse]:
            logger.info(f"Processing image: {image_path}")

            if use_cache:
                cached_response = CacheManager.cached(image_path)
                if cached_response:
                    yield RunResponse(content=cached_response, event=RunEvent.workflow_completed)
                    return

            results = self.get_disease_label(image_path)
            
            if results is None:
                yield RunResponse(event=RunEvent.workflow_completed, response="No CV data found")
            return
        
    def get_disease_label(self, image_path: str) -> Optional[MedicalImage]:
        logger.info("Identifying the disease in the image")
        results = self.cv_agent.run(image_path)
        if results is None:
            raise ValueError("No CV data found")
        self.cv_agent.session_state.setdefault("labels", {})[image_path] = results
        return self.cv_agent.session_state["labels"][image_path]
        