from langchain.chains import RetrievalQA, LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.tools import tool
import wikipedia
from langchain.vectorstores.chroma import Chroma
from pydantic import BaseModel, Field

@tool
def create_your_own(query: str) -> str:
    """This function can do whatever you would like once you fill it in """
    print(type(query))
    return query[::-1]


@tool
def eventvive(query: str) -> str:
    """This function can search through the transcript of the event and get most relevant facts, opinions, people, \
    and or Q&A from the audience"""

    # Load existing vector database
    embedding = OpenAIEmbeddings()
    persist_directory_subpart = 'docs/chroma_tacit/'
    vectordb_subpartE = Chroma(
        persist_directory=persist_directory_subpart,
        embedding_function=embedding
    )

    retriever = vectordb_subpartE.as_retriever(search_type="mmr", search_kwargs={'k': 5, 'fetch_k': 10})
    relevant_documents = retriever.get_relevant_documents(query)
    summaries = []
    for doc in relevant_documents:
        # Extract the content
        doc_content = doc.page_content
        summaries.append(f"Summary: {doc_content}")
    if not summaries:
        return "No good information was found"
    return "\n\n".join(summaries)


@tool
def create_summary(query: str) -> str:
    """This function answers questions that are generic about the event, such as summary, overall overview of
    technologies, concepts, people, or ideas that are not specific but cover the wider scope of the event."""

    PROMPT_TEMPLATE = ("""Answer the query below using information delimited between ### characters below. 

Query: 
{query}

Event Summary:
###
In Hayan Sim's panel with Erikson, University of Bristol, and Microsoft experts, telecom's evolution to 6G with \
AI, quantum tech, augmented/virtual reality, and IoT is explored. Challenges like scaling innovation, workforce \
skills, and security are discussed. The UK's telecom role is assessed, focusing on policy and research strengths, \
and vendor gaps. Telecom's societal impact, the need for resilient, sustainable networks, and international \
collaboration are emphasised. Discussed are holow fiber technology, UK's 6G strategy, Wireless Infrastructure \
Strategy, optical transponders, integrated space, air, and ground networks, university spin-outs, terrestrial \
and non-terrestrial network integration, quantum cloud services, supply chain diversification, Azure fiber, and \
telecom's role as a utility, its impact on digital transformation in industries, and nonlinearity in holow fiber.
    
Key points from the discussion include:

Evolution of Telecom Technologies: The conversation emphasized the transition from 2G to 5G and the upcoming shift \
towards 6G. This evolution is marked by increased connectivity and integration of advanced technologies like AI, \
quantum computing, and metamaterials.

Role of AI and Quantum Technologies: AI's role in network optimization and security was highlighted, along with the \
potential integration of quantum technologies in future telecom systems, especially for secure communications \
through Quantum Key Distribution (QKD).

Challenges in Telecom Development: Key challenges discussed include the need for energy-efficient telecom \
infrastructure in response to climate change, the necessity of developing a skilled workforce in modern telecom \
skills, and the importance of international collaboration in setting global telecom standards.

UK's Position in Global Telecom: The UK's strengths in university research, policy, and regulation in telecoms were \
recognized. However, the lack of large telecom vendors was seen as a weakness, alongside challenges in scaling up \
innovation and commercialization.

Impact on Society: The transformative impact of telecom technologies on various sectors like healthcare, manufacturing, \
and transportation was discussed. The importance of telecoms in driving digital transformation and its comparison to \
essential utilities like water and electricity was emphasized.

Resilience and Security: The panelists highlighted the importance of resilience and security in telecom networks, \
especially in the context of increasing threats and the need for sustainable, energy-efficient networks.

Commercialization and Innovation: The need for sustained investment, governmental support, and collaboration between \
academia, industry, and venture capital was discussed as vital for the UK's global competitiveness in telecom \
innovation.

Telecom as a Digital Transformation Driver: Improved connectivity and advanced telecom technologies are enabling \
significant shifts in business operations and service delivery across different sectors.

Barriers to Telecom Innovation: Technological challenges, policy, and regulatory hurdles, and the need for \
cross-sector collaboration were identified as barriers to innovation in the telecom sector.

Overall, the conversation provided a comprehensive overview of the current state and future prospects of \
telecommunications, highlighting its pivotal role in society, industry, and the broader global technology landscape.
###
    """)
    PROMPT = PromptTemplate(
        input_variables=["query"], template=PROMPT_TEMPLATE
    )

    llm = ChatOpenAI(model_name="gpt-4", temperature=0)
    chain = LLMChain(llm=llm, prompt=PROMPT)
    summary = chain.run(query)

    if not summary:
        return "No good summary was found"

    return f'Summary: {summary}'
