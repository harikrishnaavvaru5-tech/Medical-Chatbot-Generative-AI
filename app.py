from flask import Flask, render_template, request
from src.helper import download_hugging_face_embeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.prompt import *
from google import genai
import os

app = Flask(__name__)

load_dotenv()

GOOGLE_API_KEY=os.environ.get('GOOGLE_API_KEY')

embeddings = download_hugging_face_embeddings()

# Load FAISS index from local storage
docsearch = FAISS.load_local("medical_docs_faiss_index", embeddings,  allow_dangerous_deserialization=True)

retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k":3})

# Initialize Google GenAI client
client = genai.Client(api_key=GOOGLE_API_KEY)

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)


@app.route("/")
def index():
    return render_template('chat.html')


@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    print(input)
    
    # Retrieve relevant documents
    relevant_docs = retriever.invoke(input)
    context = "\n".join([doc.page_content for doc in relevant_docs])
    
    # Create prompt with context
    full_prompt = f"{system_prompt}\n\nContext: {context}\n\nQuestion: {input}"
    
    # Generate response using Google GenAI
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt
    )
    
    print("Response : ", response.text)
    return str(response.text)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port= 8080, debug= True)