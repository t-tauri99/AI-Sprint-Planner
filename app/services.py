from sqlalchemy.orm import Session
from datetime import timedelta, datetime, date
from models_sprint import Sprint, Task
from uuid import UUID
from fastapi import HTTPException
from schemas import SprintPerformanceMetrics
import matplotlib.pyplot as plt
import io
from fastapi.responses import StreamingResponse


def allocate_task(task, team_members):
    for member in team_members:
        if all(skill in member.skills for skill in task.required_skills) and member.available_hours >= task.estimated_hours:
            # Allocate task to member
            member.available_hours -= task.estimated_hours
            return member.id, "Task allocated successfully"
    
    return None, "No suitable member found"

def calculate_sprint_metrics(sprint_id: UUID, db: Session):
    # Fetch the sprint and its related tasks
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    tasks = db.query(Task).filter(Task.user_story.has(sprint_id=sprint_id)).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found for this sprint")

    # Calculate metrics
    total_estimated_hours = sum(task.estimated_hours for task in tasks)
    completed_tasks = [task for task in tasks if task.completed]
    completed_task_count = len(completed_tasks)

    # Completed Estimated Hours
    completed_estimated_hours = sum(task.estimated_hours for task in completed_tasks)

    # Completion Rate
    completion_rate = (completed_estimated_hours / total_estimated_hours) * 100 if total_estimated_hours > 0 else 0

    total_days = (sprint.end_date - sprint.start_date).days
    days_passed = (date.today() - sprint.start_date).days
    sprint_progress = min((days_passed / total_days) * 100 if total_days > 0 else 0, 100)

    return SprintPerformanceMetrics(
        sprint_id=sprint_id,
        total_tasks=len(tasks),
        completed_tasks=completed_task_count,
        total_estimated_hours=total_estimated_hours,
        completed_estimated_hours=completed_estimated_hours,
        completion_rate=completion_rate,
        sprint_progress=sprint_progress
    )

def generate_burn_down_chart(tasks, sprint_start, sprint_end):

    # Generate date range for the sprint
    dates = [sprint_start + timedelta(days=x) for x in range((sprint_end - sprint_start).days + 1)]

    # Calculate total hours
    total_hours = sum(task.estimated_hours for task in tasks)

    # Calculate ideal burn-down
    ideal_burn_down = [total_hours - (total_hours / len(dates)) * i for i in range(len(dates))]

    # Calculate actual burn-down
    actual_burn_down = [total_hours] * len(dates)
    completed_hours = sum(task.estimated_hours for task in tasks if task.completed)
    actual_burn_down[-1] = total_hours - completed_hours 

    # Create the chart
    plt.figure(figsize=(12, 6))
    plt.plot(dates, ideal_burn_down, label='Ideal Burn-Down', linestyle='--', color='blue')
    plt.plot(dates, actual_burn_down, label='Actual Burn-Down', marker='o', linestyle='-', color='red')

    plt.title('Sprint Burn-Down Chart')
    plt.xlabel('Date')
    plt.ylabel('Hours Remaining')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the chart to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf