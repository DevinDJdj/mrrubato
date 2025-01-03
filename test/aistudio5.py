#agent with langgraph
#pip install langgraph langchain-google-genai
#not tested.  For conceptual understanding.  

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
from chromadb import Documents, EmbeddingFunction, Embeddings
from google.api_core import retry

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from google.api_core import retry

import sqlite3
import textwrap

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages

from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from IPython.display import Image, display
from pprint import pprint
from langchain_core.messages.ai import AIMessage

from typing import Literal
from langchain_core.tools import tool

from langgraph.prebuilt import ToolNode
from collections.abc import Iterable
from random import randint

from langgraph.prebuilt import InjectedState
from langchain_core.messages.tool import ToolMessage






@tool
def add_to_order(drink: str, modifiers: Iterable[str]) -> str:
    """Adds the specified drink to the customer's order, including any modifiers.

    Returns:
      The updated order in progress.
    """


@tool
def confirm_order() -> str:
    """Asks the customer if the order is correct.

    Returns:
      The user's free-text response.
    """


@tool
def get_order() -> str:
    """Returns the users order so far. One item per line."""


@tool
def clear_order():
    """Removes all items from the user's order."""


@tool
def place_order() -> int:
    """Sends the order to the barista for fulfillment.

    Returns:
      The estimated number of minutes until the order is ready.
    """



@tool
def get_menu() -> str:
    """Provide the latest up-to-date menu."""
    # Note that this is just hard-coded text, but you could connect this to a live stock
    # database, or you could use Gemini's multi-modal capabilities and take live photos of
    # your cafe's chalk menu or the products on the counter and assmble them into an input.

    return """
    MENU:
    Coffee Drinks:
    Espresso
    Americano
    Cold Brew

    Coffee Drinks with Milk:
    Latte
    Cappuccino
    Cortado
    Macchiato
    Mocha
    Flat White

    Tea Drinks:
    English Breakfast Tea
    Green Tea
    Earl Grey

    Tea Drinks with Milk:
    Chai Latte
    Matcha Latte
    London Fog

    Other Drinks:
    Steamer
    Hot Chocolate

    Modifiers:
    Milk options: Whole, 2%, Oat, Almond, 2% Lactose Free; Default option: whole
    Espresso shots: Single, Double, Triple, Quadruple; default: Double
    Caffeine: Decaf, Regular; default: Regular
    Hot-Iced: Hot, Iced; Default: Hot
    Sweeteners (option to add one or more): vanilla sweetener, hazelnut sweetener, caramel sauce, chocolate sauce, sugar free vanilla sweetener
    Special requests: any reasonable modification that does not involve items not on the menu, for example: 'extra hot', 'one pump', 'half caff', 'extra foam', etc.

    "dirty" means add a shot of espresso to a drink that doesn't usually have it, like "Dirty Chai Latte".
    "Regular milk" is the same as 'whole milk'.
    "Sweetened" means add some regular sugar, not a sweetener.

    Soy milk has run out of stock today, so soy is not available.
  """

class OrderState(TypedDict):
    """State representing the customer's order conversation."""

    # The chat conversation. This preserves the conversation history
    # between nodes. The `add_messages` annotation indicates to LangGraph
    # that state is updated by appending returned messages, not replacing
    # them.
    messages: Annotated[list, add_messages]

    # The customer's in-progress order.
    order: list[str]

    # Flag indicating that the order is placed and completed.
    finished: bool



def human_node(state: OrderState) -> OrderState:
    """Display the last model message to the user, and receive the user's input."""
    last_msg = state["messages"][-1]
    print("Model:", last_msg.content)

    user_input = input("User: ")

    # If it looks like the user is trying to quit, flag the conversation
    # as over.
    if user_input in {"q", "quit", "exit", "goodbye"}:
        state["finished"] = True

    return state | {"messages": [("user", user_input)]}


def chatbot_with_welcome_msg(state: OrderState) -> OrderState:
    """The chatbot itself. A wrapper around the model's own chat interface."""

    if state["messages"]:
        # If there are messages, continue the conversation with the Gemini model.
        new_output = llm.invoke([BARISTABOT_SYSINT] + state["messages"])
    else:
        # If there are no messages, start with the welcome message.
        new_output = AIMessage(content=WELCOME_MSG)

    return state | {"messages": [new_output]}


def maybe_exit_human_node(state: OrderState) -> Literal["chatbot", "__end__"]:
    """Route to the chatbot, unless it looks like the user is exiting."""
    if state.get("finished", False):
        return END
    else:
        return "chatbot"



