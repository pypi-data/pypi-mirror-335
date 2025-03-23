from typing import List
from pydantic import BaseModel, StrictInt

class Response_Tags_Metadata(BaseModel):
    totalItems: StrictInt # The total number of items available
    currentPage: StrictInt # The the current page you are at
    pageSize: StrictInt # The the size of the batch
    totalPages: StrictInt # The total number of pages
    nextPage: str | None = None # The url to get the next batch of items
    prevPage: str | None = None # The url to get the previous batch of items

class Response_Tags_Items(BaseModel):
    name: str # The name of the tag
    link: str # Url to get all models from this tag

class Response_Tags(BaseModel):
    items: List[Response_Tags_Items]
    metadata: Response_Tags_Metadata

class Tags_API_Opts(BaseModel):
    limit: StrictInt # The number of results to be returned per page. This can be a number between 1 and 200. By default, each page will return 20 results. If set to 0, it'll return all the tags
    page: StrictInt # The page from which to start fetching tags
    query: str # Search query to filter tags by name
