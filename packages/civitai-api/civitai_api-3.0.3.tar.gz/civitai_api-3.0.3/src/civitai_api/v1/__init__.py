import httpx
from urllib.parse import urljoin
from typing import Any, Dict, List, Type, TypeVar
from pydantic import BaseModel, StrictBool, StrictInt

from .models.versionId_endpoint import modelVersion_endpoint_modelVersion
from .models.base.misc import Model_Types, Sort, Period, AllowCommercialUse, NsfwLevel
from .models.models_endpoint import Models_API_Opts, Models_Response
from .models.modelId_endpoint import ModelId_Response, ModelId_ModelVersion
from .models.creators_endpoint import Creators_API_Opts, Response_Creaters
from .models.images import Images_API_Opts, Response_Images
from .models.tags_endpoint import Tags_API_Opts, Response_Tags
# API endpoints references: https://github.com/civitai/civitai/wiki/REST-API-Reference

API_URL_V1 = "https://civitai.com/api/v1/"
API_URL_V1_Creators = urljoin(API_URL_V1, "creators") # https://civitai.com/api/v1/creators
API_URL_V1_Images = urljoin(API_URL_V1, "images") # https://civitai.com/api/v1/images
API_URL_V1_Models = urljoin(API_URL_V1, "models") # https://civitai.com/api/v1/models
API_URL_V1_Model_By_Id = urljoin(API_URL_V1, "models/") # "https://civitai.com/api/v1/models/:modelId"
API_URL_ModelVersion_By_VersionId = urljoin(API_URL_V1, "model-versions/")  # "https://civitai.com/api/v1/model-versions/:modelVersionId"
API_URL_ModelVersion_By_Hash = urljoin(API_URL_V1, "model-versions/by-hash/") # "https://civitai.com/api/v1/model-versions/by-hash/:hash"
API_URL_Tags = urljoin(API_URL_V1, "tags") # https://civitai.com/api/v1/tags

class QueryParamsError(Exception):
    def __init__(self, response_json: str, *args):
        super().__init__(*args)
        self.response_json = response_json

    def __str__(self):
        return f"{self.response_json}"

class LoraNotExistsError(Exception):
    def __init__(self, response_json: str, *args):
        super().__init__(*args)
        self.response_json = response_json
    
    def __str__(self):
        return f"{self.response_json}"

class ReachRequestLimitationError(Exception):
    def __init__(self, response_json: str, *args):
        super().__init__(*args)
        self.response_json = response_json

    def __str__(self):
        return f"{self.response_json}"

T = TypeVar('T')

def response_check_for_multi_results(response: httpx.Response, response_type: Type[T]) -> T:
    obj = response.json()
    if hasattr(obj, "error"): # notice that for those api endpoints that return a single result, the error message is different
        raise QueryParamsError(response.text)
    if hasattr(obj, "message"):
        raise ReachRequestLimitationError(response.text) # Server connection limitation reached
    return response_type(**obj)

def response_check_for_single_result(response: httpx.Response, response_type: Type[T]) -> T:
    if response.status_code >= 299 or response.status_code < 200:
        raise Exception(f"Error: {response.text}")
    obj = response.json()
    if hasattr(obj, "error"): # only no result matches will return error msg.
        raise LoraNotExistsError(response.text)
    if hasattr(obj, "message"):
        raise ReachRequestLimitationError(response.text)
    return response_type(**obj)

def creators(
        httpx_client:httpx.Client,
        opts: Creators_API_Opts | None = None
        ) -> Response_Creaters:
    if opts:
        query_params = opts.model_dump(exclude_none=True, exclude_defaults=True, exclude_unset=True)
    else:
        query_params = None
    response = httpx_client.get(API_URL_V1_Creators, params=query_params)
    result = response_check_for_multi_results(response, Response_Creaters)
    return result

async def async_creators(
        async_httpx_client:httpx.AsyncClient,
        opts: Creators_API_Opts | None = None
        ) -> Response_Creaters:
    if opts:
        query_params = opts.model_dump(exclude_none=True, exclude_defaults=True, exclude_unset=True)
    else:
        query_params = None
    response = await async_httpx_client.get(API_URL_V1_Creators, params=query_params)
    result = response_check_for_multi_results(response, Response_Creaters)
    return result

