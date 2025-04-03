#fairly slow...but works...
import ollama
import base64
# Option 1: Encode image to base64
with open("../../web/public/images/thinking.gif", "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

# Option 2: Use file path
image_path = "path/to/your/image.jpg"


# Using ollama.chat
response = ollama.chat(
    model="llava", # Replace with your multimodal model name
    messages=[
        {
            "role": "user",
            "content": "Describe this image.",
            "images": [encoded_string] # Use image_path for file path
        }
    ]
)
print(response['message']['content'])