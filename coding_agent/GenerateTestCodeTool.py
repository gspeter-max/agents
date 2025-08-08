from google import genai
from pprint import pprint
from google.genai import types
client  = genai.Client( api_key = 'AIzaSyDKUGAMTjpKpNxmVGU7Wi3pMM1QTumsYNI')
import subprocess
from langchain.tools import Tool
import os

def generate_code( query_for_generation : str ,add_str_in_system_instruction : str = ''):
    print(f'==================================generate_code==========================================')
    llm_ins  = 'write code in this format --> ```python  <generated_code> ``` make sense <generated_code> mean generated_code  ' + add_str_in_system_instruction
    tool = types.Tool(code_execution = types.ToolCodeExecution())
    config = types.GenerateContentConfig(
            system_instruction= llm_ins,
            tools = [tool]
            )

    response = client.models.generate_content(
        model = 'gemini-2.5-flash',
        contents = query_for_generation,
        config = config
        )

    error_texts = ''
    for response_part in response.candidates[0].content.parts:
        if response_part.text is not None:
            if "```python" in response_part.text:
                return response_part.text[10:3]  + '#### important make sure you test this code for executing this'

            else :
                error_texts += response_part.text

    return f'llm : {error_texts}'

def test_code(python_code: str):
    print('============================================test_code============================================')
    pwd = os.getcwd()
    if python_code[:9] == '```python':
        python_code = python_code[9:]
    if python_code[-3:] == '```':
        python_code = python_code[:-3]

    with open(f'{pwd}/python_execution.py','w') as f:
        f.write(python_code)

    subprocess_output = subprocess.run(['python','python_execution.py'],capture_output = True, text = True)
    output = subprocess_output.stdout  if subprocess_output.returncode == 0 else subprocess_output.stderr
    print(f'======================================output===========================================')
    print(output)
    return output


def install_modules( list_of_modules : List[str] ):
    print(f'======================== install modules {list_of_modules} =========================')
    text = ''
    for module in list_of_modules:
        result = subprocess.run(f'pip install {module}', text = True, capture_output = True, shell = True )
        print(result)
        text += f'{module} successfully installed' if result.returncode == 0 else result.stderr
        text += '\n'

    return text




