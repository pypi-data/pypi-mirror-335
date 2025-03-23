from pydantic import BaseModel, StrictInt
from typing import List
from .misc import Base_ModelVersion_File, Base_ModelVersion_Image

class Base_ModelVersion(BaseModel):
    id: StrictInt
    name: str
    publishedAt: str
    trainedWords: List[str]
    baseModel: str
    downloadUrl: str
    files: List[Base_ModelVersion_File]
    images: List[Base_ModelVersion_Image]