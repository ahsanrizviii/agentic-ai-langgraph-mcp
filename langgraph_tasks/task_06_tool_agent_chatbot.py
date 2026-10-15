
from typing import TypedDict, Annotated
from datetime import datetime

import requests

from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool

from langchain_community.tools import (WikipediaQueryRun, YouTubeSearchTool, StackExchangeTool)

from langchain_community.utilities import (StackExchangeAPIWrapper, WikipediaAPIWrapper, StackExchangeAPIWrapper)

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


wikipedia_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

youtube_tool = YouTubeSearchTool()

stackexchange_tool = StackExchangeTool(api_wrapper=StackExchangeAPIWrapper())


@tool
def calculate_age(birth_year: int) -> str:
    """Calculate a person's age from their birth year."""

    current_year = datetime.now().year
    age = current_year - birth_year

    return f"The person is approximately {age} years old."


@tool
def get_weather(city: str) -> str:
    """Get the current weather of a city."""

    try:
        response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=10
        )

        data = response.json()

        if "results" not in data:
            return f"Could not find the city: {city}"

        location = data["results"][0]

        latitude = location["latitude"]
        longitude = location["longitude"]

        city_name = location["name"]
        country = location.get("country", "")

        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,wind_speed_10m",
                "timezone": "auto"
            },
            timeout=10
        )

        weather_data = weather_response.json()

        current = weather_data["current"]

        temperature = current["temperature_2m"]
        wind_speed = current["wind_speed_10m"]

        return (
            f"Weather in {city_name}, {country}: "
            f"{temperature}°C, "
            f"wind speed {wind_speed} km/h."
        )

    except Exception as e:
        return f"Weather tool error: {str(e)}"


tools = [wikipedia_tool, youtube_tool, stackexchange_tool, calculate_age, get_weather]


llm = ChatOllama(model="llama3.2")

llm_with_tools = llm.bind_tools(tools)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):

    messages = state["messages"]

    response = llm_with_tools.invoke(messages)

    return {"messages": [response]}


tool_node = ToolNode(tools)


graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")

graph.add_conditional_edges("chat_node", tools_condition)

graph.add_edge("tools", "chat_node")


app = graph.compile()

question = input("Ask something: ")

result = app.invoke({"messages": [HumanMessage(content=question)]})


print("\nFinal Answer:")
print("----------------")
print(result["messages"][-1].content)
