from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List, Optional
from models_sprint import Base, engine, Task, User, UserStory, Sprint
from schemas import TaskSchema, SprintSchema, UserStorySchema, TeamMemberSchema, TaskAllocationOutput, TaskAllocationInput, UserSchema, SprintPerformanceMetrics
from services import allocate_task, calculate_sprint_metrics, generate_burn_down_chart
from RandomForest import SprintOptimizer
from uuid import UUID
from datetime import date

#initialize the FastAPI app
app = FastAPI()

#DB local config
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
optimizer = SprintOptimizer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Endpoint to read tasks with pagination
@app.get("/tasks/", response_model=List[TaskSchema])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = db.query(Task).offset(skip).limit(limit).all()
    return tasks

# Endpoint to create a new task
@app.post("/tasks/", response_model=TaskSchema)
def create_task(task: TaskSchema, db: Session = Depends(get_db)):
    db_task = Task(
        title=task.title, 
        description=task.description, 
        completed=task.completed,
        estimated_hours=task.estimated_hours,
        user_story_id=task.user_story_id,
        sprint_id=task.sprint_id
        )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

#Endpoint to create a new sprint
@app.post("/sprints/", response_model=SprintSchema)
def create_sprint(sprint: SprintSchema, db: Session = Depends(get_db)):
    db_sprint = Sprint(start_date=sprint.start_date, end_date=sprint.end_date)
    db.add(db_sprint)
    db.commit()
    db.refresh(db_sprint)
    return db_sprint

# Endpoint to get all sprints
@app.get("/sprints/", response_model=List[SprintSchema])
def read_sprints(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sprints = db.query(Sprint).offset(skip).limit(limit).all()
    return sprints

# Endpoint to create a new user story
@app.post("/user-stories/", response_model=UserStorySchema)
def create_user_story(user_story: UserStorySchema, db: Session = Depends(get_db)):
    db_user_story = UserStory(story=user_story.story, sprint_id=user_story.sprint_id)
    db.add(db_user_story)
    db.commit()
    db.refresh(db_user_story)
    return db_user_story

# Endpoint to get all user stories
@app.get("/user-stories/", response_model=List[UserStorySchema])
def read_user_stories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    user_stories = db.query(UserStory).offset(skip).limit(limit).all()
    return user_stories

# Endpoint to get user stories by sprint
@app.get("/sprints/{sprint_id}/user-stories/", response_model=List[UserStorySchema])
def read_user_stories_by_sprint(sprint_id: UUID, db: Session = Depends(get_db)):
    user_stories = db.query(UserStory).filter(UserStory.sprint_id == sprint_id).all()
    return user_stories

@app.post("/task-allocation/", response_model=List[TaskAllocationOutput])
def allocate_tasks(tasks: List[TaskAllocationInput], team_members: List[TeamMemberSchema], db: Session = Depends(get_db)):
    allocation_results = []
    for task in tasks:
        member_id, message = allocate_task(task, team_members)
        allocation_results.append(TaskAllocationOutput(task_id=task.task_id, assigned_member_id=member_id, message=message))

    return allocation_results

# Create a new user
@app.post("/users/", response_model=UserSchema)
def create_user(user: UserSchema, db: Session = Depends(get_db)):
    db_user = User(name=user.name, available_hours=user.available_hours, skills=user.skills)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Get all users
@app.get("/users/", response_model=List[UserSchema])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# Update an existing user
@app.put("/users/{user_id}", response_model=UserSchema)
def update_user(user_id: UUID, user: UserSchema, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.name = user.name
    db_user.skills = user.skills
    db_user.available_hours = user.available_hours
    db.commit()
    db.refresh(db_user)
    return db_user

# Delete a user
@app.delete("/users/{user_id}", response_model=UserSchema)
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return db_user

@app.get("/sprints/{sprint_id}/performance-metrics/", response_model=SprintPerformanceMetrics)
def get_sprint_performance_metrics(sprint_id: UUID, db: Session = Depends(get_db)):
    metrics = calculate_sprint_metrics(sprint_id, db)
    return metrics

@app.get("/sprints/{sprint_id}/burn-down-chart")
def get_burn_down_chart(sprint_id: UUID, db: Session = Depends(get_db)):
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    tasks = db.query(Task).filter(Task.sprint_id == sprint_id).all()
    chart = generate_burn_down_chart(tasks, sprint.start_date, sprint.end_date)
    return StreamingResponse(chart, media_type="image/png")

@app.get("/sprints/{sprint_id}/optimize")
def optimize_sprint_endpoint(sprint_id: UUID, db: Session = Depends(get_db)):
    # Fetch sprint details
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    # Fetch tasks associated with the sprint
    tasks = db.query(Task).filter(Task.sprint_id == sprint_id).all()
    total_tasks = len(tasks)
    total_estimated_hours = sum(task.estimated_hours for task in tasks if task.estimated_hours)

    upcoming_sprint = {
        "start_date": sprint.start_date,
        "end_date": sprint.end_date,
        "total_tasks": total_tasks,
        "total_estimated_hours": total_estimated_hours
    }

    # Use the optimizer to predict completion rate and get recommendations
    results = optimizer.optimize_sprint(upcoming_sprint)
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)