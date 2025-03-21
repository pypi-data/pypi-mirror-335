from testailib.utils import init_llm, extract_endpoints, format_task, concat_output_example
from .dicts import agents
from .dicts import tasks
from .dicts.output_examples import examples
from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool, DirectoryReadTool
from crewai.tools import tool
from typing import Dict, List

llm = init_llm()

@tool("Endpoint Extractor tool")
def extract_endpoints(swagger_path: str) -> str:
    """
    This tool extract the endpoints and it's methods from swagger documents
    the schema for this tool is:
    swagger_path: str -> the path for the swagger file
    """
    import json
    with open(swagger_path, encoding="utf-8") as f:
        swagger_data = json.load(f)

    # Obtenha os endpoints
    endpoints = ""
    for path, methods in swagger_data.get('paths', {}).items():
        for method in methods.keys():
            endpoints += f"{method.upper()} {path}\n"

    return endpoints

def info_gather(feature: str, swagger_path: str, dto_source: str) -> tuple[str, str]:

    format_task(tasks.api_url_find, dict(feature=feature, swagger_path=swagger_path))
    format_task(tasks.dto_file_find, dict(feature=feature, dto_source=dto_source))

    agent_api_finder = Agent(**agents.agent_api_finder, llm=llm, tools=[extract_endpoints])
    api_url_find = Task(**tasks.api_url_find, agent=agent_api_finder)

    agent_file_searcher = Agent(**agents.agent_file_searcher, llm=llm, tools=[DirectoryReadTool(), FileReadTool()])
    dto_file_find = Task(**tasks.dto_file_find, agent=agent_file_searcher)

    crew = Crew(
        agents=[agent_api_finder, agent_file_searcher],
        tasks=[dto_file_find, api_url_find],
        verbose=False,
        process=Process.sequential
    )

    crew.kickoff()

    return dto_file_find.output.raw, api_url_find.output.raw

def create_crew_xunit(feature: str, swagger_path: str, dto_source: str) -> Crew:
    dto_class, api_url = info_gather(feature, swagger_path, dto_source)
    
    llm = init_llm(temperature=0.2)
    
    format_task(tasks.xunit_write, {"feature": feature, "api_url": api_url, "dto_class": dto_class})
    format_task(tasks.xunit_review, {"feature": feature})

    concat_output_example(tasks.xunit_write, examples)
    concat_output_example(tasks.xunit_review, examples)


    xunit_writer = Agent(**agents.xunit_writer, llm=llm)
    xunit_write = Task(**tasks.xunit_write, agent=xunit_writer)

    xunit_reviewer = Agent(**agents.xunit_reviewer, llm=llm)
    xunit_review = Task(**tasks.xunit_review, agent=xunit_reviewer, context=[xunit_write])
    
    return Crew(
        agents=[xunit_writer, xunit_reviewer],
        tasks=[xunit_write, xunit_review],
        process=Process.sequential,
        verbose=False
        )

def create_manager_crew(reviews: tuple[str]) -> Crew:
    format_task(tasks.manager_xunit_task, reviews)
    concat_output_example(tasks.manager_xunit_task, examples)

    manager: Agent = Agent(**agents.result_analysis_manager, llm=llm)
    manager_task = Task(**tasks.manager_xunit_task, agent=manager)

    return Crew(
        agents=[manager],
        tasks=[manager_task],
        process=Process.sequential,
        verbose=False
    )