from typing import TypedDict

class StaffLink(TypedDict):
    name: str
    link: str
    academic_title: str
    department: str
    phone: str
    email: str

class UserID(StaffLink):
    user_id: str

class ResearchPaper(UserID):
    paper_title: str
    paper_link: str
    year: str
