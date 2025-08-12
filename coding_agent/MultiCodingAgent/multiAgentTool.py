from IPython.display import Audio
import speech_recognition
from PIL import Image
from io import BytesIO
import pydub
import typing
import logging
import wave
import google.genai
import google
import subprocess

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def convertAudioToText(filePath: str) -> str:
    """Converts the speech in an audio file into text.

    This tool takes the file path of an audio recording and transcribes the spoken words into a string of text. It is useful for understanding the content of audio files provided by the user or other tools.

    :param filePath: The absolute or relative path to the audio file.
                     The file format must be either '.wav' or '.mp3'.
    :type filePath: str
    
    :return: The transcribed text as a single string. If the speech is unclear or the file is silent,
             it may log an error internally and return an empty or non-descriptive result.
    :rtype: str

    ---
    **When to use this tool:**
    - Use this tool when you are given a path to an audio file and you need to understand its contents.
    - Example Task: A user uploads 'meeting_notes.mp3' and asks, "Can you summarize this for me?"
                     Your first step would be to call this tool with 'meeting_notes.mp3' to get the text.

    **Usage Example:**
    - Call: convertAudioToText(filePath='./speech.wav')
    - Expected Return: "hello world this is a test"
    """
    
    fileFormat = filePath[-3:]
    if fileFormat == 'mp3':
        rawWavFile = pydub.AudioSegment.from_mp3(filePath)
        rawWavFile.export('./speech.wav', format='wav')
        instance = speech_recognition.Recognizer()
        with speech_recognition.AudioFile('./speech.wav') as source:
            sourceData = instance.record(source)
        try:
            return instance.recognize_google(audio_data=sourceData)
        except speech_recognition.UnknownValueError:
            logger.info('Speech is not clear and not convertible to text')

    elif fileFormat == 'wav':
        instance = speech_recognition.Recognizer()
        with speech_recognition.AudioFile(filePath) as source:
            sourceData = instance.record(source)
        try:
            return instance.recognize_google(audio_data=sourceData)
        except speech_recognition.UnknownValueError:
            logger.info('Speech is not clear and not convertible to text')

    else:
        raise ValueError(f'{fileFormat} is not supported. Available formats: wav, mp3')

