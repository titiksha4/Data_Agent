from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool

#Checking if LLM is working correctly 
#response = llm.invoke("What is Data Engineering")
#print(response)

class response(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

load_dotenv()
llm = ChatOpenAI(model = "gpt-4", streaming=False)
parser = PydanticOutputParser(pydantic_object = response)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a master of data. The user relies on you to explain and clarify topics related to data.
            Answer the user query and use neccessary tools. 
            Wrap the output in this format and provide no other text\n{format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [search_tool]
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
query = input("What can i help you with?")
raw_response = agent_executor.invoke({"query": query})

try:
    structured_response = parser.parse(raw_response.get("output")[0]["text"])
    print(structured_response)
except Exception as e:
    print("Error parsing response", e, "Raw Response - ", raw_response)
