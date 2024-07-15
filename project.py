import streamlit as st
import requests
import sounddevice as sd
import wavio
import openai
import os
from PIL import Image
from io import BytesIO

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] ="sk-proj-mnPBz2ZgT98sEof1W8mAT3BlbkFJK3PpoCycfFUaUVBLgCZ1"
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to record audio
def record_audio(filename, duration, fs):
    st.info("Recording audio...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()
    wavio.write(filename, recording, fs, sampwidth=2)
    st.success(f"Audio recorded and saved as {filename}")

# Function to generate an image from text
def generate_image_from_text(text):
    try:
        with st.spinner("Generating image..."):
            response = openai.Image.create(
                prompt=text,
                n=1,
                size="1024x1024"
            )
        
        # Extract the URL of the generated image
        image_url = response['data'][0]['url']
        
        # Download the image
        image_response = requests.get(image_url)
        image_response.raise_for_status()  # Raise an HTTPError for bad responses
        
        # Convert the image response to a PIL Image
        image = Image.open(BytesIO(image_response.content))
        
        # Save and display the image
        image_path = "generated_image.jpg"
        image.save(image_path)
        st.success("Image generated successfully!")
        st.image(image_path, caption="Generated Image", use_column_width=True)
        
        return image

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to download the image: {e}")
    except openai.error.OpenAIError as e:
        st.error(f"OpenAI API error: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

# Streamlit interface
st.title("Voice and Text to Image Generator")
st.write("Use your voice or enter text to generate an image based on the input using AI.")

# Radio buttons to select input method
input_method = st.radio("Select input method:", ("Voice", "Text"))

if input_method == "Voice":
    if st.button("Click here to speak"):
        audio_filename = "input.wav"
        duration = 5  # Duration of the recording in seconds
        fs = 44100  # Sample rate
        record_audio(audio_filename, duration, fs)  # User input recorded and stored

        # Converting to text using OpenAI's Whisper model
        with st.spinner("Transcribing audio..."):
            audio_file = open(audio_filename, "rb")
            transcript = openai.Audio.transcribe(
                model="whisper-1", 
                file=audio_file
            )
        a = transcript['text']
        st.write("Transcribed Text:", a)

        # Generate image from transcribed text
        generate_image_from_text(a)

elif input_method == "Text":
    user_input = st.text_area("Enter your text here:")
    if st.button("Generate Image"):
        generate_image_from_text(user_input)

st.write("Powered by OpenAI")