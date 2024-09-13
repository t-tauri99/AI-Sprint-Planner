from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import JSON 
import uuid

Base = declarative_base()

#Create Users table
class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    skills = Column(JSON)
    available_hours = Column(Integer)
    tasks = relationship("Task", back_populates="user")

#Create Tasks table
class Task(Base):
    __tablename__ = 'tasks'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    estimated_hours = Column(Float)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    user_story_id = Column(UUID(as_uuid=True), ForeignKey('user_stories.id'))
    user = relationship("User", back_populates="tasks")
    sprint_id = Column(UUID(as_uuid=True), ForeignKey('sprints.id'))
    user_story = relationship("UserStory", back_populates="tasks")
    sprint = relationship("Sprint", back_populates="tasks")

#Create User Stories table
class UserStory(Base):
    __tablename__ = 'user_stories'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story = Column(String)
    sprint_id = Column(UUID(as_uuid=True), ForeignKey('sprints.id'))
    tasks = relationship("Task", back_populates="user_story")

#Create Sprints table
class Sprint(Base):
    __tablename__ = 'sprints'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    start_date = Column(Date)
    end_date = Column(Date)
    user_stories = relationship("UserStory", back_populates="sprint")
    tasks = relationship("Task", back_populates="sprint")

UserStory.sprint = relationship("Sprint", back_populates="user_stories")
Task.user_story = relationship("UserStory", back_populates="tasks")

# Setup database connection
engine = create_engine('postgresql://postgres:vibhav123@localhost/sprint planning')
Base.metadata.create_all(engine)
#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
