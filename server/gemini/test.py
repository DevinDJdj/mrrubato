#pip install --upgrade --quiet google-genai

import sys
from IPython.display import HTML, Image, Markdown, display
from google import genai
from google.genai.types import (
    FunctionDeclaration,
    GenerateContentConfig,
    GoogleSearch,
    HarmBlockThreshold,
    HarmCategory,
    Part,
    SafetySetting,
    Tool,
    ToolCodeExecution,
)

sys.path.insert(0, 'c:/devinpiano/')
sys.path.insert(1, 'c:/devinpiano/music/')
#sys.path.append('../')
import config  



PROJECT_ID = config.cfg['google']['PROJECT_ID']  # @param {type: "string", placeholder: "[your-project-id]", isTemplate: true}
LOCATION = config.cfg['google']['LOCATION']  # @param {type: "string", placeholder: "[your-location]", isTemplate: true}
API_KEY = config.cfg['google']['AISTUDIO']  # @param {type: "string", placeholder: "[your-api-key]", isTemplate: true}

#client = genai.Client(vertexai=True, api_key=API_KEY)
client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

MODEL_ID = "gemini-2.5-pro-exp-03-25"  # @param {type: "string"}

response = client.models.generate_content(
    model=MODEL_ID, contents="What's the largest planet in our solar system?"
)

display(Markdown(response.text))
