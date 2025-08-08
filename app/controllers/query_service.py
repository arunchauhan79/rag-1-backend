
from typing import List
from schema import ChatHistoryCreate,ChatHistoryResponse, ChatMessage ,QueryResponse 
from fastapi import HTTPException
from db import get_database
from core import DatabaseConnectionException, BadRequestException, settings
from pymongo.asynchronous.database import AsyncDatabase
from datetime import datetime, timezone
from utils import  get_vectorstore
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, BaseMessage







async def query_doc(search:str, orgId:str, db:AsyncDatabase):
    try:
        print("query_doc")
        session_id = "sess_123"
        filter_dict = {}
      # Step 1: Get similar documents
        vector_store = get_vectorstore()
        # results = vector_store.similarity_search(query=search, filter={"orgId": orgId})
        if orgId:
            # Search in organization
            filter_dict = {"orgId": orgId}
            
            
        if filter_dict:    
            retriever = vector_store.as_retriever(
                search_kwargs={
                    "k": 2,
                    "filter": filter_dict
                }
            )
        else:
            retriever = vector_store.as_retriever(
                search_kwargs={
                    "k": 2,                   
                }
            )
            
        results = retriever.invoke(search)   
        context = "\n\n".join([doc.page_content for doc in results])
        #chat_history = await get_chat_history(session_id)
       
        # Step 3: Build prompt with chat history
        chat_template = ChatPromptTemplate.from_messages([
            ('system', 'You are a helpful assistant.'),
           # MessagesPlaceholder(variable_name='chat_history'),
            ('human', 'Given the following context, please answer the question from given context only. If context is insufficient then say i do not know \n\nContext:\n{context}\n\nQuestion: {question}')
        ])
        prompt = chat_template.invoke({
            'question': search,
            'context': context,
            #'chat_history': chat_history
        })

        # Step 4: Invoke the model
        llm = ChatOpenAI(model_name="o4-mini", api_key=settings.OPENAI_API_KEY)
        response = llm.invoke(prompt)

        # Step 5: Append to chat_history
        # chat_history.append(HumanMessage(content=search))
        # chat_history.append(AIMessage(content=response.content))

        # # Step 6: Save chat history to DB
        # doc_to_save = ChatHistoryCreate(
        #     sessionId="sess_123",
        #     userId="user_001",
        #     orgId="org_001",
        #     messages=[
        #         ChatMessage(
        #             role="user",
        #             message=search,
        #             timestamp=datetime.now(timezone.utc)
        #         ),
        #         ChatMessage(
        #             role="ai",
        #             message=response.content,
        #             timestamp=datetime.now(timezone.utc)
        #         )
        #     ],
        #     isActive=True
        # )

        # save_chat_response = await save_chat_history(doc_to_save)

        # Step 7: Return response
        print("llm response",response.content)
        return QueryResponse(
            query = search,
            answer = response.content
        )
        
    except Exception as e:
        raise BadRequestException(f"Error in fetching data for query {e}")

async def save_chat_history(payload:ChatHistoryCreate) -> ChatHistoryResponse:
    try:
        db = get_database()
        if db is None:
            raise DatabaseConnectionException(f"Database not connected")
        now = datetime.now(timezone.utc)
        result = await db.chatHistory.find_one_and_update(
            {"sessionId": payload.sessionId},
                {
                "$push": {
                    "messages": {
                        "$each": [msg.dict() for msg in payload.messages]  # ✅ Each dict is pushed individually
                    },
                },
                "$setOnInsert": {
                    "userId": payload.userId,
                    "orgId": payload.orgId,
                    "isActive":payload.isActive,
                    "createdAt": now
                },
                "$set": {   
                    "updatedAt": now
                }
            },
            upsert=True,
            return_document=True
        )

        # doc = await db.chatHistory.find_one({"sessionId": payload.sessionId})
        
        # history = ChatHistoryResponse.model_validate({**doc, "id": str(doc["_id"])}),
        # return ChatHistoryResponse(
        #     sessionId=doc["sessionId"],
        #     userId=doc["userId"],
        #     orgId=doc["orgId"],
        #     messages=[ChatMessage(**msg) for msg in doc["messages"]],
        #     createdAt=doc["createdAt"],
        #     updatedAt=doc["updatedAt"]
        # )
    except Exception as e:  
        raise HTTPException(status_code=500,detail=f"Failed to save user chat history: {e}",)
    

async def get_chat_history(session_id: str) -> List[BaseMessage]:
    db = get_database()
    doc = await db.chatHistory.find_one({"sessionId": session_id})
    
    messages = []
    if doc and "messages" in doc:
        for msg in doc["messages"]:
            if msg["role"] in ("user", "human"):
                messages.append(HumanMessage(content=msg["message"]))
            elif msg["role"] in ("ai", "assistant"):
                messages.append(AIMessage(content=msg["message"]))
    return messages