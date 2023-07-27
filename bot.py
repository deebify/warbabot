import os
import json
from botbuilder.core import TurnContext, ActivityHandler, ConversationState
from botbuilder.schema import ChannelAccount
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores.faiss import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import CharacterTextSplitter
from langchain import OpenAI, VectorDBQA
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyPDFLoader
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.document_loaders import TextLoader
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts.prompt import PromptTemplate
from langchain.callbacks import get_openai_callback


qa_template = """
        You are a helpful AI assistant named Q&A bot developed and created by Warba Bank Developers. The user gives you a file its content is represented by the following pieces of context, use them to answer the question at the end.
        If you don't know the answer, just say you don't know. Do NOT try to make up an answer.
        If the question is not related to the context, politely respond that you are tuned to only answer questions that are related to the context.
        Use as much detail as possible when responding.

        context: {context}
        =========
        question: {question}
        ======
        """
QA_PROMPT = PromptTemplate(template=qa_template, input_variables=["context","question"])

class MyBot(ActivityHandler):
    def __init__(self, conversation_state: ConversationState):
        self.conversation_state = conversation_state
        self.session_accessor = self.conversation_state.create_property("Session")

        loader = CSVLoader(file_path="data.csv", encoding="utf-8", csv_args={'delimiter': ','})
        data = loader.load()
        
        # Pass the OpenAI API key when initializing OpenAIEmbeddings
        embeddings = OpenAIEmbeddings(openai_api_key='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')
        
        vectors = FAISS.from_documents(data, embeddings)
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(temperature=0.0, model_name='gpt-3.5-turbo', openai_api_key='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'),
            retriever=vectors.as_retriever(), max_tokens_limit=4097, combine_docs_chain_kwargs={"prompt": QA_PROMPT}
        )


    def run_chain(self, chat_history, question):
        return self.chain.run({'chat_history': chat_history, 'question': question})
    
    

    async def get_response(self, user_message, turn_context: TurnContext):
    # Retrieve the session for the current user
        session = await self.session_accessor.get(turn_context, lambda: {"messages": [{"role": "system", "content": "You work for W Bank and answer any questions related to the bank."}]})

    # Add user message to the session
        session["messages"].append({"role": "user", "content": user_message})

        response = self.run_chain("", user_message)

        ai_response = response  # Use response directly

    # Add AI response to the session
        session["messages"].append({"role": "assistant", "content": ai_response})

        # Save the updated session
        await self.conversation_state.save_changes(turn_context)

        return ai_response


    async def on_message_activity(self, turn_context: TurnContext):
        user_message = turn_context.activity.text
        response_message = await self.get_response(user_message, turn_context)
        await turn_context.send_activity(response_message)

    async def on_members_added_activity(self, members_added: ChannelAccount, turn_context: TurnContext):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome to Warba Bank how can I help you?")


