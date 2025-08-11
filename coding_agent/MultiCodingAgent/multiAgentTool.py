from IPython.display import Audio
from typing import List
import speech_recognition
from PIL import Image
from io import BytesIO
import pydub
import logging
import wave
import google.genai
import google
import subprocess

logger = logging.getLogger()
logger.setLevel(logging.INFO)
userPersonalInformation = []

# class toolBox:
#     """
#     A collection of utility tools for handling audio, images, text, and system commands.
#     Designed for use in interactive AI-agent environments such as Gemini.
#     """

#     def __init__(self):
#         """
#         Initialize the toolBox with an empty personal user information store.
#         """
#         self.userPersonalInformation = []

#     @staticmethod
def convertAudioToText(filePath: str) -> str:
    """
    Convert a spoken audio file into transcribed text using Google Speech Recognition.

    Supports `.wav` and `.mp3` formats. MP3 files are converted to WAV before processing.
    If speech is unclear, logs an informational message and returns None.

    Args:
        filePath (str): Path to the audio file. Must be `.wav` or `.mp3`.

    Returns:
        str: Transcribed text if successful, otherwise None.

    Raises:
        ValueError: If file format is unsupported.
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

# @staticmethod
def textToAudio(text: str) -> str:
    """
    Convert a text string into a spoken audio file using Gemini TTS.

    The output is saved locally at `./textToAudioFile.wav`.

    Args:
        text (str): The text content to convert into speech.

    Returns:
        str: Informational message with save path and playback instructions.
    """
    client = google.genai.Client(api_key='YOUR_API_KEY')
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

# @staticmethod
def playAudioFile(filePath: str) -> None:
    """
    Play an audio file in the current environment.

    Uses IPython's Audio display class.
    Intended for Jupyter or similar interactive environments.

    Args:
        filePath (str): Path to the audio file.

    Returns:
        None
    """
    Audio(filename=filePath, autoplay=True)

# @staticmethod
def storePersonalUserInformation(userInformation: str) -> str:
    global userPersonalInformation
    """
    Store personal user information in memory.

    Args:
        userInformation (str): Information to store.

    Returns:
        str: Message indicating storage index and usage instructions.
    """
    storedIndex = len(userPersonalInformation)
    userPersonalInformation.append([userInformation])
    return (
        f'userInformation is stored at index {storedIndex}. '
        'You can remove it later using removePersonalUserInformation tool.'
    )

# @staticmethod
def removePersonalUserInformation(userInformationIndex: int) -> str:
    global userPersonalInformation
    """
    Remove stored personal user information by its index.

    Args:
        userInformationIndex (int): Index of the information to remove.

    Returns:
        str: Success or error message.
    """
    try:
        userPersonalInformation.pop(userInformationIndex)
        return f'userPersonalInformation at index {userInformationIndex} is removed.'
    except Exception as error:
        return f'Error: {error}'

# @staticmethod
def getuserPersonalInformation() -> List:
    """
    Retrieve all stored personal user information.

    Returns:
        List: A list of stored user information entries.
    """
    return userPersonalInformation

# @staticmethod
def runCommondInTerminal(Commond: str) -> str:
    """
    Execute a shell command and return its output.

    Args:
        Commond (str): Command to run in the terminal.

    Returns:
        str: Command output if successful, else error output.
    """
    commondOutput = subprocess.run(Commond, shell=True, capture_output=True, text=True)
    return commondOutput.stdout if commondOutput.returncode == 0 else commondOutput.stderr

# @staticmethod
def generateImageFromPrompt(Prompt: str) -> str:
    """
    Generate an image from a text prompt using Gemini image generation model.

    Saves the generated image as `image.png`.

    Args:
        Prompt (str): The image description prompt.

    Returns:
        str: Message indicating the image save path.
    """
    client = google.genai.Client(api_key='YOUR_API_KEY')
    generateContentConfig = google.genai.types.GenerateContentConfig(
        responseModalities=['TEXT', 'IMAGE']
    )
    response = client.models.generate_content(
        model='gemini-2.0-flash-preview-image-generation',
        contents=Prompt,
        config=generateContentConfig
    )

    for value in response.candidates[0].content.parts:
        if value.inline_data is not None:
            image = Image.open(BytesIO(value.inline_data.data))
            image.save('image.png')

    return 'Image saved at ./image.png'


