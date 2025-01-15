from langchain_community.document_loaders import CSVLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import google.generativeai as genai


def create_rag_chain(csv_path: str, google_api_key: str, columns_to_use=None):
    """
    Creates a Retrieval-Augmented Generation (RAG) chain using a CSV file and Google API.
    Args:
        csv_path (str): The file path to the CSV document.
        google_api_key (str): The API key for accessing Google services.
        columns_to_use (list, optional): List of column names to include in the metadata. Defaults to None.
    Returns:
        rag_chain: A configured RAG chain for answering questions based on the CSV data.
    """

    # Configure Google API
    genai.configure(api_key=google_api_key)

    # 1. Load CSV documents
    loader = CSVLoader(
        file_path=csv_path,
        csv_args={"delimiter": ",", "quotechar": '"'},
        source_column="source"
        if columns_to_use is None
        else None,  # Automatically add source column
        metadata_columns=columns_to_use,  # Specify which columns to include in metadata
    )
    documents = loader.load()

    # 2. Transform CSV rows into meaningful text chunks
    def format_document(doc):
        # If specific columns were selected, use only those
        if columns_to_use:
            metadata = {k: doc.metadata[k] for k in columns_to_use if k in doc.metadata}
        else:
            metadata = doc.metadata

        # Create a formatted text representation of the CSV row
        formatted_text = "\n".join(
            [f"{key}: {value}" for key, value in metadata.items()]
        )
        doc.page_content = formatted_text
        return doc

    documents = [format_document(doc) for doc in documents]

    # 3. Create vector store with Google's embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001", google_api_key=google_api_key
    )

    vectorstore = Chroma.from_documents(documents=documents, embedding=embeddings)

    retriever = vectorstore.as_retriever(
        search_type="similarity", search_kwargs={"k": 10}
    )

    # 4. Create Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=google_api_key,
        temperature=0,
        convert_system_message_to_human=True,
    )

    # 5. Create prompt template
    template = """
    You are a polite Cocktail Advisor.
    Answer the question based only on the following context from the CSV data, 
    using all the data from the csv file you have: {context}
    
    Question: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    # 6. Create and return the RAG chain
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain
