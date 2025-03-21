from crewai import LLM
import os
import json
import re

def get_andes_events(file_path: str):
    
    def load_input_from_file(file_path):
        """Função para carregar o conteúdo do arquivo."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as error:
            raise RuntimeError(f"Erro ao ler o arquivo: {error}")

    def extract_events(input_text):
        """Função para extrair todos os eventos."""
        usecase_pattern = re.compile(
            r"usecase\s+(\w+)\s*{\s*name:\s*\"([^\"]+)\"\s*.*?description:\s*\"([^\"]+)\"\s*.*?performer:\s*(\w+)\s*.*?(event.*?})\s*}",
            re.DOTALL
        )
        event_pattern = re.compile(
            r"event\s+(\w+)\s*{\s*name:\s*\"([^\"]+)\"\s*.*?description:\s*\"([^\"]+)\"\s*.*?action:\s*\"([^\"]+)\"\s*}",
            re.DOTALL
        )

        events = []

        for usecase_match in usecase_pattern.finditer(input_text):
            events_block = usecase_match.group(5)

            for event_match in event_pattern.finditer(events_block):
                event_id = event_match.group(1)
                event_name = event_match.group(2)
                event_description = event_match.group(3)
                event_action = event_match.group(4).strip()

                events.append({
                    "event_id": event_id,
                    "name": event_name,
                    "description": event_description,
                    "action": event_action
                })

        return events
    
    input_text = load_input_from_file(file_path)
    events = extract_events(input_text)
    return events


def extract_endpoints(swagger_path: str) -> list[str]:
    with open(swagger_path, encoding="utf-8") as f:
        swagger_data = json.load(f)

    # Obtenha os endpoints
    endpoints = ""
    for path, methods in swagger_data.get('paths', {}).items():
        for method in methods.keys():
            endpoints += f"{method.upper()} {path}\n"

    return endpoints

def concat_output_example(task, output_examples) -> None:
    output_example = output_examples[task["output_example"]]
    concat_description = task["description"] + output_example
    task["description"] = concat_description

def format_task(task: dict, input: dict | list | tuple) -> None:
    if isinstance(input, dict):
        task["description"] = task["description"].format(**input)
    elif isinstance(input, (list, tuple)):
        task["description"] = task["description"].format(*input)

def init_llm(temperature: float = 0.0, config: dict = None) -> LLM:
    return LLM(
        model=os.getenv("LLM_MODEL"),
        api_key=os.getenv("API_KEY"),
        temperature=temperature
    )