def images(
        httpx_client:httpx.Client,
        opts: Images_API_Opts | None = None
        ) -> Response_Images:
    if opts:
        query_params = opts.model_dump(exclude_none=True, exclude_defaults=True, exclude_unset=True)
    response = httpx_client.get(API_URL_V1_Images, params=query_params)
    result = response_check_for_multi_results(response, Response_Images)
    return result

async def async_images(
        async_httpx_client:httpx.AsyncClient,
        opts: Images_API_Opts | None = None
) -> Response_Images:
    if opts:
        query_params = opts.model_dump(exclude_none=True, exclude_defaults=True, exclude_unset=True)
    else:
        query_params = None
    response = await async_httpx_client.get(API_URL_V1_Images, params=query_params)
    result = response_check_for_multi_results(response, Response_Images)
    return result

def models(
        httpx_client:httpx.Client,
        opts: Models_API_Opts | None = None
) -> Models_Response:
    if (opts):
        if (opts.favorites or opts.hidden):
            if not (httpx_client.headers):
                raise ValueError("If the \'favorites\' and the \'hidden\' params were set, The api_key must be provided while initialize CivitaiAPI class.")
            
    if opts:
        query_params = opts.model_dump(exclude_none=True, exclude_defaults=True, exclude_unset=True)
    else:
        query_params = None
    response = httpx_client.get(API_URL_V1_Models, params=query_params)
    result = response_check_for_multi_results(response, Models_Response)
    return result

async def async_models(
        async_httpx_client:httpx.AsyncClient,
        opts: Models_API_Opts | None = None
) -> Models_Response:
    if (opts):
        if (opts.favorites or opts.hidden):
            if not (async_httpx_client.headers):
                raise ValueError("If the \'favorites\' and the \'hidden\' params were set, The api_key must be provided while initialize CivitaiAPI class.")
            
    if opts:
        query_params = opts.model_dump(exclude_none=True, exclude_defaults=True, exclude_unset=True)
    else:
        query_params = None
    response = await async_httpx_client.get(API_URL_V1_Models, params=query_params)
    result = response_check_for_multi_results(response, Models_Response)
    return result

def get_model_by_id(
        httpx_client:httpx.Client,
        modelId: int
) -> ModelId_Response:
    response = httpx_client.get(urljoin(API_URL_V1_Model_By_Id, str(modelId)))
    result = response_check_for_single_result(response, ModelId_Response)
    return result

async def async_get_model_by_id(
        async_httpx_client:httpx.AsyncClient,
        modelId: int
) -> ModelId_Response:
    response = await async_httpx_client.get(urljoin(API_URL_V1_Model_By_Id, str(modelId)))
    result = response_check_for_single_result(response, ModelId_Response)
    return result

def get_model_by_versionId(
        httpx_client:httpx.Client,
        modelVersionId: int
) -> modelVersion_endpoint_modelVersion:
    response = httpx_client.get(urljoin(API_URL_ModelVersion_By_VersionId, str(modelVersionId)))
    result = response_check_for_single_result(response, modelVersion_endpoint_modelVersion)
    return result

async def async_get_model_by_versionId(
        async_httpx_client:httpx.AsyncClient,
        modelVersionId: int
) -> modelVersion_endpoint_modelVersion:
    response = await async_httpx_client.get(urljoin(API_URL_ModelVersion_By_VersionId, str(modelVersionId)))
    result = response_check_for_single_result(response, modelVersion_endpoint_modelVersion)
    return result

def get_model_by_hash(
        httpx_client:httpx.Client,
        hash: str
) -> modelVersion_endpoint_modelVersion:
    response = httpx_client.get(urljoin(API_URL_ModelVersion_By_Hash, hash))
    result = response_check_for_single_result(response, modelVersion_endpoint_modelVersion)
    return result

async def async_get_model_by_hash(
        async_httpx_client:httpx.AsyncClient,
        hash: str
) -> modelVersion_endpoint_modelVersion:
    url = urljoin(API_URL_ModelVersion_By_Hash, hash)
    response = await async_httpx_client.get(url=url)
    result = response_check_for_single_result(response, modelVersion_endpoint_modelVersion)
    return result

def tags(
        httpx_client:httpx.Client,
        opts: Tags_API_Opts | None = None
) -> Response_Tags:
    if opts:
        query_params = opts.model_dump(exclude_none=True, exclude_defaults=True, exclude_unset=True)
    else:
        query_params = None
    response = httpx_client.get(API_URL_Tags, params=query_params)
    result = response_check_for_multi_results(response, Response_Tags)
    return result

