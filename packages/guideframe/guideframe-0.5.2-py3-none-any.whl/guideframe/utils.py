from guideframe.audio import generate_voicover
from guideframe.video import start_ffmpeg_recording, stop_ffmpeg_recording
import time
import sys

# Function to get the environment settings based on the argument provided to the script
def get_env_settings():
    if len(sys.argv) > 1:
        env = sys.argv[1]  # Getting the environment argument
    else:
        print("No environment argument provided. Use 'macos' or 'github'.")
        sys.exit(1)

    # Define settings based on environment
    if env == "macos":
        return {
            "input_format": "avfoundation",
            "input_display": "1",
            "driver_location": "/opt/homebrew/bin/chromedriver"
        }
    elif env == "github":
        return {
            "input_format": "x11grab",
            "input_display": ":99.0",
            "driver_location": "/usr/bin/chromedriver"
        }
    else:
        print("Invalid environment specified. Use 'macos' or 'github'.")
        sys.exit(1)


# Function to extract the markdown filename based on the script name (to prevent hard coding filename)
def extract_md_filename():
    script_name = sys.argv[0]
    return script_name.replace(".py", ".md")

# Function to extract the script name and drop the extension (for use in final output naming)
def extract_script_name():
    script_name = sys.argv[0]
    return script_name.replace(".py", "")

# Function to run a step in the guide
def guide_step(step_number, *actions, order="action-after-vo"):
    # Get the environment settings
    env_settings = get_env_settings()
    input_format = env_settings["input_format"]
    input_display = env_settings["input_display"]
    md_file = extract_md_filename()

    # Start the recording for the step
    step = start_ffmpeg_recording(f"step{step_number}.mp4", input_format, input_display)

    # Conditional logic to account for vo relative to action
    if order == "action-before-vo":
        for action in actions:
            action()
            # time.sleep(1)
        generate_voicover(md_file, step_number)
    else:  # Default order is action-after-vo
        generate_voicover(md_file, step_number)
        for action in actions:
            action()
            # time.sleep(1)

    stop_ffmpeg_recording(step)