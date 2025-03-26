from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from typing import Optional
from pydantic import BaseModel

class ReportVerification(BaseModel):
    valid: bool
    feedback: Optional[str]

@CrewBase
class AnomalyReview():
    """AnomalyReview crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def anomaly_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['anomaly_reviewer'],
            verbose=True
        )



    @task
    def review_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_task'],
            output_pydantic=ReportVerification,
        )


    @crew
    def crew(self) -> Crew:
        """Creates the AnomalyReview crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
