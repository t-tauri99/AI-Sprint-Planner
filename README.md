# AI-Sprint-Planner

## Overview
This project provides an **AI-Powered Sprint Planning and Optimization API** using FastAPI. It automates task allocation, tracks sprint progress, and uses machine learning to predict sprint outcomes and provide recommendations.

## Features
- **Task Allocation**: Assign tasks based on skills and availability.
- **Sprint Progress**: Track completion rate and sprint progress.
- **Burn-Down Chart**: Visualize remaining work.
- **Predictive Modeling**: Use RandomForest to predict sprint success.

## File Functionalities

### `app/main.py`
- FastAPI routes handling task allocation, sprint optimization, and metrics.

### `app/models_sprint.py`
- Database schema for tasks, sprints, and users.

### `app/schemas.py`
- Pydantic models for request validation.

### `app/services.py`
- Core logic for task allocation, sprint metrics, and burn-down chart generation.

### `app/RandomForest.py`
- Loads the trained RandomForest model and handles predictions.

### `app/model.pkl`
- Pre-trained RandomForest model for sprint prediction.

### `data/sprint_data_sample.csv`
- Sample data for model training and testing.

### `agents/Multi_Agent_sprint_planner.py`
- Automates sprint and task management using agents.