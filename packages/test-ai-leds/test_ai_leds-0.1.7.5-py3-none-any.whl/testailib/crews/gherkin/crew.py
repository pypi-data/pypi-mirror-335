from crewai import Agent, Task, Crew, Process
from .dicts import agents
from .dicts import tasks
from testailib.utils import format_task, init_llm

llm_low_temp = init_llm(temperature=0.2)
llm_high_temp = init_llm(temperature=0.6)

def create_gherkin_crew(user_case: str) -> Crew:
    for task in (tasks.gherkin_code, tasks.gherkin_review):
        format_task(task, {"user_case": user_case})

    gherkin_writer = Agent(**agents.gherkin_writer, llm=llm_high_temp)
    gherkin_write = Task(**tasks.gherkin_code, agent=gherkin_writer)

    gherkin_reviewer = Agent(**agents.gherkin_reviewer, llm=llm_low_temp)
    gherkin_review = Task(**tasks.gherkin_review, agent=gherkin_reviewer, context=[gherkin_write])

    return Crew(
        agents=[gherkin_writer, gherkin_reviewer],
        tasks=[gherkin_write, gherkin_review],
        max_rpm=10,
        process=Process.sequential,
        verbose=False
    )
    
def create_manager_crew(reviews: list[str]) -> Crew:
    format_task(tasks.manager_gherkin_task, reviews)
    manager: Agent = Agent(**agents.manager_gherkin, llm=llm_low_temp)
    final_task: Task = Task(**tasks.manager_gherkin_task, agent=manager)

    return Crew(
        agents=[manager],
        tasks=[final_task],
        max_rpm=2,
        process=Process.sequential,
        verbose=False
    )
