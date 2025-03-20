#!/usr/bin/env python3
import os
from google import genai
from google.genai import types

def generate(image_path):
    # Hardcoded Gemini API key (for personal use)
    api_key = "AIzaSyDiNZBLQMDBFHSXOPp0Aa0ODvKih_2Sgow"
    client = genai.Client(api_key=api_key)

    # Upload the user-specified image for OCR
    user_file = client.files.upload(file=image_path)

    model = "gemini-2.0-flash-lite"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_uri(
                    file_uri=user_file.uri,
                    mime_type=user_file.mime_type,
                ),
                types.Part.from_text(
                    text="Please transcribe the handwritten Hindi text in this image. The text is in Hindi handwriting. Provide the transcribed text in Devanagari script (Hindi script). Also, just directly give me the extracted text nothing else"
                ),
            ],
        ),
    ]

    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")
if __name__ == "__main__":
    image_path = input("Enter the path to the image for Hindi OCR: ").strip()
    if not os.path.exists(image_path):
        print("Error: The file does not exist.")
    else:
        generate(image_path)
