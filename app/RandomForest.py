import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib

model = joblib.load('sprint_model.pkl')

class SprintOptimizer:
    def __init__(self):
        self.model = model

    def prepare_data(self, sprints_data):
        df = pd.DataFrame(sprints_data)
        df['start_date'] = pd.to_datetime(df['start_date'], format='%Y-%m-%d')
        df['end_date'] = pd.to_datetime(df['end_date'], format='%Y-%m-%d')
        df['sprint_duration'] = (df['end_date'] - df['start_date']).dt.days
        df['tasks_per_day'] = df['total_tasks'] / df['sprint_duration']
        df['avg_task_size'] = df['total_estimated_hours'] / df['total_tasks']
        
        return df

    def optimize_sprint(self, upcoming_sprint):
        if self.model is None:
            raise ValueError("Model not trained. Call train_model first.")
        
        sprint_df = self.prepare_data([upcoming_sprint])
        X = sprint_df[['sprint_duration', 'tasks_per_day', 'avg_task_size', 'total_tasks']]
        
        predicted_completion_rate = self.model.predict(X)[0]
        
        recommendations = []
        if predicted_completion_rate < 0.8:
            if sprint_df['tasks_per_day'].values[0] > 1.5:
                recommendations.append("Consider reducing the number of tasks in this sprint.")
            if sprint_df['avg_task_size'].values[0] > 8:
                recommendations.append("The average task size seems large. Consider breaking down tasks into smaller units.")
        
        return {
            "predicted_completion_rate": predicted_completion_rate,
            "recommendations": recommendations
        }