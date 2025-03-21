from typing import List, Dict,  Any
from pydantic import BaseModel
from enum import Enum
import json
class CourseStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    
class CourseInfo(BaseModel):
    id: int
    code: str
    name: str
    year: str
    session: str
    status: str
    created_at: str
    last_active: str
    status: CourseStatus

    def __str__(self) -> str:
        """Format UserCourse as a pretty-printed JSON string"""
        return json.dumps(self.model_dump(), indent=2, default=str)
    
    def __repr__(self) -> str:
        """Return a string representation of UserCourse"""
        return f"UserCourse(course={self.name},)"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert UserCourse to a dictionary"""
        return self.model_dump()