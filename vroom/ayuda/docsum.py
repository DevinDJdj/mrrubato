#pip install sumy
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# Input text to be summarized


input_text = """
Your input text goes here. It can be a long paragraph or multiple paragraphs. 
"""

with open('./uploads/transcripts/00973440_20240918100044.txt') as f:
    input_text = f.read()

# Parse the input text
parser = PlaintextParser.from_string(input_text, Tokenizer("english"))

# Create an LSA summarizer
summarizer = LsaSummarizer()

# Generate the summary
summary = summarizer(parser.document, sentences_count=3)  # You can adjust the number of sentences in the summary

# Output the summary
print("Original Text:")
print(input_text)
print("\nSummary:")
for sentence in summary:
    print(sentence)

