#pip install spacy translate
#pip install googletrans

import spacy
from translate import Translator

# Load a Japanese language model (e.g., for analysis)
nlp = spacy.load("ja_core_news_md")



# Initialize the translator (example using Google Translate)

translator = Translator(to_lang="en", from_lang="ja")

def translate_japanese_to_english(text):
  """
  Translates Japanese text to English using SpaCy for analysis and the 'translate' library for translation.
  """
  # Process with SpaCy (optional, but helpful for analysis)
  doc = nlp(text)

  # Extract text from the SpaCy Doc and translate
  try:
    translation = translator.translate(text)
    return translation
  except Exception as e:
      print(f"Translation error: {e}")
      return None

# Example usage
japanese_text = "こんにちは、世界！"
english_translation = translate_japanese_to_english(japanese_text)
if english_translation:
    print(f"Original: {japanese_text}")
    print(f"Translated: {english_translation}")
