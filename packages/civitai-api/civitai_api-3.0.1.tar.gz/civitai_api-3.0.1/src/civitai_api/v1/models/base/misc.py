from enum import StrEnum
from pydantic import BaseModel, StrictInt

class Model_Types(StrEnum):
    Checkpoint = "Checkpoint"
    TextualInversion = "TextualInversion"
    Hypernetwork = "Hypernetwork"
    AestheticGradient = "AestheticGradient"
    LORA = "LORA"
    Controlnet = "Controlnet"
    Poses = "Poses"
    LoCon = "LoCon"
    DoRA = "DoRA"
    Other = "Other"
    MotionModule = "MotionModule"
    Upscaler = "Upscaler"
    VAE = "VAE"
    Wildcards = "Wildcards"
    Workflows = "Workflows"

class Period(StrEnum):
    AllTime = "AllTime"
    Day = "Day"
    Week = "Week"
    Month = "Month"
    Year = "Year"

class AllowCommercialUse(StrEnum):
    Image = "Image"
    RentCivit = "RentCivit"
    Rent = "Rent"
    Sell = "Sell"
    None_ = "None"

class Sort(StrEnum):
    Most_Reactions = "Most Reactions"
    Most_Comments = "Most Comments"
    Newest = "Newest"

class NsfwLevel(StrEnum):
    None_ = 'None'
    Soft = 'Soft'
    Mature = 'Mature'
    X = 'X'

class ModelVersion_Files_Hashes(BaseModel):
    SHA256: str
    CRC32: str
    BLAKE3: str
    AutoV3: str
    AutoV2: str
    AutoV1: str

class Base_ModelVersion_Files_Metadata_Format(StrEnum):
    SafeTensor = "SafeTensor"
    PickleTensor = "PickleTensor"
    Other = "Other"
    Diffusers = "Diffusers"

class Base_ModelVersion_Files_Metadata(BaseModel):
    format: Base_ModelVersion_Files_Metadata_Format	# The specified model format for the file

class Base_ModelVersion_Files_PickleScanResult(StrEnum):
    Pending = 'Pending'
    Success = 'Success'
    Danger = 'Danger'
    Error = 'Error'
    
class Base_ModelVersion_Files_VirusScanResult(StrEnum):
    Pending = 'Pending'
    Success = 'Success'
    Danger = 'Danger'
    Error = 'Error'

class Base_ModelVersion_File(BaseModel):
    name: str # file name
    id: StrictInt # file id
    metadata: Base_ModelVersion_Files_Metadata
    pickleScanResult: Base_ModelVersion_Files_PickleScanResult # Status of the pickle scan ('Pending', 'Success', 'Danger', 'Error')
    virusScanResult: Base_ModelVersion_Files_VirusScanResult # Status of the virus scan ('Pending', 'Success', 'Danger', 'Error')
    scannedAt: str # (ISO 8601) The date in which the file was scanned
    primary: bool # If the file is the primary file for the model version
    type: str
    hashes: ModelVersion_Files_Hashes
    downloadUrl: str # model download url: "https://civitai.com/api/download/models/8387"

class Base_ModelVersion_Image(BaseModel):
    url: str
    nsfwLevel: StrictInt
    width: StrictInt
    height: StrictInt
    hash: str
