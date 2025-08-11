from google.adk.agents import LlmAgent
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk import Runner
from google.adk.tools import google_search, FunctionTool
from multiAgentTool import toolBox 
import asyncio
import google

class multiCodeAgent:
    def __init__( self, agentType: str = 'parallel'):
        self.toolKit = [
            google_search,
            FunctionTool(func = toolBox.convertAudioToText),
            FunctionTool(func = toolBox.textToAudio),
            FunctionTool(func = toolBox.playAudioFile),
            FunctionTool(func = toolBox.storePersonalUserInformation),
            FunctionTool(func = toolBox.removePersonalUserInformation),
            FunctionTool(func = toolBox.getuserPersonalInformation),
            FunctionTool(func = toolBox.runCommondInTerminal),
            FunctionTool(func = toolBox.generateImageFromPrompt)
        ]
        
        self.rootAgent = self.getLlmAgent(agentType = agentType)
        self.agentSession = InMemorySessionService()
        self.runner = Runner( app_name = 'multiAgent', agent = self.rootAgent, \
                session_service = self.agentSession )
        


    def description( self, role ):
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

        else:
            raise ValueError(f'{role} not a valid name in (code_execution_agent, web_search_agent , OmniTaskAgent)')

    def getLlmAgent( self, agentType: str ):

        code_agent = LlmAgent(
            name = 'codeExecutionAgent',
            description = self.description( role = 'code_execution_agent'),
            model = 'gemini-2.5-flash',
            generate_content_config = types.GenerateContentConfig(
                    temperature = 0.2
                ),
            code_executor = google.adk.code_executors.BuiltInCodeExecutor(
                stateful = True
                ),
            output_key = 'chat_history',
            tools = self.toolKit
            planner = google.adk.planners.BuiltInPlanner(
                thinking_config = google.genai.types.ThinkingConfig(
                    includeThoughts = True,
                    thinkingBudget = 2000
                    )
                )
        )

        WebSearchAgent = LlmAgent(
                name = 'webSearchAgent',
                description = self.description( role = 'web_search_agent' ),
                model = 'gemini-2.5-flash',
                generate_content_config = types.GenerateContentConfig(
                    temperature = 0.6
                    ),
                tools = self.toolKit,
                planner = google.adk.planners.BuiltInPlanner(
                    thinking_config = google.genai.types.ThinkingConfig(
                        includeThoughts = True,
                        thinkingBudget = 2000
                        )
                    ),
                output_key = 'GoogleSearchToolResult'
                )

        if agentType.lower() == 'parallel':
            parallelAgent = google.adk.agents.ParallelAgent(
                name = 'parallelAgent',
                sub_agents = [WebSearchAgent,code_agent]
            )

            return parallelAgent
        
        if agentType.lower() == 'sequential':
            sequentialAgent =  google.adk.agents.ParallelAgent(
                name = 'sequenctialAgent',
                sub_agents = [WebSearchAgent,code_agent]
            )
            
            return sequentialAgent
        
        raise ValueError(f'{agentType} is not found in (sequential, parallel)')

    async def getResponse( self, userQuery : str,return_event : bool = False ):
        if await self.agentSession.get_session(  app_name = 'multiAgent',user_id = 'user_id',session_id = '123') is None:
            session = await self.agentSession.create_session(
                app_name = 'multiAgent',
                user_id = 'user_id',
                session_id = '123'
            )
        
        events = [] 
        async for event in self.runner.run_async( user_id ='user_id', new_message = types.Content(role = 'user',\
                    parts = [types.Part.from_text(text = userQuery)]), session_id = '123' ):
            events.append(event)

        if return_event is True:
            return events
        
        else:
            for content_parts in events:
                for part in content_parts.content.parts:
                    print(part.text)


agents= multiCodeAgent()
