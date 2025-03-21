from concurrent.futures import ThreadPoolExecutor
from .crews.gherkin.crew import create_gherkin_crew as gherkin_constructor, create_manager_crew as gherkin_manager_constructor
from .crews.xunit.crew import create_crew_xunit as xunit_constructor, create_manager_crew as xunit_manager_constructor
from .crews.cypress.crew import create_cypress_crew as cypress_constructor, create_manager_crew as cypress_manager_constructor
from .crews.unit.crew import create_unitAnalyzer_crew, generate_unitTest_crew
from .utils import get_andes_events
from pathlib import Path
import os


def write_file(path: str, data: str) -> None:
    Path(fr"{path}").write_text(data, encoding="utf-8")

def run_crew_parallel(crew_constructor, manager_crew_constructor, **kwargs) -> str:
    crew = crew_constructor(**kwargs)
    with ThreadPoolExecutor(max_workers=3) as executor:
        runs = [executor.submit(crew.kickoff) for _ in range(3)]
        results = [run.result() for run in runs]
    manager_crew = manager_crew_constructor(results)
    output = manager_crew.kickoff()
    return output.raw

def handle_gherkin(user_case: str, output_path: str) -> None:
    crew_constructor = gherkin_constructor
    manager_crew_constructor = gherkin_manager_constructor

    kwargs = dict(
        user_case=user_case
    )

    result = run_crew_parallel(crew_constructor, manager_crew_constructor, **kwargs)
    write_file(output_path, result)

def handle_xunit(feature_path: str, output_path: str) -> None:
    #sanitizePath = feature_path.strip('\"')
    feature = Path(feature_path).read_text(encoding="utf-8")
    swagger_path = os.getenv("SWAGGER_PATH")
    dto_source = os.getenv("DTO_SOURCE")

    kwargs = dict(
        feature=feature,
        swagger_path=swagger_path,
        dto_source=dto_source
    )

    result = run_crew_parallel(xunit_constructor, xunit_manager_constructor, **kwargs)
    write_file(output_path, result)

def handle_cypress(vue_path: str, output_path: str) -> None:
    with open(vue_path, encoding="utf-8") as file:
        vue_code = file.read()
    
    kwargs = dict(
        vue_code=vue_code
    )

    result = run_crew_parallel(cypress_constructor, cypress_manager_constructor, **kwargs)
    write_file(output_path, result)

def handle_unit(absolute_path: str, output_path: str):
    Analyzer_crew = create_unitAnalyzer_crew(absolute_path)
    Analyzer_Result = Analyzer_crew.kickoff()


    TestGenerator_crew = generate_unitTest_crew(Analyzer_Result.raw, absolute_path)
    TestGenerator_Result = TestGenerator_crew.kickoff()
    result = TestGenerator_Result.raw

    write_file(output_path, result)

