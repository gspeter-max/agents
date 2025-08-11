from google.adk.agents import LlmAgent
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk import Runner
from google.adk.tools import google_search, FunctionTool, AgentTool
import asyncio
import google


from multiAgentTool import (
    convertAudioToText,
    textToAudio,
    playAudioFile,
    storePersonalUserInformation,
    removePersonalUserInformation,
    getuserPersonalInformation,
    runCommondInTerminal,
    generateImageFromPrompt
)

class multiCodeAgent:
    """
    multiCodeAgent manages multiple specialized LlmAgents for parallel execution.
    It orchestrates agents for:
      - Web research
      - Code generation & execution
      - Audio storytelling (TTS & playback)
      - Image generation from prompts
    """

    def __init__(self, agentType: str = 'parallel'):
        # Register tools as FunctionTools
        self.convertAudioToText = FunctionTool(func=convertAudioToText)
        self.textToAudio = FunctionTool(func=textToAudio)
        self.playAudioFile = FunctionTool(func=playAudioFile)
        self.storePersonalUserInformation = FunctionTool(func=storePersonalUserInformation)
        self.removePersonalUserInformation = FunctionTool(func=removePersonalUserInformation)
        self.getuserPersonalInformation = FunctionTool(func=getuserPersonalInformation)
        self.runCommondInTerminal = FunctionTool(func=runCommondInTerminal)
        self.generateImageFromPrompt = FunctionTool(func=generateImageFromPrompt)

        # Create agents and runner
        self.rootAgent = self.getLlmAgent(agentType=agentType)
        self.agentSession = InMemorySessionService()
        self.runner = Runner(
            app_name='multiAgent',
            agent=self.rootAgent,
            session_service=self.agentSession
        )

    
    def getLlmAgent(self, agentType: str):
        # Web search agent
        webSearchAgent = AgentTool(agent=LlmAgent(
            name='webSearchAgent',
            description=self.description(role='webSearchAgent'),
            model='gemini-2.5-flash',
            generate_content_config=types.GenerateContentConfig(
                temperature=0.2
            ),
            output_key='webSearchAgentChat',
            tools=[google_search],
            planner=google.adk.planners.BuiltInPlanner(
                thinking_config=google.genai.types.ThinkingConfig(
                    includeThoughts=True,
                    thinkingBudget=2000
                )
            )
        ))

        # Code execution agent
        codeExecutionAgent = AgentTool(agent=LlmAgent(
            name='codeExecutionAgent',
            description=self.description(role='code_execution_agent'),
            model='gemini-2.5-flash',
            generate_content_config=types.GenerateContentConfig(
                temperature=0.2
            ),
            code_executor=google.adk.code_executors.BuiltInCodeExecutor(
                stateful=True
            ),
            output_key='codeExecutionAgentChat',
            planner=google.adk.planners.BuiltInPlanner(
                thinking_config=google.genai.types.ThinkingConfig(
                    includeThoughts=True,
                    thinkingBudget=2000
                )
            )
        ))

        # Storytelling & audio agent
        storeTellingAudioAgent = LlmAgent(
            name='storeTellingAudioAgent',
            description=self.description(role='storeTellingAudioAgent'),
            model='gemini-2.5-flash',
            generate_content_config=types.GenerateContentConfig(
                temperature=0.2
            ),
            output_key='chat_history',
            tools=[webSearchAgent, self.textToAudio, self.playAudioFile],
            planner=google.adk.planners.BuiltInPlanner(
                thinking_config=google.genai.types.ThinkingConfig(
                    includeThoughts=True,
                    thinkingBudget=2000
                )
            )
        )

        # Code generation agent
        codeGenerateAgent = LlmAgent(
            name='codeGenerateAgent',
            description=self.description(role='codeGenerateAgent'),
            model='gemini-2.5-flash',
            generate_content_config=types.GenerateContentConfig(
                temperature=0.6
            ),
            tools=[codeExecutionAgent, self.runCommondInTerminal, webSearchAgent],
            planner=google.adk.planners.BuiltInPlanner(
                thinking_config=google.genai.types.ThinkingConfig(
                    includeThoughts=True,
                    thinkingBudget=2000
                )
            ),
            output_key='GoogleSearchToolResult'
        )

        # Image generation agent
        generateImagesAgent = LlmAgent(
            name='generateImagesAgent',
            description=self.description(role='generateImagesAgent'),
            model='gemini-2.5-flash',
            generate_content_config=types.GenerateContentConfig(
                temperature=0.6
            ),
            tools=[self.generateImageFromPrompt, self.runCommondInTerminal, webSearchAgent],
            planner=google.adk.planners.BuiltInPlanner(
                thinking_config=google.genai.types.ThinkingConfig(
                    includeThoughts=True,
                    thinkingBudget=2000
                )
            ),
            output_key='GoogleSearchToolResult'
        )

        # Parallel agent wrapper
        parallelAgent = google.adk.agents.ParallelAgent(
            name='parallelAgent',
            sub_agents=[generateImagesAgent, codeGenerateAgent, storeTellingAudioAgent]
        )

        return parallelAgent

    async def getResponse(self, userQuery: str, return_event: bool = False):
        if await self.agentSession.get_session(
            app_name='multiAgent',
            user_id='user_id',
            session_id='123'
        ) is None:
            await self.agentSession.create_session(
                app_name='multiAgent',
                user_id='user_id',
                session_id='123'
            )

        events = []
        async for event in self.runner.run_async(
            user_id='user_id',
            new_message=types.Content(
                role='user',
                parts=[types.Part.from_text(text=userQuery)]
            ),
            session_id='123'
        ):
            events.append(event)

        if return_event:
            return events
        else:
            for content_parts in events:
                for part in content_parts.content.parts:
                    print(part.text)


# Example usage:
# agents = multiCodeAgent()
# await agents.getResponse('hey  ')