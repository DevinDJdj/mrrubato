#pip install googletrans
#pip install asyncio

import asyncio
from googletrans import Translator

translator = Translator()
async def translate_japanese_to_english(text):
    """
    Translates Japanese text to English using the 'googletrans' library.
    """
    try:
        translation = await translator.translate(text, src='ja', dest='en')
        return translation.text
    except Exception as e:
        print(f"Translation error: {e}")
        return None
    
input = "こんにちは、世界！"
translated = asyncio.run(translate_japanese_to_english(input))
if translated:
    print(f"Original: {input}")
    print(f"Translated: {translated}")
