from crewai import Agent, Task, Crew, Process
from .dicts import agents
from .dicts import tasks
from .dicts import files
import ast
import os
from pathlib import Path
from testailib.utils import init_llm

llm_low_temp = init_llm(temperature=0.2)

def create_unitAnalyzer_crew(absolute_path: str) -> Crew:
    
    dependency_finder_agent = Agent(**agents.dict_dependency_finder_agent, llm=llm_low_temp)
    analyze_code_task = Task(**tasks.create_analyze_code_task(files.read_file_path(absolute_path)), agent=dependency_finder_agent)

    crew_dependency = Crew(
        agents=[dependency_finder_agent],
        tasks=[analyze_code_task],
        verbose=False,
    )

    return crew_dependency

def generate_unitTest_crew(dependency_results:str, absolute_path: str) -> Crew:
    dependency_results = list(ast.literal_eval(dependency_results))

    existing_test = f"{Path(absolute_path).stem}Test.cs"
    dependency_results.append(existing_test)

    path = Path(absolute_path)
    parts = path.parts

    if "src" not in parts:
        print("Erro: O diretório 'src' não foi encontrado no caminho fornecido.")
    else:
        src_index = parts.index("src")
        # Reconstrói o caminho até "src"
        base_directory = Path(*parts[:src_index + 1])


    content_files = []
    for dependency in dependency_results:
        found_paths = files.find_file(base_directory, dependency)
        content_files.append(found_paths)

    existing_test_content, related_files_content = files.process_test_and_related_files(content_files)
    

    test_generator_agent = Agent(**agents.dict_test_generator_agent, llm = llm_low_temp)
    generate_test_task = Task(**tasks.create_generate_test_task(files.read_file_path(absolute_path), related_files_content, existing_test_content),  agent=test_generator_agent)

    crew_test_generation = Crew(
        agents=[test_generator_agent],
        tasks=[generate_test_task],
        verbose=False,
    )
    return crew_test_generation
    