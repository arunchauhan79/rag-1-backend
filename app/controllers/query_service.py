
from typing import List
from schema import ChatHistoryCreate,ChatHistoryResponse, ChatMessage ,QueryResponse, SearchBase 
from fastapi import HTTPException
from db import get_database
from core import DatabaseConnectionException, BadRequestException, settings
from pymongo.asynchronous.database import AsyncDatabase
from datetime import datetime, timezone
from utils import  get_vectorstore
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, BaseMessage







async def query_doc(search_text: str, org_id: str, db: AsyncDatabase):
    """
    Query documents using RAG pipeline with organization filtering.
    
    Args:
        search_text: The user's search query
        org_id: Organization ID for filtering
        db: Database connection
        
    Returns:
        QueryResponse containing the response and metadata
    """
    try:
        print(f"Processing query: '{search_text}' for organization: {org_id}")
        
        # Get vectorstore and create retriever with org filter
        vector_store = get_vectorstore()
        retriever = vector_store.as_retriever(
            search_kwargs={
                "k": 5,
                "filter": {"orgId": org_id}  # Filter by organization
            }
        )
        
        # Retrieve relevant documents
        docs = retriever.invoke(search_text)
        
        if not docs:
            print(f"No documents found for query: '{search_text}' in organization: {org_id}")
            return QueryResponse(
                query=search_text,
                answer="I couldn't find any relevant information in your documents for this query.",
                document_ids=[],
                confidence=0.0
            )
        
        # Prepare context from retrieved documents and collect document IDs
        context_parts = []
        document_ids = []
        
        for doc in docs:
            context_parts.append(doc.page_content)
            
            # Extract only document ID from metadata (sources removed)
            doc_id = doc.metadata.get('documentId')
            if doc_id and doc_id not in document_ids:
                document_ids.append(doc_id)
                
            print(f"Retrieved chunk metadata: {doc.metadata}")
        
        context = "\n\n".join(context_parts)
        
        # Step 3: Build prompt with context
        chat_template = ChatPromptTemplate.from_messages([
            ('system', 'You are a helpful assistant.'),
            ('human', 'Given the following context, please answer the question from given context only. If context is insufficient then say I do not know \n\nContext:\n{context}\n\nQuestion: {question}')
        ])
        
        prompt = chat_template.invoke({
            'question': search_text,
            'context': context,
        })

        # Step 4: Invoke the model
        llm = ChatOpenAI(model_name="gpt-4o-mini", api_key=settings.OPENAI_API_KEY)
        response = llm.invoke(prompt)

        print(f"Generated response for query: '{search_text}' using {len(document_ids)} documents")
        print("LLM response:", response.content)
        
        return QueryResponse(
            query=search_text,
            answer=response.content,
            document_ids=document_ids,  # Include document IDs in response
            confidence=min(len(docs) * 0.2, 1.0)  # Simple confidence scoring
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