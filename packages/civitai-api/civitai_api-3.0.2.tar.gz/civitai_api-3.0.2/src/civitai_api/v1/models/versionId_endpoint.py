from .base.modelVersion import Base_ModelVersion
from .base.misc import Model_Types, Base_ModelVersion_Image
from pydantic import BaseModel, StrictInt
from typing import List

class modelVersion_endpoint_modelVersion_earlyAccessConfig(BaseModel):
    timeframe: StrictInt | None = None
    donationGoal: StrictInt | None = None
    downloadPrice: StrictInt | None = None
    donationGoalId: StrictInt | None = None
    generationPrice: StrictInt | None = None
    chargeForDownload: bool | None = None
    chargeForGeneration: bool | None = None
    donationGoalEnabled: bool | None = None
    originalPublishedAt: str | None = None # ISO8061
    generationTrialLimit: StrictInt | None = None

class modelVersion_endpoint_modelVersion_model(BaseModel):
    name: str
    nsfw: bool
    poi: bool
    type: Model_Types

class modelVersion_endpoint_modelVersion(Base_ModelVersion):
    air: str
    baseModelType: str | None = None
    description: str | None = None
    earlyAccessConfig: modelVersion_endpoint_modelVersion_earlyAccessConfig
    earlyAccessEndsAt: str | None = None # ISO8061
    model: modelVersion_endpoint_modelVersion_model
    modelId: StrictInt
    updatedAt: str # ISO 8061
    uploadType: str # This looks like an enum type
    usageControl: str # This looks like an enum type