def textToAudio(text: str, numVoice: int) -> str:
    """Converts a string of text into a spoken audio file.

    This tool generates a speech audio file from the provided text. The generated audio is ALWAYS saved
    to the same location: './textToAudioFile.wav'. You can choose between two voice configurations.

    :param text: The text you want to convert into speech.
    :type text: str
    
    :param numVoice: An integer to select the voice style.
                     - Set `numVoice = 1` for a standard, single male voice (named 'Enceladus').
                     - Set `numVoice = 2` for a multi-speaker conversation between a male ('peter')
                       and a female ('linda') voice. To use this, format the 'text' parameter
                       with speaker tags, e.g., "<speaker:peter> Hello Linda! </speaker><speaker:linda> Hi Peter! </speaker>".
                     Using any number other than 1 or 2 will result in an error.
    :type numVoice: int

    :return: A confirmation message as a string, stating that the audio has been successfully saved
             to the fixed path './textToAudioFile.wav'. It does NOT return the audio data itself.
    :rtype: str

    ---
    **CRUCIAL AGENT INSTRUCTIONS:**
    1.  **Fixed Output Path:** The output file is ALWAYS saved at './textToAudioFile.wav'. It will be
        overwritten each time this tool is called.
    2.  **Playback is a Separate Step:** This tool ONLY creates the file. To play the audio for the user,
        you must use a different tool (like `playAudio`) with the path './textToAudioFile.wav'.
    3.  **Voice Selection:** If the user does not specify a voice, default to `numVoice = 1`. If they ask
        for a conversation or multiple speakers, use `numVoice = 2` and format the text with speaker tags.

    **Usage Example (for storytelling):**
    - Call: textToAudio(text="The brave knight entered the dark cave, wondering what awaited him.", numVoice=1)
    - Return: 'The text-to-audio output has been saved at "./textToAudioFile.wav". ...'
    - Next Step: Call `playAudio(filePath='./textToAudioFile.wav')`.
    """
    
    client = google.genai.Client(api_key='AIzaSyDH5WfjRliWtcO8z4b7yZ7io6inv_PQZ1E')
    
    if numVoice == 1:
        generateContentConfig = google.genai.types.GenerateContentConfig(
            speechConfig=google.genai.types.SpeechConfig(
                voiceConfig=google.genai.types.VoiceConfig(
                    prebuiltVoiceConfig=google.genai.types.PrebuiltVoiceConfig(
                        voiceName='Enceladus'
                    )
                )
            ),
            responseModalities=['AUDIO']
        )
    
    if numVoice == 2:
        generateContentConfig = google.genai.types.GenerateContentConfig(
            responseModalities = ['AUDIO'],
            speechConfig = google.genai.types.SpeechConfig(
                multiSpeakerVoiceConfig = google.genai.types.MultiSpeakerVoiceConfig(
                    speakerVoiceConfigs = [
                        google.genai.types.SpeakerVoiceConfig(
                            speaker = 'peter',
                            voiceConfig = google.genai.types.VoiceConfig(
                                prebuiltVoiceConfig = google.genai.types.PrebuiltVoiceConfig(
                                    voiceName = 'Schedar'
                                    )
                                )
                            ),
                        google.genai.types.SpeakerVoiceConfig(
                            speaker = 'linda',
                            voiceConfig = google.genai.types.VoiceConfig(
                                prebuiltVoiceConfig = google.genai.types.PrebuiltVoiceConfig(
                                    voiceName = 'leda'
                                    )
                                )
                            )
                        ]
                    )
                )
            )
    
    if numVoice > 2:
        return 'numVoice Grather then 2 is not supported with google.genai '

    response = client.models.generate_content(
        model='gemini-2.5-flash-preview-tts',
        contents=text,
        config=generateContentConfig
    )

    audio = response.candidates[0].content.parts[0].inline_data.data
    with wave.open('./textToAudioFile.wav', 'wb') as wf:
        wf.setnchannels(1)
        wf.setframerate(24000)
        wf.setsampwidth(2)
        wf.writeframes(audio)

    return (
        'The text-to-audio output has been saved at "./textToAudioFile.wav". '
        'If you wish to listen to it, use the `playAudio` tool with this file path.'
    )

def runCommondInTerminal(Commond: str) -> str:
    """Executes one or more commands in the system's command-line terminal.

    This is a very powerful tool that allows you to interact directly with the operating system.
    You can manage files, install software packages, and run system utilities.
    It returns the output of the command, which can be used for confirmation, debugging, or further steps.

    :param Commond: a single commands to be executed in sequence.
    :type Commond: str 
    
    :return: The standard output (stdout) or standard error (stderr) generated by the command(s).
             You should check this output to see if your command was successful.
    :rtype: str

    ---
    **CAPABILITIES & STRATEGIC USAGE FOR AGENTS:**
    
    This tool is your key to solving complex problems that require setup or external programs.

    **1. Software & Dependency Management:**
       - **Problem:** A `codeExecutionAgent` fails with a `ModuleNotFoundError`.
       - **SOLUTION:** Use this tool to install the missing package.
       - **Example Call:** `runCommondInTerminal(Commond='pip install pandas')`
       - **Example Call:** `runCommondInTerminal(Commond='pip install -r requirements.txt')`

    **2. File System Management:**
       - **Problem:** You need to create a project structure before generating files.
       - **SOLUTION:** Use this tool to create directories.
       - **Example Call:** `runCommondInTerminal(Commond='mkdir ./my_new_project')`
       - **Other Commands:** `ls -l` (to see file details), `touch script.py` (to create an empty file),
         `rm old_file.txt` (to delete a file).

    **3. Information Gathering:**
       - **Problem:** You don't know the current working directory.
       - **SOLUTION:** Use the 'pwd' command.
       - **Example Call:** `runCommondInTerminal(Commond='pwd')`

    **4. Chaining with Other Tools:**
       - **If you are unsure of a command's syntax, use the `webSearchAgent` first!**
       - **Example Workflow:**
         1. **Goal:** Clone a git repository.
         2. **Thought:** I don't remember the exact command.
         3. **Action:** Call `webSearchAgent` with "how to clone a git repository".
         4. **Result:** The search tells me the command is `git clone [URL]`.
         5. **Action:** Call `runCommondInTerminal(Commond='git clone https://github.com/example/repo.git')`.
    """

    commondOutput = subprocess.run( Commond, shell=True, capture_output=True, text=True)
    out = commondOutput.stdout if commondOutput.returncode == 0 else commondOutput.stderr
    
    return out 
