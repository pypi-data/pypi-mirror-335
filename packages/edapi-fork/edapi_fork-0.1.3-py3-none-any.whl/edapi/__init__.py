"""
Package for Ed API Python integration.
"""

# the only default import should be the API class
from .edapi import EdAPI
from .models.user import User
from .models.course import CourseInfo

__all__ = ["EdAPI", "User", "CourseInfo", "CourseInfo"]
