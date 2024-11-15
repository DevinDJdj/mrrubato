#pip install google-generativeai
import sys

import datetime
# adding Folder_2/subfolder to the system path
#not great mechanism for config.  Maybe just make absolute path?
sys.path.insert(0, 'c:/devinpiano/')
sys.path.insert(1, 'c:/devinpiano/music')
#sys.path.append('../')
import config  

import os
import pandas as pd
import requests
import json
from oauth2client.tools import argparser, run_flow
import google.generativeai as genai

from IPython.display import HTML, Markdown, display
import time



if __name__ == '__main__':
    argparser.add_argument("--title", help="Video title", default="What a Wonderful World")
    argparser.add_argument("--video", help="Video ID", default="4flRJWtfY9c")

    args = argparser.parse_args()


    genai.configure(api_key=config.cfg['google']['AISTUDIO'])
    flash = genai.GenerativeModel('gemini-1.5-flash')
    response = flash.generate_content("Explain how AI works as if I were a kid.")
    Markdown(response.text)


    chat = flash.start_chat(history=[])
    response = chat.send_message('Hello! My name is Zlork.')
    print(response.text)

    response = chat.send_message('Can you tell something interesting about dinosaurs?')
    print(response.text)

    response = chat.send_message('Do you remember what my name is?')
    print(response.text)

    for model in genai.list_models():
        print(model.name)

    for model in genai.list_models():
        if model.name == 'models/gemini-1.5-flash':
            print(model)
            break

    #temperature=1.0,  
    #higher temperature is related to randomness
    short_model = genai.GenerativeModel(
        'gemini-1.5-flash',
        generation_config=genai.GenerationConfig(max_output_tokens=200))

    response = short_model.generate_content('Write a 1000 word essay on the importance of olives in modern society.')
    print(response.text)



    high_temp_model = genai.GenerativeModel(
        'gemini-1.5-flash',
        generation_config=genai.GenerationConfig(temperature=2.0))

    for _ in range(3):
        response = high_temp_model.generate_content('Pick a random colour... (answer in a single word)')
        if response.parts:
            print(response.text, '-' * 25)

        # Slow down a bit so we don't get Resource Exhausted errors.
        time.sleep(20)


    low_temp_model = genai.GenerativeModel(
        'gemini-1.5-flash',
        generation_config=genai.GenerationConfig(temperature=0.0))

    for _ in range(4):
        response = low_temp_model.generate_content('Pick a random colour... (answer in a single word)')
        if response.parts:
            print(response.text, '-' * 25)

    time.sleep(20)


    model = genai.GenerativeModel(
        'gemini-1.5-flash-001',
        generation_config=genai.GenerationConfig(
            # These are the default values for gemini-1.5-flash-001.
            temperature=1.0,
            top_k=64,
            top_p=0.95,
        ))

    story_prompt = "You are a creative writer. Write a short story about a cat who goes on an adventure."
    response = model.generate_content(story_prompt)
    print(response.text)


    model = genai.GenerativeModel(
    'gemini-1.5-flash-001',
        generation_config=genai.GenerationConfig(
            temperature=0.1,
            top_p=1,
            max_output_tokens=5,
        ))

    zero_shot_prompt = """Classify movie reviews as POSITIVE, NEUTRAL or NEGATIVE.
    Review: "Her" is a disturbing study revealing the direction
    humanity is headed if AI is allowed to keep evolving,
    unchecked. I wish there were more movies like this masterpiece.
    Sentiment: """

    response = model.generate_content(zero_shot_prompt)
    print(response.text)


    import enum

    class Sentiment(enum.Enum):
        POSITIVE = "positive"
        NEUTRAL = "neutral"
        NEGATIVE = "negative"


    model = genai.GenerativeModel(
        'gemini-1.5-flash-001',
        generation_config=genai.GenerationConfig(
            response_mime_type="text/x.enum",
            response_schema=Sentiment
        ))

    response = model.generate_content(zero_shot_prompt)
    print(response.text)


    model = genai.GenerativeModel(
        'gemini-1.5-flash-latest',
        generation_config=genai.GenerationConfig(
            temperature=0.1,
            top_p=1,
            max_output_tokens=250,
        ))

    few_shot_prompt = """Parse a customer's pizza order into valid JSON:

        EXAMPLE:
        I want a small pizza with cheese, tomato sauce, and pepperoni.
        JSON Response:
        ```
        {
        "size": "small",
        "type": "normal",
        "ingredients": ["cheese", "tomato sauce", "peperoni"]
        }
        ```

        EXAMPLE:
        Can I get a large pizza with tomato sauce, basil and mozzarella
        JSON Response:
        ```
        {
        "size": "large",
        "type": "normal",
        "ingredients": ["tomato sauce", "basil", "mozzarella"]
        }

        ORDER:
    """

    customer_order = "Give me a large with cheese & pineapple"


    response = model.generate_content([few_shot_prompt, customer_order])
    print(response.text)


    import typing_extensions as typing

    class PizzaOrder(typing.TypedDict):
        size: str
        ingredients: list[str]
        type: str


    model = genai.GenerativeModel(
        'gemini-1.5-flash-latest',
        generation_config=genai.GenerationConfig(
            temperature=0.1,
            response_mime_type="application/json",
            response_schema=PizzaOrder,
        ))

    response = model.generate_content("Can I have a large dessert pizza with apple and chocolate")
    print(response.text)


    prompt = """When I was 4 years old, my partner was 3 times my age. Now, I
    am 20 years old. How old is my partner? Return the answer immediately."""

    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(prompt)

    print(response.text)


    prompt = """When I was 4 years old, my partner was 3 times my age. Now,
    I am 20 years old. How old is my partner? Let's think step by step."""

    response = model.generate_content(prompt)
    print(response.text)



    model_instructions = """
    Solve a question answering task with interleaving Thought, Action, Observation steps. Thought can reason about the current situation,
    Observation is understanding relevant information from an Action's output and Action can be one of three types:
    (1) <search>entity</search>, which searches the exact entity on Wikipedia and returns the first paragraph if it exists. If not, it
        will return some similar entities to search and you can try to search the information from those topics.
    (2) <lookup>keyword</lookup>, which returns the next sentence containing keyword in the current context. This only does exact matches,
        so keep your searches short.
    (3) <finish>answer</finish>, which returns the answer and finishes the task.
    """

    example1 = """Question
    Musician and satirist Allie Goertz wrote a song about the "The Simpsons" character Milhouse, who Matt Groening named after who?

    Thought 1
    The question simplifies to "The Simpsons" character Milhouse is named after who. I only need to search Milhouse and find who it is named after.

    Action 1
    <search>Milhouse</search>

    Observation 1
    Milhouse Mussolini Van Houten is a recurring character in the Fox animated television series The Simpsons voiced by Pamela Hayden and created by Matt Groening.

    Thought 2
    The paragraph does not tell who Milhouse is named after, maybe I can look up "named after".

    Action 2
    <lookup>named after</lookup>

    Observation 2
    Milhouse was named after U.S. president Richard Nixon, whose middle name was Milhous.

    Thought 3
    Milhouse was named after U.S. president Richard Nixon, so the answer is Richard Nixon.

    Action 3
    <finish>Richard Nixon</finish>
    """

    example2 = """Question
    What is the elevation range for the area that the eastern sector of the Colorado orogeny extends into?

    Thought 1
    I need to search Colorado orogeny, find the area that the eastern sector of the Colorado orogeny extends into, then find the elevation range of the area.

    Action 1
    <search>Colorado orogeny</search>

    Observation 1
    The Colorado orogeny was an episode of mountain building (an orogeny) in Colorado and surrounding areas.

    Thought 2
    It does not mention the eastern sector. So I need to look up eastern sector.

    Action 2
    <lookup>eastern sector</lookup>

    Observation 2
    The eastern sector extends into the High Plains and is called the Central Plains orogeny.

    Thought 3
    The eastern sector of Colorado orogeny extends into the High Plains. So I need to search High Plains and find its elevation range.

    Action 3
    <search>High Plains</search>

    Observation 3
    High Plains refers to one of two distinct land regions

    Thought 4
    I need to instead search High Plains (United States).

    Action 4
    <search>High Plains (United States)</search>

    Observation 4
    The High Plains are a subregion of the Great Plains. From east to west, the High Plains rise in elevation from around 1,800 to 7,000 ft (550 to 2,130m).

    Thought 5
    High Plains rise in elevation from around 1,800 to 7,000 ft, so the answer is 1,800 to 7,000 ft.

    Action 5
    <finish>1,800 to 7,000 ft</finish>
    """


    question = """Question
    Who was the youngest author listed on the transformers NLP paper?
    """

    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    react_chat = model.start_chat()

    # You will perform the Action, so generate up to, but not including, the Observation.
    config = genai.GenerationConfig(stop_sequences=["\nObservation"])

    resp = react_chat.send_message(
        [model_instructions, example1, example2, question],
        generation_config=config)
    print(resp.text)


    observation = """Observation 1
    [1706.03762] Attention Is All You Need
    Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, Illia Polosukhin
    We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.
    """
    resp = react_chat.send_message(observation, generation_config=config)
    print(resp.text)


    model = genai.GenerativeModel(
    'gemini-1.5-flash-latest',
    generation_config=genai.GenerationConfig(
        temperature=1,
        top_p=1,
        max_output_tokens=1024,
    ))

    # Gemini 1.5 models are very chatty, so it helps to specify they stick to the code.
    code_prompt = """
    Write a Python function to calculate the factorial of a number. No explanation, provide only the code.
    """

    response = model.generate_content(code_prompt)
    Markdown(response.text)


    model = genai.GenerativeModel(
        'gemini-1.5-flash-latest',
        tools='code_execution')

    code_exec_prompt = """
    Calculate the sum of the first 14 prime numbers. Only consider the odd primes, and make sure you get them all.
    """

    response = model.generate_content(code_exec_prompt)
    Markdown(response.text)
