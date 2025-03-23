import pytest
import httpx
import os
pytestmark = pytest.mark.anyio

from src.civitai_api.v1 import creators, async_creators, images, \
    async_images, models, async_models, get_model_by_id, async_get_model_by_id, \
    get_model_by_versionId, async_get_model_by_versionId, get_model_by_hash, \
    async_get_model_by_hash, tags, async_tags
from dotenv import load_dotenv
load_dotenv()
proxy = os.environ.get('PROXY', None)
api_key = os.environ.get('API_KEY', None)

# 1. Initialization httpx client at first
@pytest.fixture
def httpx_client():
    with httpx.Client(proxy = proxy) as client:
        yield client

@pytest.fixture
async def httpx_async_client():
    async with httpx.AsyncClient(proxy = proxy) as async_client:
        yield async_client

# 2. prepare query paramters
@pytest.fixture
def creators_request_queru_params():
    from src.civitai_api.v1.models.creators_endpoint import Creators_API_Opts
    return Creators_API_Opts(
        limit=20, 
        page=1, 
        query="Elesico"
        )

@pytest.fixture
def images_request_query_params():
    from src.civitai_api.v1.models.images import NsfwLevel, Sort, Period, Images_API_Opts
    return Images_API_Opts(
        limit=2, 
        postId=9178972, 
        modelId=949620, 
        modelVersionId=1063193, 
        username="Elesico", 
        nsfw=[NsfwLevel.X], 
        sort=Sort.Newest, 
        period=Period.AllTime,
        page=2
        )

@pytest.fixture
def models_request_query_params():
    from src.civitai_api.v1.models.models_endpoint import Models_API_Opts, Sort, Period, Model_Types, AllowCommercialUse
    return Models_API_Opts(
        limit=20,
        page=1,
        query="VSK-94 | Girls' Frontline",
        tag="girls_frontline",
        username="LeonDoesntDraw",
        types=[Model_Types.LORA],
        sort=Sort.Newest,
        period=Period.AllTime,
        rating=5,
        favorites=False,
        hidden=False,
        primaryFileOnly=False,
        # allowNoCredit=True,
        # allowDerivatives=True,
        allowDifferentLicenses=True,
        allowCommercialUse=[AllowCommercialUse.Image, AllowCommercialUse.Rent, AllowCommercialUse.Sell],
        nsfw=True,
        supportsGeneration=True,
        token=api_key
    )

@pytest.fixture
def model_id():
    return 11821

@pytest.fixture
def model_version_id():
    return 127062

@pytest.fixture
def model_hash():
    return "253BD9C3037584A20AD46C833E9BC90A1F8F7EA031FD81BF1E8392DBC9C45F3E"

@pytest.fixture
def tags_request_query_params():
    from src.civitai_api.v1.models.tags_endpoint import Tags_API_Opts
    return Tags_API_Opts(
        limit=20,
        page=1,
        query="girls_frontline"
        )

# 3. make queries
class TestAPI_V1:
    def test_creators(self, httpx_client, creators_request_queru_params):
        response = creators(httpx_client, creators_request_queru_params)
        assert response.metadata.totalItems == 1
        assert response.items[0].username == "Elesico"
    
    async def test_async_creators(self, httpx_async_client, creators_request_queru_params):
        response = await async_creators(httpx_async_client, creators_request_queru_params)
        assert response.metadata.totalItems == 1
        assert response.items[0].username == "Elesico"

    def test_images(self, httpx_client, images_request_query_params):
        response = images(httpx_client, images_request_query_params)
        assert len(response.items) == 2
        assert response.metadata.pageSize == 2
        assert response.metadata.currentPage == 2

    async def test_async_images(self, httpx_async_client, images_request_query_params):
        response = await async_images(httpx_async_client, images_request_query_params)
        assert len(response.items) == 2
        assert response.metadata.pageSize == 2
        assert response.metadata.currentPage == 2

def test_models(httpx_client, models_request_query_params):
    response = models(httpx_client, models_request_query_params)
    assert len(response.items) == 1
    assert response.metadata.pageSize == 20
    assert response.items[0].id == 11821


async def test_async_models(httpx_async_client, models_request_query_params):
    response = await async_models(httpx_async_client, models_request_query_params)
    assert len(response.items) == 1
    assert response.metadata.pageSize == 20
    assert response.items[0].id == 11821

def test_get_model_by_id(httpx_client, model_id):
    response = get_model_by_id(httpx_client, model_id)
    assert response.id == model_id

async def test_async_get_model_by_id(httpx_async_client, model_id):
    response = await async_get_model_by_id(httpx_async_client, model_id)
    assert response.id == model_id

def test_get_model_by_versionId(httpx_client, model_version_id):
    response = get_model_by_versionId(httpx_client, model_version_id)
    assert response.id == model_version_id

async def test_async_get_model_by_versionId(httpx_async_client, model_version_id):
    response = await async_get_model_by_versionId(httpx_async_client, model_version_id)
    assert response.id == model_version_id

def test_get_model_by_hash(httpx_client, model_hash):
    response = get_model_by_hash(httpx_client, model_hash)
    assert response.files[0].hashes.BLAKE3 == model_hash

async def test_async_get_model_by_hash(httpx_async_client, model_hash):
    response = await async_get_model_by_hash(httpx_async_client, model_hash)
    assert response.files[0].hashes.BLAKE3 == model_hash

def test_tags(httpx_client, tags_request_query_params):
    response = tags(httpx_client, tags_request_query_params)
    assert len(response.items) > 0
    assert response.metadata.pageSize == 20

async def test_async_tags(httpx_async_client, tags_request_query_params):
    response = await async_tags(httpx_async_client, tags_request_query_params)
    assert len(response.items) > 0
    assert response.metadata.pageSize == 20

def test_httpx_query_params():
    from src.civitai_api.v1.models.models_endpoint import Models_Response
    non_nsfw_result = httpx.get(url="https://civitai.com/api/v1/models",params={"nsfw":False, "username":"kind5516", "query":"channel_style"}).json()
    non_nsfw_result = Models_Response(**non_nsfw_result)
    assert len(non_nsfw_result.items) == 0

    nsfw_result = httpx.get(url="https://civitai.com/api/v1/models", params={"nsfw":True, "username":"kind5516", "query":"channel_style"}).json()
    nsfw_result = Models_Response(**nsfw_result)
    assert nsfw_result.items[0].id == 1318764