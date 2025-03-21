from crewai import Agent, Task, Crew, Process
from .dicts import agents, tasks
from .dicts.output_examples import examples
from testailib.utils import format_task, concat_output_example, init_llm

llm_low_temp = init_llm()
llm_high_temp = init_llm(temperature=0.3)

def create_cypress_crew(vue_code: str) -> Crew:
    for task in (tasks.cypress_write, tasks.cypress_review):
        format_task(task, {"vue_code": vue_code})
        concat_output_example(task, examples)

    cypress_writer= Agent(**agents.cypress_writer, llm=llm_high_temp)
    cypress_write: Task = Task(**tasks.cypress_write, agent=cypress_writer)

    cypress_reviewer: Agent = Agent(**agents.cypress_reviewer, llm=llm_low_temp)
    cypress_review: Task = Task(**tasks.cypress_review, agent=cypress_reviewer, context=[cypress_write])
    
    return Crew(
        agents=[cypress_writer, cypress_reviewer],
        tasks=[cypress_write, cypress_review],
        process=Process.sequential,
        verbose=False
    )

def create_manager_crew(results: list[str]) -> str:
    format_task(tasks.final_task, results)

    manager: Agent = Agent(**agents.manager, llm=llm_low_temp)
    final_task: Task = Task(**tasks.final_task, agent=manager)

    return Crew(
        agents=[manager],
        tasks=[final_task],
        process=Process.sequential
    )
