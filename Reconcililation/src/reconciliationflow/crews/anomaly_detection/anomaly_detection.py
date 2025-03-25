from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class AnomalyDetection:
    """AnomalyDetection crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'


    @agent
    def anomaly_detector(self) -> Agent:
        return Agent(
            config=self.agents_config['anomaly_detector'],
            verbose=True
        )


    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the AnomalyDetection crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            memory=True
        )
