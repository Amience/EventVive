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
def TelecomFuture(query: str) -> str:
    """This function can search through the transcript of the event and get most relevant facts, opinions, people, \
    and or Q&A from the audience"""

    # Load existing vector database
    embedding = OpenAIEmbeddings()
    persist_directory_subpart = 'docs/chroma/telecomfuture/'
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
def TelecomFuture_create_summary(query: str) -> str:
    """This function answers questions that are generic about the event, such as summary, overall overview of
    technologies, concepts, people, or ideas that are not specific but cover the wider scope of the event."""

    PROMPT_TEMPLATE = ("""Answer the query below using information delimited between ### characters below. 

Query: 
{query}

Event Summary:
###
In Dr Hayaatun Sillem's panel with Erikson (Dr Mallikarjun Tatipamula), University of Bristol \
(Prof. Dimitra Simeonidou), and Microsoft (Dr David Parker) experts, telecom's evolution to 6G with \
AI, quantum tech, augmented/virtual reality, and IoT is explored. Challenges like scaling innovation, workforce \
skills, and security are discussed. The UK's telecom role is assessed, focusing on policy and research strengths, \
and vendor gaps. Telecom's societal impact, the need for resilient, sustainable networks, and international \
collaboration are emphasised. Discussed are hollow fiber technology, UK's 6G strategy, Wireless Infrastructure \
Strategy, optical transponders, integrated space, air, and ground networks, university spin-outs, terrestrial \
and non-terrestrial network integration, quantum cloud services, supply chain diversification, Azure fiber, and \
telecom's role as a utility, its impact on digital transformation in industries, and nonlinearity in hollow fiber.
    
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

    llm = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0)
    chain = LLMChain(llm=llm, prompt=PROMPT)
    summary = chain.run(query)

    if not summary:
        return "No good summary was found"

    return f'Summary: {summary}'


@tool
def TelecomFuture_summarise_presenters(query: str) -> str:
    """This function answers questions that are specifically about the presenters of the event, and people \
    in the panel"""

    PROMPT_TEMPLATE = ("""Answer the query below using information delimited between ### characters below. 

Query: 
{query}

Context:
###
Dr Hayaatun Sillem:
Dr Hayaatun Sillem, she is the CEO at the Royal Academy of Engineering and the Queen Elizabeth Prize for Engineering Foundation. \
She hosts online chats to explore topical issues that are important for engineering and society. The overarching \
goal of the Royal Academy of Engineering is to harness the power of engineering to build a sustainable society \
and an inclusive economy. Hayaatun has been exploring critical technologies such as Quantum Technologies, semiconductors, \
engineering biology, artificial intelligence, and future telecoms through a miniseries of critical conversations.

Dr Mallikarjun Tatipamula:
Dr Mallikarjun Tatipamula is an Academy fellow and the Chief Technology Officer at Erikson. He has over 33 years of experience \
in telecommunications, starting from the 2G era. His current focus is on 5G technology development. He believes \
that 5G will enhance mobile broadband experiences, enabling immersive experiences for users with applications such \
as augmented reality and virtual reality. Additionally, he sees 5G as a key driver of digital transformation across \
various industries, including manufacturing, utilities, smart cities, and transportation, due to its high speed, \
low latency, and high capacity connectivity.

Professor Dimitra Simeonidou:
Professor Dimitra Simeonidou is an Academy Fellow and a professor of high performance networks at the University of \
Bristol. She leads a large research center with about 200 academics and researchers working across a number of \
technologies, including IoT, wireless, optical, cloud physical infrastructure, and cloud services. As a researcher, \
she identifies himself as a systems person, focusing on network architectures and end-to-end network performance \
optimization. She is particularly interested in smart infrastructure, smart cities, and 5G and 6G environments. \
She believes that connectivity is a utility on par with water and electricity, and is crucial for driving digital \
transformation in society and businesses. Her work aims to design future telecom systems that are resilient, \
inclusive, fair, and available to all.

Dr David Parker:
Dr David Parker is an Academy fellow, co-founder and former CEO of Luminosity, a company specializing in hollow \
fiber technology that was acquired by Microsoft in December last year. He is now part of the leadership team for \
Azure fiber. His work focuses on developing optical technologies, including new types of fiber optic cables, to \
enhance the performance of the core network infrastructure that underpins the internet. His recent work on hollow \
core fiber technology has the potential to revolutionize the telecommunications industry by providing faster data \
transmission speeds and lower latency.
###
    """)
    PROMPT = PromptTemplate(
        input_variables=["query"], template=PROMPT_TEMPLATE
    )

    llm = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0)
    chain = LLMChain(llm=llm, prompt=PROMPT)
    summary = chain.run(query)

    if not summary:
        return "No good summary was found"

    return f'Summary: {summary}'



@tool
def GreenReport2023(query: str) -> str:
    """This function can search through the transcript of the event and get most relevant facts, opinions, people"""

    # Load existing vector database
    embedding = OpenAIEmbeddings()
    persist_directory_subpart = 'docs/chroma/GreenReport2023/'
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
def GreenReport2023_create_summary(query: str) -> str:
    """This function answers questions that are generic about the event, such as summary, overall overview of
    technologies, concepts, people, or ideas that are not specific but cover the wider scope of the event."""

    PROMPT_TEMPLATE = ("""Answer the query below using information delimited between ### characters below. 

Query: 
{query}

Event Summary:
###
Greener by Design Annual Report 2022-2023 - Royal Aeronautical Society

The Royal Aeronautical Society's comprehensive report on aerospace's strides towards environmental \
sustainability encompasses a broad range of pivotal topics, highlighted by an assembly of experts in \
various facets of the field.

Climate Urgency and Aviation's Environmental Challenge:
The report kicks off by echoing the World Meteorological Organization's alarming prediction: a 66% likelihood \
of global temperatures surpassing the critical 1.5C mark above pre-industrial levels in the next few years.
Aviation’s struggle with decarbonization is a core focus. The sector, recognized as challenging to decarbonize, \
grapples with reducing CO2 emissions and the costly transition towards greener alternatives.

Sustainable Aviation Fuel (SAF):
SAF emerges as a promising solution, poised to significantly enhance fuel efficiency. Despite potential benefits, \
the report highlights challenges in SAF production and utilization, stressing the need for efficient and sustainable \
methods that don’t compromise food production.

Advancements in Aircraft Technologies:
The document delves into the evolution of electric and hybrid aircraft, underscoring the progress and challenges \
in extending their range and seating capacities.
Hydrogen fuel cell hybrid electric aircraft are spotlighted, discussing their feasibility, challenges, and recent \
breakthroughs, including several inaugural flights and ongoing developments.

Virtual Interlining in Airlines:
The innovative concept of virtual interlining marks a significant shift in airline operations. This trend, driven \
by cost-effectiveness, involves passengers booking connecting flights between airlines without formal agreements, \
highlighting a new approach to travel logistics.

Carbon Budgets and the Net Zero Challenge:
The report discusses the importance of meeting interim carbon reduction targets on the pathway to achieving Net \
Zero by 2050. It proposes various operational and technological strategies, emphasizing the need for effective \
policy measures alongside technological innovations.

Contrail Management:
A significant portion of the report is dedicated to the science behind contrails and their environmental impact. \
The discussion revolves around the formation, impact, and potential strategies to mitigate contrails, emphasizing \
their significant contribution to atmospheric warming.

Non-CO2 Climate Effects:
Non-CO2 effects on climate change, often overshadowed by CO2 emissions, receive substantial attention. \
The report explores various research findings, technological advancements, and policy implications concerning \
non-CO2 emissions.

Collaborative Efforts and Future Outlook:
The report concludes with a focus on the Greener by Design Group's objectives and activities. It highlights the \
group's role in researching, assessing, and advising on aviation's environmental impact, promoting best practices, \
and fostering a balanced understanding of the sector's environmental programs.

In essence, the "Greener by Design" Annual Report for 2022-2023 presents a multi-faceted view of the aerospace \
industry’s environmental challenges and advancements. It serves as a repository of current knowledge, strategies, \
and future directions in the journey towards sustainable aviation.
###
    """)
    PROMPT = PromptTemplate(
        input_variables=["query"], template=PROMPT_TEMPLATE
    )

    llm = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0)
    chain = LLMChain(llm=llm, prompt=PROMPT)
    summary = chain.run(query)

    if not summary:
        return "No good summary was found"

    return f'Summary: {summary}'