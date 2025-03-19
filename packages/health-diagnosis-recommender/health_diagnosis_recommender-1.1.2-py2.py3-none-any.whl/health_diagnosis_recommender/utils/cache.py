from typing import Optional
from ..models.medical_image import MedicalImage
from ..models.diagnosis_report import DiagnosisReport
from phi.utils.log import logger

class CacheManager:
    def __init__(self, session_state: dict):
        self.session_state = session_state

    def cached(self, image_path: str) -> MedicalImage:
        logger.info("Checking cache for existing label")
        return self.session_state.get("labels", {}).get(image_path)

    def add_response_to_cache(self, image_path: str, response: DiagnosisReport):
        logger.info(f"Caching response for image: {image_path}")
        self.session_state.setdefault("recommendations", {})[image_path] = response
