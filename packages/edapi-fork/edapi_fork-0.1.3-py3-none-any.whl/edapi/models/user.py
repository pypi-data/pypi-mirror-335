from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from enum import Enum
from edapi.types.api_types.endpoints.user import API_User_Response
from .course import CourseInfo, CourseStatus
import json




class User(BaseModel):
    """
    Extract user data from the API response and transform it into our model. 
    Removed redundant fields and added various helper methods
    """
    id: int
    name: str
    email: str
    courses: List[CourseInfo]

    def get_course_by_id(self, course_id: int) -> Optional[CourseInfo]:
        """Get a course by its ID"""
        for course in self.courses:
            if course.course.id == course_id:
                return course
        return None

    def get_course_by_code(self, code: str) -> Optional[CourseInfo]:
        """Get a course by its code"""
        for course in self.courses:
            if course.course.code == code:
                return course
        return None

    def get_active_courses(self) -> List[CourseInfo]:
        """Returns a list of active courses."""
        return [course for course in self.courses if course.status == CourseStatus.ACTIVE]

    @classmethod
    def from_api_response(cls, api_response:API_User_Response ) -> "User":
        """
        Create a User instance from the EdAPI response.

        The EdAPI response has a different structure than our model,
        so we need to transform it.

        Args:
            api_response: The raw JSON response from EdAPI

        Returns:
            A User instance populated with data from the API response
        """
        # Extract user data
        user_data = api_response.get('user', {})

        # Extract courses data
        courses_data = api_response.get('courses', [])

        # Transform each course into our model structure
        courses = []
        for course_data in courses_data:
            # Create the CourseInfo object
            course_status_str = course_data.get('course', {}).get('status', CourseStatus.ARCHIVED)
            course_info = CourseInfo(
                id=course_data.get('course', {}).get('id', 0),
                code=course_data.get('course', {}).get('code', ''),
                name=course_data.get('course', {}).get('name', ''),
                year=course_data.get('course', {}).get('year', ''),
                session=course_data.get('course', {}).get('session', ''),
                status=CourseStatus(course_status_str) ,
                created_at=course_data.get('course', {}).get('created_at', ''),
                last_active=course_data.get('last_active', '') )
            courses.append(course_info)

        return cls(**{
            'id': user_data.get('id', 0),
            'name': user_data.get('name', ''),
            'email': user_data.get('email', ''),
            'courses': courses
        })
    
    def __str__(self) -> str:
        """Format User as a pretty-printed JSON string"""
        return json.dumps(self.model_dump(), indent=2, default=str)
    
    def __repr__(self) -> str:
        """Return a string representation of User"""
        return f"User(id={self.id}, name='{self.name}', courses={len(self.courses)})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert User to a dictionary"""
        return self.model_dump()
