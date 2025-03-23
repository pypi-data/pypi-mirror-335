from gtts import gTTS # Importing gTTS for audio generation (opensource based on Google translate API)
from mutagen.mp3 import MP3 # Importing the MP3 module from mutagen for audio length checking
import time # Importing the time module for sleep functions
import re # Importing regex library as this proved a simple method for extracting text under headings

'''
Pivoting to gTTS
This has a significantly simpler design in terms of saving clips so it better serves this need that pytts
It also sounds generally better and easily fulfills the intended logic in terms of clip generation for later splicing
Leaving pytts in for now until clip assembly logic is in place.
'''

# Function to create the gTTS speech clips. Takes the text arg passed by the user and a file name to write it to
def export_gtts(text, file_name):
    tts = gTTS(text)
    tts.save(file_name)
    print("Exported", file_name)


# Function to check the length of an audio clip and then sleep based on it
def sleep_based_on_vo(file_name):
    audio = MP3(file_name)
    print("Sleeping for", audio.info.length, "seconds")
    time.sleep(audio.info.length)


# Function to extract the markdown content under a specified heading
def pull_vo_from_markdown(md_file, step_number):
    # Open the markdown file and read
    with open(md_file, "r", encoding="utf-8") as file:
        md_content = file.read()
    
    '''
    Regex pattern breakdown:

    ## Step {step_number} -> The step heading to match
    \s* -> Any whitespace characters before the content
    (.*?) -> The content under the step heading
    (?=\n##|\Z) -> A lookahead to match the next step heading (##) or the end of the file
    '''

    # Define the regex pattern for the step heading (explained above)
    step_heading = rf"## Step {step_number}\s*(.*?)\s*(?=\n##|\Z)"

    # Search the markdown content for the step heading
    match = re.search(step_heading, md_content, re.DOTALL)

    # Return the content under the step heading if found
    return match.group(1).strip() if match else None


# Function to generate the voiceover (in order to avoid repetition in main script)
def generate_voicover(md_file, step_number):
    # Extract voiceover text from the .md file (hard coded for now as each test will need this function defined)
    voiceover = pull_vo_from_markdown(md_file, step_number) # Passing the step number and file to the regex based function

    # Check if content was found
    if not voiceover:
        print(f"Warning: No content found for Step {step_number}")
        return

    # Export the voiceover to an MP3 file
    export_gtts(voiceover, f"step{step_number}.mp3")
    # Sleeping based on the length of the voiceover
    sleep_based_on_vo(f"step{step_number}.mp3")