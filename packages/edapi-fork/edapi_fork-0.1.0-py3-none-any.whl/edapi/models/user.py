from typing import List, Dict, Optional, Any
from pydantic import BaseModel


class Category(BaseModel):
    name: str
    subcategories: List['Category'] = []
    thread_template: Optional[str] = None


class CourseSettings(BaseModel):
    default_page: str
    discussion: Dict[str, Any]
    # Add other settings as needed


class CourseInfo(BaseModel):
    id: int
    code: str
    name: str
    year: str
    session: str
    status: str
    created_at: str


class CourseRole(BaseModel):
    user_id: int
    course_id: int
    lab_id: Optional[int] = None
    role: str
    tutorial: Optional[str] = None


class UserCourse(BaseModel):
    course: CourseInfo
    role: CourseRole
    last_active: str
    lab: Optional[Any] = None


class UserInfoSummary(BaseModel):
    """A simplified model containing just the essential user info."""
    name: str
    email: str
    courses: List[Dict[str, Any]]


class User(BaseModel):
    id: int
    name: str
    email: str
    courses: List[UserCourse]

    def get_course_by_id(self, course_id: int) -> Optional[UserCourse]:
        """Get a course by its ID"""
        for course in self.courses:
            if course.course.id == course_id:
                return course
        return None

    def get_course_by_code(self, code: str) -> Optional[UserCourse]:
        """Get a course by its code"""
        for course in self.courses:
            if course.course.code == code:
                return course
        return None

    def get_user_info_summary(self) -> UserInfoSummary:
        """Returns a simplified object with essential user information."""
        course_list = []
        for course in self.courses:
            c = course.course
            course_list.append({
                'id': c.id,
                'code': c.code,
                'name': c.name,
                'year': c.year,
                'session': c.session,
                'status': c.status,
                'role': course.role.role
            })

        return UserInfoSummary(
            name=self.name,
            email=self.email,
            courses=course_list
        )

    def get_active_courses(self) -> List[UserCourse]:
        """Returns a list of active courses."""
        return [course for course in self.courses if course.last_active]

    @classmethod
    def from_api_response(cls, api_response: Dict[str, Any]) -> "User":
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
            course_info = CourseInfo(
                id=course_data.get('course', {}).get('id', 0),
                code=course_data.get('course', {}).get('code', ''),
                name=course_data.get('course', {}).get('name', ''),
                year=course_data.get('course', {}).get('year', ''),
                session=course_data.get('course', {}).get('session', ''),
                status=course_data.get('course', {}).get('status', ''),
                created_at=course_data.get('course', {}).get('created_at', '')
            )

            # Create the CourseRole object
            role_data = course_data.get('role', {})
            course_role = CourseRole(
                user_id=role_data.get('user_id', 0),
                course_id=role_data.get('course_id', 0),
                lab_id=role_data.get('lab_id'),
                role=role_data.get('role', ''),
                tutorial=role_data.get('tutorial')
            )

            # Create the UserCourse object
            user_course = UserCourse(
                course=course_info,
                role=course_role,
                last_active=course_data.get('last_active', ''),
                lab=course_data.get('lab')
            )

            courses.append(user_course)

        return cls(**{
            'id': user_data.get('id', 0),
            'name': user_data.get('name', ''),
            'email': user_data.get('email', ''),
            'courses': courses
        })
