import base64
from pydantic import BaseModel, Field
from typing import Optional

class MedicalImage(BaseModel):
    path: str = Field(description="Path to the medical image file")
    image: Optional[str] = Field(description="Base64 encoded image data")
    model_config = {
        "arbitrary_types_allowed": True  
    }

    @classmethod
    def from_image(cls, path: str):
        with open(path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return cls(path=path, image=encoded_string)
