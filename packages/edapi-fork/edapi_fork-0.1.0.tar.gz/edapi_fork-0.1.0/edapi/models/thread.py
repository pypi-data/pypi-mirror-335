from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SimpleThreadUser(BaseModel):
    """Simplified user information."""
    id: int
    name: str


class SimpleThreadComment(BaseModel):
    """Simplified comment model with only essential fields."""
    id: int
    user_id: int
    course_id: int
    thread_id: int
    parent_id: Optional[int] = None
    type: str
    document: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        extra = 'ignore'  # Ignore extra fields in the API response


class SimpleThread(BaseModel):
    """Simplified thread model with only the fields you need."""
    id: int
    user_id: int
    course_id: int
    type: str
    title: str
    document: str
    category: str
    subcategory: str
    subsubcategory: str
    unique_view_count: int
    vote_count: int
    created_at: datetime
    updated_at: datetime
    user: Optional[SimpleThreadUser] = None

    class Config:
        extra = 'ignore'  # Ignore extra fields in the API response


class SimpleThreadWithComments(SimpleThread):
    """Thread with comments included."""
    comments: List[SimpleThreadComment] = []
