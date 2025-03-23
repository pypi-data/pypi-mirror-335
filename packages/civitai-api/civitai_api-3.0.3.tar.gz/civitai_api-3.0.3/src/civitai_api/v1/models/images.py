from enum import StrEnum
from typing import Annotated, Any, Dict, List, Optional
from annotated_types import Len
from pydantic import BaseModel, Field, StrictInt
from .base.misc import Sort, Period, NsfwLevel

class Response_Images_Stats(BaseModel):
    cryCount: int # The number of cry reactions
    laughCount: int # The number of laugh reactions
    likeCount: int # The number of like reactions
    heartCount: int # The number of heart reactions
    commentCount: int # The number of comment reactions

class Response_Images_Meta_CivitaiResources_Type(StrEnum):
    checkpoint = "checkpoint"
    lora = "lora"

class Response_Images_Meta_Resources(BaseModel):
    hash: str
    name: str
    type: Response_Images_Meta_CivitaiResources_Type
    # weight: float | None = None

class Response_Images_Meta_CivitaiResources(BaseModel):
    type: Response_Images_Meta_CivitaiResources_Type
    # weight: Optional[float] = None
    modelVersionId: int
    # modelVersionName: str | None = None

class Response_Images_Meta(BaseModel): # this field is a non-structured object that contains additional information about the image, the meta structure will be different for each webui
    Size: str
    seed: int
    vaes: str | None = None
    comfy: str | None = None # the json data str
    Model: str
    steps: int
    prompt: str
    sampler: str
    Version: str # webui version str
    cfgScale: int
    clipSkip: str
    resources: List[Response_Images_Meta_Resources]
    civitaiResources: List[Response_Images_Meta_CivitaiResources] # The generation process used model resource information
    Hires_upscale: str | None = None
    Hires_upscaler: str | None = None
    negativePrompt: str
    Denoising_strength: str | None = None
    ADetailer_model: str | None = Field(default=None, alias="ADetailer model")
    ADetailer_version: str | None = Field(default=None, alias="ADetailer version") # version str
    ADetailer_mask_blur: str | None = Field(default=None, alias="ADetailer mask blur") # float str
    ADetailer_confidence: str | None = Field(default=None, alias="ADetailer confidence") # float str
    ADetailer_dilate_erode: str | None = Field(default=None, alias="ADetailer dilate erode") # float str
    ADetailer_inpaint_padding: str | None = Field(default=None, alias="ADetailer inpaint padding") # float str
    ADetailer_denoising_strength: str | None = Field(default=None, alias="ADetailer denoising strength") # float str
    ADetailer_inpaint_only_masked: str | None = Field(default=None, alias="ADetailer inpaint only masked") # bool str
    #   "meta": {
    #     "Size": "512x768",
    #     "seed": 234871805,
    #     "Model": "Meina",
    #     "steps": 35,
    #     "prompt": "<lora:setsunaTokage_v10:0.6>, green hair, long hair, standing, (ribbed dress), zettai ryouiki, choker, (black eyes), looking at viewer, adjusting hair, hand in own hair, street, grin, sharp teeth, high ponytail, [Style of boku no hero academia]",
    #     "sampler": "DPM++ SDE Karras",
    #     "cfgScale": 7,
    #     "Clip skip": "2",
    #     "Hires upscale": "2",
    #     "Hires upscaler": "4x-AnimeSharp",
    #     "negativePrompt": "(worst quality, low quality, extra digits:1.3), easynegative,",
    #     "Denoising strength": "0.4"
    #   },

class Response_Images_Metadata(BaseModel):
    nextCursor: int | str | None = None  # The id of the first image in the next batch
    currentPage: Optional[int] = None # The the current page you are at (if paging)
    pageSize: Optional[int] = None  # The the size of the batch (if paging)
    nextPage: Optional[str] = None     #The url to get the next batch of items

class Response_Images_Item(BaseModel):
    id: int	# The id of the image
    url: str # The url of the image at it's source resolution
    hash: str # The blurhash of the image
    width: int # The width of the image
    height: int	# The height of the image
    nsfw: bool # If the image has any mature content labels
    nsfwLevel: NsfwLevel # The NSFW level of the image
    createdAt: str # (ISO 8601 format) The date the image was posted
    postId: int # The ID of the post the image belongs to
    stats: Response_Images_Stats
    # meta: Dict | None = None # this field is a non-structured object that contains additional information about the image, the meta structure will be different for each webui
    # username: Optional[str] = None # The username of the creator
    # baseModel: Optional[str] = None # The base model of the image

class Response_Images(BaseModel):
    items: List[Response_Images_Item]
    metadata: Response_Images_Metadata

class Images_API_Opts(BaseModel):
    limit: None | StrictInt = None # The number of results to be returned per page. This can be a number between 0 and 200. By default, each page will return 100 results.
    postId: None | StrictInt = None # The ID of a post to get images from
    modelId: None | StrictInt = None # The ID of a model to get images from (model gallery)
    modelVersionId: None | StrictInt = None # The ID of a model version to get images from (model gallery filtered to version)
    username: None | str = None # Filter to images from a specific user
    nsfw: None | bool | List[NsfwLevel] = None # Filter to images that contain mature content flags or not (undefined returns all)
    sort: None | Sort = None # The order in which you wish to sort the results
    period: None | Period = None # The time frame in which the images will be sorted
    page: None | StrictInt = None # The page from which to start fetching creators