def generateImageFromPrompt(Prompt: str, numResults: int) -> str:
    """Generates one or more images from a detailed text prompt and saves them to a folder.

    This tool acts as a digital artist. It creates images based on your description. All generated
    images are ALWAYS saved inside a dedicated folder named './imageGenerationFolder/'.
    The files are named sequentially (image0.png, image1.png, etc.).

    :param Prompt: A highly descriptive text prompt of the image to be generated.
                   For best results, be specific about the subject, style, lighting, and composition.
                   Using keywords from web searches can significantly improve quality.
    :type Prompt: str
    
    :param numResults: The number of different images to generate from the prompt.
    :type numResults: int

    :return: A confirmation string indicating the output directory where the images are stored.
    :rtype: str

    ---
    **AGENT STRATEGY FOR CREATING GREAT IMAGES:**

    1.  **Deconstruct the Request:** Understand the core subject, style, and mood the user wants.
    2.  **Research if Necessary:** If the user asks for a specific style (e.g., "vaporwave", "art deco")
        or a subject you are unfamiliar with, use the `webSearchAgent` first to gather descriptive keywords.
    3.  **Construct a Rich Prompt:** Combine the user's request with the keywords from your research to
        build a powerful, detailed prompt.
    4.  **Execute and Inform:** Call this tool. After it succeeds, inform the user that their image(s)
        have been created and are located in the './imageGenerationFolder/' directory.

    **Usage Example (with research):**
    - **User:** "Make me a picture of a car in the cyberpunk style."
    - **Step 1 (Agent's thought):** I need to know what "cyberpunk style" means visually.
    - **Step 2 (Agent's action):** Call `webSearchAgent` with "cyberpunk aesthetic keywords".
    - **Step 3 (Agent's learning):** Search results provide keywords: "neon, rain, futuristic, high-tech,
      dystopian, glowing billboards, dark city streets".
    - **Step 4 (Agent's action):** Call `generateImageFromPrompt(
        Prompt="A futuristic cyberpunk car driving on a rain-slicked, dark city street at night, illuminated by glowing neon billboards and dramatic lighting, photorealistic, 8k",
        numResults=1
    )`
    - **Step 5 (Agent's response to user):** "I have created the image. It is stored at ./imageGenerationFolder/image0.png"
    """

    client = google.genai.Client(api_key='AIzaSyDH5WfjRliWtcO8z4b7yZ7io6inv_PQZ1E')
    generateContentConfig = google.genai.types.GenerateContentConfig(
        responseModalities=['TEXT', 'IMAGE']
    )
    subprocess.run('mkdir ./imageGenerationFolder', shell = True , capture_output = True, text = True )
    for i in range(numResults):
        response = client.models.generate_content(
            model='gemini-2.0-flash-preview-image-generation',
            contents=Prompt,
            config=generateContentConfig
        )

        for value in response.candidates[0].content.parts:
            if value.inline_data is not None:
                image = Image.open(BytesIO(value.inline_data.data))
                image.save(f'./imageGenerationFolder/image{i}.png')

    return 'images stored at ./imageGenerationFolder '

