from google.adk.agents import LlmAgent
from google.genai import types 
from google.adk.sessions import InMemorySessionService
from google.adk import Runner
from google.adk.tools import google_search
import asyncio 
import google


def description( role ):
    if role.lower() == 'code_execution_agent':
        return '"code_execution_agent" is an autonomous AI coding and execution agent designed to\
                generate, execute, and refine code in a fully stateful environment.\
                Powered by the google-2.5-flash model with low-temperature precision\
                (0.2), it combines structured planning and deep reasoning via a built\
                -in planner with a generous thinking budget. Mark writes clean, \
                efficient code, runs it in an isolated execution environment, \
                and retains state across runs for iterative improvement. \
                The agent outputs detailed results, including its reasoning steps\
                , to maintain transparency and reliability in every \
                coding session.' 
        
    if role.lower() == 'web_search_agent': 
        return '"WebSearch Agent" is an autonomous AI research assistant designed \
                to search, retrieve, and synthesize web-based information with high \
                accuracy and speed. Leveraging structured planning and deep reasoning\
                , it can execute targeted queries, parse complex web data, and \
                generate concise, well-organized summaries. \
                The agent supports multi-step search strategies, evaluates multiple \
                sources for credibility, and retains search context to refine \
                results iteratively. Ideal for real-time fact-finding, \
                competitive intelligence, and complex research workflows, \
                it ensures outputs are both relevant and verifiable.'
    
    if role.lower() == 'omnitaskagent':
        return '"OmniTask Agent" is a composite AI system that orchestrates specialized sub-agents to handle complex,\
                multi-domain tasks end-to-end. It integrates a Code Execution Agent for generating, \
                testing, and refining high-quality software, and a Web Search Agent for retrieving,\
                analyzing, and synthesizing authoritative web-based information. Using structured \
                planning and a shared state, OmniTask Agent can combine live research with executable code \
                generation in a single workflow — for example, finding the latest algorithmic techniques online,\
                implementing them in code, testing results, and presenting polished outputs. This architecture\
                allows the main agent to delegate subtasks to domain experts, merge their outputs,\
                and produce final results that are accurate, actionable, and execution-ready.'
    else:
        raise ValueError(f'{role} not a valid name in (code_execution_agent, web_search_agent , OmniTaskAgent)')


code_agent = LlmAgent(
    name = 'codeExecutionAgent',
    description = description( role = 'code_execution_agent'),
    model = 'gemini-2.5-flash',
    generate_content_config = types.GenerateContentConfig(
            temperature = 0.2
         ),
    code_executor = google.adk.code_executors.BuiltInCodeExecutor(
        stateful = True
        ),
    output_key = 'chat_history',
    planner = google.adk.planners.BuiltInPlanner(
        thinking_config = google.genai.types.ThinkingConfig(
            includeThoughts = True,
            thinkingBudget = 2000
            ) 
        )
)

WebSearchAgent = LlmAgent(
        name = 'webSearchAgent',
        description = description( role = 'web_search_agent' ),
        model = 'gemini-2.5-flash',
        generate_content_config = types.GenerateContentConfig(
            temperature = 0.6
            ),
        tools = [google_search],
        planner = google.adk.planners.BuiltInPlanner(
            thinking_config = google.genai.types.ThinkingConfig(
                includeThoughts = True,
                thinkingBudget = 2000
                )
            ),
        output_key = 'GoogleSearchToolResult'
        )


ParentModel = LlmAgent(
    name = 'OmniTaskAgent',
    description = description(role = 'OmniTaskAgent'),
    model = 'gemini-2.5-flash',
    generate_content_config = types.GenerateContentConfig(
        temperature = 0.2
    ),
    output_key = 'RootAgentChatHistory',
    planner = google.adk.planners.BuiltInPlanner(
        thinking_config = google.genai.types.ThinkingConfig(
            includeThoughts = True,
            thinkingBudget = 2000
        )
    ),
    sub_agents = [code_agent, WebSearchAgent]
)

async def SessionRunner( llm_agent ):
    agent_session = InMemorySessionService()
    session = await agent_session.create_session(
        app_name = 'multiAgent',
        user_id = 'user_id',
        session_id = '123'
    )
    runner = Runner( app_name = 'multiAgent', agent = llm_agent, \
            session_service = agent_session )
    
    return runner,session


async def getResponse( llm_agent, userQuery : str ):
    runner,session = await SessionRunner( llm_agent )
    response = runner.run(
        user_id ='user_id',
        new_message = types.Content(role = 'user',\
                parts = [types.Part.from_text(text = userQuery)]),
        session_id = '123'
    )
    print(next(response))
    # return next(response)

response = await getResponse(
        llm_agent = ParentModel,
        userQuery = 'what is the capital of india ?'
    )