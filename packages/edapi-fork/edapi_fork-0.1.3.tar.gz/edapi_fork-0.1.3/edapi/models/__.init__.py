"""
Models for working with Ed API data.
"""

from .user import (
    User,
)

from .thread import (
    SimpleThreadUser,
    SimpleThreadComment,
    SimpleThread,
    SimpleThreadWithComments
)

from .course import (
    CourseInfo,
    CourseRole,
)

__all__ = [
    'User',
    'CourseInfo',
    'CourseRole',
    'SimpleThreadUser',
    'SimpleThreadComment',
    'SimpleThread',
    'SimpleThreadWithComments',
]
