from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
from langchain_core.output_parsers import StrOutputParser
from tools import web_scrape, web_search
from dotenv import load_dotenv

load_dotenv()

    

model = ChatGoogleGenerativeAI(model= "gemini-3-flash-preview")
parser = StrOutputParser()


def build_search_agent ():
    return create_agent(
        model= model ,
        tools= [web_search]
    )

def build_reader_agent():
    return create_agent(
        model = model,
        tools= [web_scrape]
    )



report_writer_prompt = ChatPromptTemplate.from_messages(
        [
        ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
        ("human", """Write a detailed research report on the topic below.

        Topic: {topic}

        Research Gathered:
        {research}

        Structure the report as:
        - Introduction
        - Key Findings (minimum 3 well-explained points)
        - Conclusion
        - Sources (list all URLs found in the research)

        Be detailed, factual and professional.""")
        ])
    
report_writing_chain =report_writer_prompt | model | parser

report_reviewer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific." ),
    ("human", """Review the research report below and evaluate it strictly.
    Report:
    {report}

    Respond in this exact format:

    Score: X/10

    Strengths:
    - ...
    - ...

    Areas to Improve:
    - ...
    - ...

    One line verdict:
    ..."""),
])

report_reviewer_chain = report_reviewer_prompt| model | parser

