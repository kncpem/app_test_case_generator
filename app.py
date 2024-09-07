import requests
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()
from prompt import examples
import io
import google.generativeai as genai
from pdf2image import convert_from_bytes
from PIL import Image
import base64

genai.configure(api_key = os.getenv("GOOGLE_API_KEY"))

st.title("RedBus Test Case Generator")
context = st.text_area("Provide optional context for the test")
uploaded_files = st.file_uploader("Upload RedBus App Screenshots", type=['png', 'jpg'], accept_multiple_files=True)


def handle_image_upload(uploaded_file):
    if uploaded_file is not None:
        image_data = uploaded_file.getvalue() 
        image_byte_arr = io.BytesIO(image_data)
        mime_type = uploaded_file.type
        image_parts = [
            {
                "mime_type": mime_type,
                "data": base64.b64encode(image_byte_arr.getvalue()).decode()
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

def get_gemini_response(input_text, image_data, examples):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, image_data, examples])
    return response

if uploaded_files:
    if st.button("Describe Testing Instructions"):
        try:
            image_parts = []
            for uploaded_file in uploaded_files:
                image_parts.extend(handle_image_upload(uploaded_file))

            prompt = examples
            gemini_response = get_gemini_response(context, image_parts[0], prompt)

            test_cases = gemini_response.candidates[0].content.parts[0].text

            st.write("Test Case Generated:")
            st.markdown(test_cases)

        except FileNotFoundError as e:
            st.error(str(e))