def maybe_route_to_tools(state: OrderState) -> Literal["tools", "human"]:
    """Route between human or tool nodes, depending if a tool call is made."""
    if not (msgs := state.get("messages", [])):
        raise ValueError(f"No messages found when parsing state: {state}")

    # Only route based on the last message.
    msg = msgs[-1]

    # When the chatbot returns tool_calls, route to the "tools" node.
    if hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
        return "tools"
    else:
        return "human"


def chatbot_with_tools(state: OrderState) -> OrderState:
    """The chatbot with tools. A simple wrapper around the model's own chat interface."""
    defaults = {"order": [], "finished": False}

    if state["messages"]:
        new_output = llm_with_tools.invoke([BARISTABOT_SYSINT] + state["messages"])
    else:
        new_output = AIMessage(content=WELCOME_MSG)

    # Set up some defaults if not already set, then pass through the provided state,
    # overriding only the "messages" field.
    return defaults | state | {"messages": [new_output]}



def order_node(state: OrderState) -> OrderState:
    """The ordering node. This is where the order state is manipulated."""
    tool_msg = state.get("messages", [])[-1]
    order = state.get("order", [])
    outbound_msgs = []
    order_placed = False

    for tool_call in tool_msg.tool_calls:

        if tool_call["name"] == "add_to_order":

            # Each order item is just a string. This is where it assembled as "drink (modifiers, ...)".
            modifiers = tool_call["args"]["modifiers"]
            modifier_str = ", ".join(modifiers) if modifiers else "no modifiers"

            order.append(f'{tool_call["args"]["drink"]} ({modifier_str})')
            response = "\n".join(order)

        elif tool_call["name"] == "confirm_order":

            # We could entrust the LLM to do order confirmation, but it is a good practice to
            # show the user the exact data that comprises their order so that what they confirm
            # precisely matches the order that goes to the kitchen - avoiding hallucination
            # or reality skew.

            # In a real scenario, this is where you would connect your POS screen to show the
            # order to the user.

            print("Your order:")
            if not order:
                print("  (no items)")

            for drink in order:
                print(f"  {drink}")

            response = input("Is this correct? ")

        elif tool_call["name"] == "get_order":

            response = "\n".join(order) if order else "(no order)"

        elif tool_call["name"] == "clear_order":

            order.clear()
            response = None

        elif tool_call["name"] == "place_order":

            order_text = "\n".join(order)
            print("Sending order to kitchen!")
            print(order_text)

            # TODO(you!): Implement cafe.
            order_placed = True
            response = randint(1, 5)  # ETA in minutes

        else:
            raise NotImplementedError(f'Unknown tool call: {tool_call["name"]}')

        # Record the tool results as tool messages.
        outbound_msgs.append(
            ToolMessage(
                content=response,
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )
        )

    return {"messages": outbound_msgs, "order": order, "finished": order_placed}


def maybe_route_to_tools(state: OrderState) -> str:
    """Route between chat and tool nodes if a tool call is made."""
    if not (msgs := state.get("messages", [])):
        raise ValueError(f"No messages found when parsing state: {state}")

    msg = msgs[-1]

    if state.get("finished", False):
        # When an order is placed, exit the app. The system instruction indicates
        # that the chatbot should say thanks and goodbye at this point, so we can exit
        # cleanly.
        return END

    elif hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
        # Route to `tools` node for any automated tool calls first.
        if any(
            tool["name"] in tool_node.tools_by_name.keys() for tool in msg.tool_calls
        ):
            return "tools"
        else:
            return "ordering"

    else:
        return "human"
    

def chatbot(state: OrderState) -> OrderState:
    """The chatbot itself. A simple wrapper around the model's own chat interface."""
    message_history = [BARISTABOT_SYSINT] + state["messages"]
    return {"messages": [llm.invoke(message_history)]}

# The system instruction defines how the chatbot is expected to behave and includes
# rules for when to call different functions, as well as rules for the conversation, such
# as tone and what is permitted for discussion.
BARISTABOT_SYSINT = (
    "system",  # 'system' indicates the message is a system instruction.
    "You are a BaristaBot, an interactive cafe ordering system. A human will talk to you about the "
    "available products you have and you will answer any questions about menu items (and only about "
    "menu items - no off-topic discussion, but you can chat about the products and their history). "
    "The customer will place an order for 1 or more items from the menu, which you will structure "
    "and send to the ordering system after confirming the order with the human. "
    "\n\n"
    "Add items to the customer's order with add_to_order, and reset the order with clear_order. "
    "To see the contents of the order so far, call get_order (this is shown to you, not the user) "
    "Always confirm_order with the user (double-check) before calling place_order. Calling confirm_order will "
    "display the order items to the user and returns their response to seeing the list. Their response may contain modifications. "
    "Always verify and respond with drink and modifier names from the MENU before adding them to the order. "
    "If you are unsure a drink or modifier matches those on the MENU, ask a question to clarify or redirect. "
    "You only have the modifiers listed on the menu. "
    "Once the customer has finished ordering items, Call confirm_order to ensure it is correct then make "
    "any necessary updates and then call place_order. Once place_order has returned, thank the user and "
    "say goodbye!",
)

