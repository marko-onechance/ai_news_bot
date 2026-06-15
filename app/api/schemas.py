from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SourceBase(BaseModel):
    name: str
    type: str
    url: str
    enabled: bool = True


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    url: Optional[str] = None
    enabled: Optional[bool] = None


class SourceOut(SourceBase):
    id: int
    model_config = {"from_attributes": True}



class KeywordBase(BaseModel):
    word: str


class KeywordCreate(KeywordBase):
    pass


class KeywordOut(KeywordBase):
    id: int
    model_config = {"from_attributes": True}



class NewsItemOut(BaseModel):
    id: int
    title: str
    url: Optional[str]
    summary: Optional[str]
    source: str
    published_at: datetime
    raw_text: Optional[str]
    model_config = {"from_attributes": True}



class PostOut(BaseModel):
    id: int
    news_id: int
    generated_text: str
    published_at: Optional[datetime]
    status: str
    model_config = {"from_attributes": True}



class TriggerResponse(BaseModel):
    task_id: str
    status: str



class GenerateRequest(BaseModel):
    news_id: int


class GenerateResponse(BaseModel):
    post_id: int
    news_id: int
    generated_text: str
    status: str