from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import date

class TaskSchema(BaseModel):
    id: Optional[UUID]
    title: str
    description: Optional[str] = None
    completed: bool
    estimated_hours: float
    user_story_id: Optional[UUID] = None
    sprint_id: UUID 

    class Config:
        orm_mode = True

# Pydantic Model for Sprint
class SprintSchema(BaseModel):
    id: Optional[UUID]
    start_date: date
    end_date: date

    class Config:
        orm_mode = True

# Pydantic Model for User Story
class UserStorySchema(BaseModel):
    id: Optional[UUID]
    story: str
    sprint_id: Optional[UUID]

    class Config:
        orm_mode = True

# Pydantic model for TeamMember
class TeamMemberSchema(BaseModel):
    id: UUID
    name: str
    skills: List[str] 
    available_hours: int

    class Config:
        orm_mode = True

# Pydantic model for Task Allocation Input
class TaskAllocationInput(BaseModel):
    task_id: UUID
    required_skills: List[str]
    estimated_hours: float

# Pydantic model for Task Allocation Output
class TaskAllocationOutput(BaseModel):
    task_id: UUID
    assigned_member_id: Optional[UUID]
    message: str

class UserSchema(BaseModel):
    id: Optional[UUID]
    name: str
    skills: List[str]
    available_hours: int

    class Config:
        orm_mode = True

# Pydantic model for Sprint Performance Metrics
class SprintPerformanceMetrics(BaseModel):
    sprint_id: UUID
    total_tasks: int
    completed_tasks: int
    total_estimated_hours: float
    completed_estimated_hours: float
    completion_rate: float
    sprint_progress: float

    class Config:
        orm_mode = True

class SprintData(BaseModel):
    start_date: str
    end_date: str
    total_tasks: int
    total_estimated_hours: float