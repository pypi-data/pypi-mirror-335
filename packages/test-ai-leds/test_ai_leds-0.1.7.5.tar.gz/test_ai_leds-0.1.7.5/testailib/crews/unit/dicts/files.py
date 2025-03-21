from pathlib import Path
import difflib
import os
import chardet

def detect_encoding(file_path):
    with open(file_path, "rb") as f:
        result = chardet.detect(f.read())
        return result["encoding"]

def read_file_path(file_path: str) -> str:
    file_path = file_path.strip("'").replace("\\\\", "\\")

    with open(file_path, 'r', encoding='utf-8-sig', errors="ignore") as file:
        cs_file_content = file.read()

    return cs_file_content

def find_file(base_directory: str, file_name: str) -> str:
    """
    Recursivamente procura por um arquivo no diretório fornecido e seus subdiretórios.
    Se não for encontrado uma correspondência exata, retorna a correspondência mais próxima usando correspondência difusa.
    """
    found_files = []
    for root, _, files in os.walk(base_directory):
        if file_name in files:
            return os.path.join(root, file_name).replace("\\", "/")
        
        found_files.extend([os.path.join(root, file).replace("\\", "/") for file in files])

    file_names = [os.path.basename(path) for path in found_files]
    closest_match = difflib.get_close_matches(file_name, file_names, n=1)
    
    if closest_match:
        for path in found_files:
            if os.path.basename(path) == closest_match[0]:
                return path  
    
    return None

def process_test_and_related_files(found_paths: list):
    existing_test_content = ""
    
    # Verifica se o último caminho é um arquivo de teste
    if found_paths and found_paths[-1] and "Test" in found_paths[-1]:
        test_file_path = found_paths.pop()
        encoding = detect_encoding(test_file_path)
        with open(test_file_path, "r", encoding=encoding, errors="ignore") as f:
            existing_test_content = f.read()

    related_files_content = []
    
    # Processa os arquivos relacionados
    for related_file in found_paths:
        if not related_file:
            continue  # Ignora valores None

        # Ignora arquivos binários
        if related_file.endswith(('.dll', '.exe', '.pdb', '.so', '.obj', '.lib')):
            print(f"Ignorando arquivo binário: {related_file}")
            continue

        encoding = detect_encoding(related_file)
        with open(related_file, "r", encoding=encoding, errors="ignore") as f:
            related_files_content.append(f.read())
    
    related_files_content = "\n\n".join(related_files_content)

    return existing_test_content, related_files_content
