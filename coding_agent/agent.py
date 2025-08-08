from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain.chat_models import init_chat_model
from langchain.tools import Tool
from googlesearch import search
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationSummaryBufferMemory
from GenerateTestCodeTool import generate_coe, test_code
from bs4 import BeautifulSoup
import requests
import time


def get_web_data(query):

    document_list = []
    for index, url in enumerate(search( query , num_results = 10)):
        if (index == 0) and (str(url)[:8] != 'https://'):
            continue

        text = ''
        response = requests.get(url)
        if response.status_code == 403:
            continue

        soup = BeautifulSoup( response.text, 'html.parser')
        for value in soup.select('p'):
            text += value.getText(strip = True)

        document = Document(
                page_content = text,
                metadata = {'source' : url}
            )
        document_list.append(document)
        if response.status_code == 200:
            break
        time.sleep(2)

    recursive_splitters = RecursiveCharacterTextSplitter( chunk_size = 1000, chunk_overlap = 20)
    docs = recursive_splitters.split_documents(document_list)

    embedding = GoogleGenerativeAIEmbeddings( model = 'gemini-embedding-001', \
            google_api_key = 'AIzaSyDKUGAMTjpKpNxmVGU7Wi3pMM1QTumsYNI'
            )

    chroma_bd = Chroma(embedding_function = embedding ) 
    chroma_bd.add_documents(docs)
    return chroma_bd.similarity_search(query)

def SetupToolAndModules( self ):

    tools = [
        Tool(
            name = 'get_data_from_web',
            func = get_web_data,
            description = 'usefull when you not know something , and need to search on the web  \
                    and  get vectorized data using user `query` '
        ),
        Tool(
            name = 'generate_code_with_instruction',
            func = generate_code,
            description = 'Useful when you need to generate executable code based on a natural language query. \
                    This tool allows dynamic code generation by passing a system-level instruction to the LLM \
                    using add_str_in_system_instruction. Ideal for scenarios where precise code generation logic \
                    or constraints must be enforced during runtime. Ensure to test the generated code to verify \
                    its correctness and functionality.'
        ),
        Tool(
            name = 'test_codetest_code_execution',
            func = test_code,
            description = 'Useful when you need to test whether a given code snippet runs successfully or not. \
                    This tool executes the provided code and returns the result or any runtime errors, \
                    making it ideal for validating dynamically generated code or debugging logic. \
                    It helps ensure the code is functional, safe to run, and produces the expected \
                    output before further use.'
        ),Tool(
            name="install_modules",
            func=install_modules,
            description=(
                "Use this tool to install one or more Python packages dynamically during runtime. "
                "Provide a list of package names (as strings). "
                "For each package, the tool will run a pip install command silently. "
                "If installation is successful, it logs a success message. "
                "If installation fails, it returns the error output from pip. "
                "Returns a complete report for all packages in a single string."
        ))
    ]


    llm = init_chat_model( model = 'gemini-2.5-flash', model_provider = 'google_genai', \
        google_api_key = 'AIzaSyDKUGAMTjpKpNxmVGU7Wi3pMM1QTumsYNI')

    template = '''You are an intelligent and highly capable AI agent. Your task is to answer user queries \
        using available tools as needed. Follow strict step-by-step reasoning and only respond with the \
        correct final answer once you're confident.

        You have access to the following tools:{tools}
        You are an AI coding agent with access to the `test_code_execution` tool. Your goal is to produce \
        Python code that **runs successfully** when executed. Follow this format:

        - **Input format**: Always output only the code, nothing else. Use exactly:
        ```python
        <code here>
        ```

        Use the following format exactly:

        Question: the input question you must answer
        Thought: you should always think about what to do next
        Action: the action to take, must be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question
        python_code: 
        ```python
        < code > 
        ```  instand of this in test_code_execution pass out as a input only ```python <code> ``` ### extremly important thing

        Begin!

        Question: {input}
        Chat History: {chat_history}
        {agent_scratchpad}
        '''

    prompt_template = PromptTemplate.from_template(template)

    agent = create_react_agent(
        llm = llm,
        prompt = prompt_template,
        tools = tools
    )
    self.memory= ConversationSummaryBufferMemory(
        llm = llm,
        max_token_limit = 1000,
        input_key = 'input',
        memory_key = 'chat_history'
    )

    self.agent_executor = AgentExecutor( agent = agent , tools = tools, handle_parsing_errors=True)

def generate_content(self , query):
    response = self.agent_executor.invoke(
        {
            'input' : query,
            'chat_history' : self.memory.chat_memory
        })

    self.memory.chat_memory.add_user_message(query)
    self.memory.chat_memory.add_ai_message(response['output'])
    return response