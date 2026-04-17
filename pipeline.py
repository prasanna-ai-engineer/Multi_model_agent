from agent import build_search_agent , build_reader_agent,  report_writing_chain, report_reviewer_chain
from rich import print

def run_research_pipeline(topic: str ) -> dict:
    state = {}

    ##  build Search agent is working
    print("\n"+ "="*50)
    print("step 1 - search agent is working.")
    print("="*50)


    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_result"] = search_result["messages"][-1].content

    print("\n search result ",state['search_result'])

    ## Step 2 -- scraper agent
    print("\n"+ "="*50)
    print("step 2 - scraping the data from the sites")
    print("="*50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages":[(
            "user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_result'][:800]}")
        ]
    })

    state["scraped_data"] = reader_result["messages"][-1].content

    print("\n scraped data \n", state["scraped_data"])

    ### step 3 writer chain 
    print("\n"+ "="*50)
    print("step 2 - creating the report out of the scraped data")
    print("="*50)

    research_combined = (
        f"searched result \n {state['search_result']} ",
        f"scraped data \n {state["scraped_data"]}"
    )

    state["generated_report"] = report_writing_chain.invoke({
        "topic": topic,
        "research" : research_combined
    })

    print("\n final report \n", state["generated_report"])

    ## Step 4 report reviewing and rating 

    print("\n"+ "="*50)
    print("step 4 - reviewing the report and rating it out of 10")
    print("="*50)

    state["feedback"] = report_reviewer_chain.invoke({
        "report" : state["generated_report"]
    })

    print("\n feedback \n", state["feedback"])

    return state


if __name__ == "__main__":
    topic = input("\n please type in the topic you want to research on : ")
    run_research_pipeline(topic=topic)

