async def async_tags(
        async_httpx_client:httpx.AsyncClient,
        opts: Tags_API_Opts | None = None
) -> Response_Tags:
    if opts:
        query_params = opts.model_dump(exclude_none=True, exclude_defaults=True, exclude_unset=True)
    else:
        query_params = None
    response = await async_httpx_client.get(API_URL_Tags, params=query_params)
    result = response_check_for_multi_results(response, Response_Tags)
    return result

class CiviClient:
    def __init__(
            self, 
            api_key: str, 
            httpx_client: httpx.Client = httpx.Client(), 
            async_httpx_client: httpx.AsyncClient = httpx.AsyncClient()
            ):
        self.api_key = api_key
        self.httpx_client = httpx_client
        self.async_httpx_client = async_httpx_client

    def creators(
            self, 
            limit: None | StrictInt = None, 
            page: None | StrictInt = None, 
            query: None | str = None
            ):
        opts = Creators_API_Opts(limit=limit, page=page, query=query)
        return creators(self.httpx_client, opts)

    async def async_creators(
            self, 
            limit: None | StrictInt = None, 
            page: None | StrictInt = None, 
            query: None | str = None
            ) -> Response_Creaters:
        opts = Creators_API_Opts(limit=limit, page=page, query=query)
        return await async_creators(self.async_httpx_client, opts)

    def images(
            self, 
            limit: None | StrictInt = None, 
            postId: None | StrictInt = None, 
            modelId: None | StrictInt = None, 
            modelVersionId: None | StrictInt = None, 
            username: None | str = None, 
            nsfw: None | bool | list[NsfwLevel] = None, 
            sort: None | Sort = None, 
            period: None | Period = None, 
            page: None | StrictInt = None
            ) -> Response_Images:
        opts: Images_API_Opts = Images_API_Opts(
            limit=limit,
            postId=postId,
            modelId=modelId,
            modelVersionId=modelVersionId,
            username=username,
            nsfw=nsfw,
            sort=sort,
            period=period,
            page=page
        )
        return images(self.httpx_client, opts)

    async def async_images(
            self, 
            limit: None | StrictInt = None, 
            postId: None | StrictInt = None, 
            modelId: None | StrictInt = None, 
            modelVersionId: None | StrictInt = None, 
            username: None | str = None, 
            nsfw: None | bool | list[NsfwLevel] = None, 
            sort: None | Sort = None, 
            period: None | Period = None, 
            page: None | StrictInt = None
            ) -> Response_Images:
        opts: Images_API_Opts = Images_API_Opts(
            limit=limit,
            postId=postId,
            modelId=modelId,
            modelVersionId=modelVersionId,
            username=username,
            nsfw=nsfw,
            sort=sort,
            period=period,
            page=page
        )
        return await async_images(self.async_httpx_client, opts)

    def models(
            self, 
            limit: 	None | StrictInt = None, 	# The number of results to be returned per page. This can be a number between 1 and 100. By default, each page will return 100 results
            page: 	None | StrictInt = None, 	# The page from which to start fetching models
            query: 	None | str = None, 	# Search query to filter models by name
            tag: 	None | str = None, 	# Search query to filter models by tag
            username: 	None | str = None, 	# Search query to filter models by user
            types: List[Model_Types] | None = None, 	# The type of model you want to filter with. If none is specified, it will return all types
            sort: 	None | Sort = None, 	# The order in which you wish to sort the results
            period: None | Period = None, 	# The time frame in which the models will be sorted
            rating: None | StrictInt = None, 	# The rating you wish to filter the models with. If none is specified, it will return models with any rating
            favorites: None | StrictBool = None, 	# (AUTHED) Filter to favorites of the authenticated user (this requires an API token or session cookie)
            hidden: None | StrictBool = None, 	# (AUTHED) Filter to hidden models of the authenticated user (this requires an API token or session cookie)
            primaryFileOnly: None | StrictBool = None, 	# Only include the primary file for each model (This will use your preferred format options if you use an API token or session cookie)
            allowNoCredit: None | StrictBool = None, 	# Filter to models that require or don't require crediting the creator
            allowDerivatives: None | StrictBool = None, 	# Filter to models that allow or don't allow creating derivatives
            allowDifferentLicenses: None | StrictBool = None, # Filter to models that allow or don't allow derivatives to have a different license
            allowCommercialUse: List[AllowCommercialUse] | None = None, 	# Filter to models based on their commercial permissions
            nsfw: None | StrictBool = None, # If false, will return safer images and hide models that don't have safe images
            supportsGeneration: None | StrictBool = None, 	# If true, will return models that support generation
            ) -> Models_Response:
        opts: Models_API_Opts = Models_API_Opts(
            limit=limit,
            page=page,
            query=query,
            tag=tag,
            username=username,
            types=types,
            sort=sort,
            period=period,
            rating=rating,
            favorites=favorites,
            hidden=hidden,
            primaryFileOnly=primaryFileOnly,
            allowNoCredit=allowNoCredit,
            allowDerivatives=allowDerivatives,
            allowDifferentLicenses=allowDifferentLicenses,
            allowCommercialUse=allowCommercialUse,
            nsfw=nsfw,
            supportsGeneration=supportsGeneration,
            token=self.api_key
        )
        return models(self.httpx_client, opts)

    async def async_models(self, 
            limit: 	None | StrictInt = None, 	# The number of results to be returned per page. This can be a number between 1 and 100. By default, each page will return 100 results
            page: 	None | StrictInt = None, 	# The page from which to start fetching models
            query: 	None | str = None, 	# Search query to filter models by name
            tag: 	None | str = None, 	# Search query to filter models by tag
            username: 	None | str = None, 	# Search query to filter models by user
            types: List[Model_Types] | None = None, 	# The type of model you want to filter with. If none is specified, it will return all types
            sort: 	None | Sort = None, 	# The order in which you wish to sort the results
            period: None | Period = None, 	# The time frame in which the models will be sorted
            rating: None | StrictInt = None, 	# The rating you wish to filter the models with. If none is specified, it will return models with any rating
            favorites: None | StrictBool = None, 	# (AUTHED) Filter to favorites of the authenticated user (this requires an API token or session cookie)
            hidden: None | StrictBool = None, 	# (AUTHED) Filter to hidden models of the authenticated user (this requires an API token or session cookie)
            primaryFileOnly: None | StrictBool = None, 	# Only include the primary file for each model (This will use your preferred format options if you use an API token or session cookie)
            allowNoCredit: None | StrictBool = None, 	# Filter to models that require or don't require crediting the creator
            allowDerivatives: None | StrictBool = None, 	# Filter to models that allow or don't allow creating derivatives
            allowDifferentLicenses: None | StrictBool = None, # Filter to models that allow or don't allow derivatives to have a different license
            allowCommercialUse: List[AllowCommercialUse] | None = None, 	# Filter to models based on their commercial permissions
            nsfw: None | StrictBool = None, # If false, will return safer images and hide models that don't have safe images
            supportsGeneration: None | StrictBool = None, 	# If true, will return models that support generation
            ) -> Models_Response:
        opts: Models_API_Opts = Models_API_Opts(
            limit=limit,
            page=page,
            query=query,
            tag=tag,
            username=username,
            types=types,
            sort=sort,
            period=period,
            rating=rating,
            favorites=favorites,
            hidden=hidden,
            primaryFileOnly=primaryFileOnly,
            allowNoCredit=allowNoCredit,
            allowDerivatives=allowDerivatives,
            allowDifferentLicenses=allowDifferentLicenses,
            allowCommercialUse=allowCommercialUse,
            nsfw=nsfw,
            supportsGeneration=supportsGeneration,
            token=self.api_key
        )
        return await async_models(self.async_httpx_client, opts)

    def get_model_by_id(self, modelId: int):
        return get_model_by_id(self.httpx_client, modelId)

    async def async_get_model_by_id(self, modelId: int):
        return await async_get_model_by_id(self.async_httpx_client, modelId)

    def get_model_by_versionId(self, versionId: int):
        return get_model_by_versionId(self.httpx_client, versionId)

    async def async_get_model_by_versionId(self, versionId: int):
        return await async_get_model_by_versionId(self.async_httpx_client, versionId)

    def get_model_by_hash(self, hash: str):
        return get_model_by_hash(self.httpx_client, hash)
    
    async def async_get_model_by_hash(self, hash: str):
        return await async_get_model_by_hash(self.async_httpx_client, hash)
    
    def tags(self, opts: Tags_API_Opts):
        return tags(self.httpx_client, opts)
    
    async def async_tags(self, opts: Tags_API_Opts):
        return await async_tags(self.async_httpx_client, opts)
