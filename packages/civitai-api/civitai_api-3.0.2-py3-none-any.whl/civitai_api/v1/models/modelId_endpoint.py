from .base.modelVersion import Base_ModelVersion
from .base.misc import Model_Types, AllowCommercialUse
from .creators_endpoint import Response_Creaters_Item
from pydantic import BaseModel, StrictInt
from enum import StrEnum
from typing import List

class ModelId_Availability(StrEnum):
    EarlyAccess = 'EarlyAccess'
    Public = 'Public'

class ModelId_ModelVersion(Base_ModelVersion):
    availability: ModelId_Availability
    index: StrictInt
    nsfwLevel: StrictInt

class ModelId_Response(BaseModel):
    id: StrictInt
    name: str
    allowNoCredit: bool
    allowCommercialUse: List[AllowCommercialUse]
    allowDerivatives: bool
    allowDifferentLicense: bool
    type: Model_Types
    minor: bool
    poi: bool
    nsfw: bool
    nsfwLevel: StrictInt
    tags: List[str]
    creator: Response_Creaters_Item
    modelVersions: List[ModelId_ModelVersion]