# This is the message with which the system opens the conversation.
WELCOME_MSG = "Welcome to the BaristaBot cafe. Type `q` to quit. How may I serve you today?"

if __name__ == '__main__':
    argparser.add_argument("--title", help="Video title", default="What a Wonderful World")
    argparser.add_argument("--video", help="Video ID", default="4flRJWtfY9c")

    args = argparser.parse_args()


    genai.configure(api_key=config.cfg['google']['AISTUDIO'])

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")


    # Define the tools and create a "tools" node.
    tools = [get_menu]
    tool_node = ToolNode(tools)

    # Attach the tools to the model so that it knows what it can call.
    llm_with_tools = llm.bind_tools(tools)



    # Set up the initial graph based on our state definition.
    graph_builder = StateGraph(OrderState)

    # Add the chatbot function to the app graph as a node called "chatbot".
    graph_builder.add_node("chatbot", chatbot)

    # Define the chatbot node as the app entrypoint.
    graph_builder.add_edge(START, "chatbot")

    chat_graph = graph_builder.compile()

    Image(chat_graph.get_graph().draw_mermaid_png())

    user_msg = "Hello, what can you do?"
    state = chat_graph.invoke({"messages": [user_msg]})

    # The state object contains lots of information. Uncomment the pprint lines to see it all.
    # pprint(state)

    # Note that the final state now has 2 messages. Our HumanMessage, and an additional AIMessage.
    for msg in state["messages"]:
        print(f"{type(msg).__name__}: {msg.content}")


    user_msg = "Oh great, what kinds of latte can you make?"

    state["messages"].append(user_msg)
    state = chat_graph.invoke(state)

    # pprint(state)
    for msg in state["messages"]:
        print(f"{type(msg).__name__}: {msg.content}")


    # Start building a new graph.
    graph_builder = StateGraph(OrderState)

    # Add the chatbot and human nodes to the app graph.
    graph_builder.add_node("chatbot", chatbot_with_welcome_msg)
    graph_builder.add_node("human", human_node)

    # Start with the chatbot again.
    graph_builder.add_edge(START, "chatbot")

    # The chatbot will always go to the human next.
    graph_builder.add_edge("chatbot", "human");


    graph_builder.add_conditional_edges("human", maybe_exit_human_node)

    chat_with_human_graph = graph_builder.compile()

    Image(chat_with_human_graph.get_graph().draw_mermaid_png())


    graph_builder = StateGraph(OrderState)

    # Add the nodes, including the new tool_node.
    graph_builder.add_node("chatbot", chatbot_with_tools)
    graph_builder.add_node("human", human_node)
    graph_builder.add_node("tools", tool_node)

    # Chatbot may go to tools, or human.
    graph_builder.add_conditional_edges("chatbot", maybe_route_to_tools)
    # Human may go back to chatbot, or exit.
    graph_builder.add_conditional_edges("human", maybe_exit_human_node)

    # Tools always route back to chat afterwards.
    graph_builder.add_edge("tools", "chatbot")

    graph_builder.add_edge(START, "chatbot")
    graph_with_menu = graph_builder.compile()

    Image(graph_with_menu.get_graph().draw_mermaid_png())


    # Auto-tools will be invoked automatically by the ToolNode
    auto_tools = [get_menu]
    tool_node = ToolNode(auto_tools)

    # Order-tools will be handled by the order node.
    order_tools = [add_to_order, confirm_order, get_order, clear_order, place_order]

    # The LLM needs to know about all of the tools, so specify everything here.
    llm_with_tools = llm.bind_tools(auto_tools + order_tools)


    graph_builder = StateGraph(OrderState)

    # Nodes
    graph_builder.add_node("chatbot", chatbot_with_tools)
    graph_builder.add_node("human", human_node)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_node("ordering", order_node)

    # Chatbot -> {ordering, tools, human, END}
    graph_builder.add_conditional_edges("chatbot", maybe_route_to_tools)
    # Human -> {chatbot, END}
    graph_builder.add_conditional_edges("human", maybe_exit_human_node)

    # Tools (both kinds) always route back to chat afterwards.
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge("ordering", "chatbot")

    graph_builder.add_edge(START, "chatbot")
    graph_with_order_tools = graph_builder.compile()

    Image(graph_with_order_tools.get_graph().draw_mermaid_png())
