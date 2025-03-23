from .base.misc import Model_Types, Sort, Period, AllowCommercialUse
from .modelId_endpoint import ModelId_Response
from pydantic import BaseModel, StrictBool, StrictInt
from typing import List

class Models_Response_Metadata(BaseModel):
    totalItems: int | None = None 	# The total number of items available
    currentPage: int | None = None 	# The the current page you are at
    pageSize: int | None = None 	# The the size of the batch
    totalPages: int | None = None 	# The total number of pages
    nextPage: str | None = None	# The url to get the next batch of items
    prevPage: str | None = None	# The url to get the previous batch of items

class Models_Response(BaseModel):
    items: List[ModelId_Response]
    metadata: Models_Response_Metadata

class Models_API_Opts(BaseModel):
    limit: 	None | StrictInt = None 	# The number of results to be returned per page. This can be a number between 1 and 100. By default, each page will return 100 results
    page: 	None | StrictInt = None 	# The page from which to start fetching models
    query: 	None | str = None 	# Search query to filter models by name
    tag: 	None | str = None 	# Search query to filter models by tag
    username: 	None | str = None 	# Search query to filter models by user
    types: List[Model_Types] | None = None 	# The type of model you want to filter with. If none is specified, it will return all types
    sort: 	None | Sort = None 	# The order in which you wish to sort the results
    period: None | Period = None 	# The time frame in which the models will be sorted
    rating: None | StrictInt = None 	# The rating you wish to filter the models with. If none is specified, it will return models with any rating
    favorites: None | StrictBool = None 	# (AUTHED) Filter to favorites of the authenticated user (this requires an API token or session cookie)
    hidden: None | StrictBool = None 	# (AUTHED) Filter to hidden models of the authenticated user (this requires an API token or session cookie)
    primaryFileOnly: None | StrictBool = None 	# Only include the primary file for each model (This will use your preferred format options if you use an API token or session cookie)
    allowNoCredit: None | StrictBool = None 	# Filter to models that require or don't require crediting the creator
    allowDerivatives: None | StrictBool = None 	# Filter to models that allow or don't allow creating derivatives
    allowDifferentLicenses: None | StrictBool = None # Filter to models that allow or don't allow derivatives to have a different license
    allowCommercialUse: List[AllowCommercialUse] | None = None 	# Filter to models based on their commercial permissions
    nsfw: None | StrictBool = None # If false, will return safer images and hide models that don't have safe images
    supportsGeneration: None | StrictBool = None 	# If true, will return models that support generation
    token: str # required for search models