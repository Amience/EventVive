from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
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
def agent_cs25_e(query: str) -> str:
    """This function can search part-E subsection of CS25 aircraft certification document and retrieve \
    most relevant regulations based on the user query"""

    # Load existing vector database
    embedding = OpenAIEmbeddings()
    persist_directory_subpart = 'docs/chroma/CS25_subpart_E_curated/'
    vectordb_subpartE = Chroma(
        persist_directory=persist_directory_subpart,
        embedding_function=embedding
    )

    retriever = vectordb_subpartE.as_retriever(search_type="mmr", search_kwargs={'k': 4, 'fetch_k': 10})
    relevant_documents = retriever.get_relevant_documents(query)
    summaries = []
    document_dicts = []
    for doc in relevant_documents:
        # Extract the content and source
        doc_content = doc.page_content
        doc_source = doc.metadata['source']
        # Create a dictionary for the current document
        doc_dict = {
            'content': doc_content,
            'source': doc_source
        }
        # Append the dictionary to the list
        document_dicts.append(doc_dict)

        summaries.append(f"Summary: {doc_content}\nSource: {doc_source}")
    if not summaries:
        return "No good CS25 regulation was found"

    return "\n\n".join(summaries)


@tool
def search_wikipedia(query: str, self=None) -> str:
    """Run Wikipedia search and get page summaries."""
    page_titles = wikipedia.search(query)
    summaries = []
    for page_title in page_titles[: 3]:
        try:
            wiki_page = wikipedia.page(title=page_title, auto_suggest=False)
            summaries.append(f"Page: {page_title}\nSummary: {wiki_page.summary}")
        except (
            self.wiki_client.exceptions.PageError,
            self.wiki_client.exceptions.DisambiguationError,
        ):
            pass
    if not summaries:
        return "No good Wikipedia Search Result was found"
    return "\n\n".join(summaries)


@tool
def create_summary(conversation_history: str) -> str:
    """This function can create a summary of the conversation based on conversation history"""
    # conversation_history = st.session_state.entity_memory.entity_store
    print(conversation_history)
    summary = '''You are an aerospace engineer concerned with certifying an aircraft. Communicate this summary in \
    a technical language, be concise.'''
    if not summary:
        return "No good summary was found"

    return f'Use the following persona for the summary: {summary}'
