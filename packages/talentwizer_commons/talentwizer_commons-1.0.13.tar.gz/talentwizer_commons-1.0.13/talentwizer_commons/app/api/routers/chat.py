from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.core.llms import ChatMessage
from llama_index.core.llms import MessageRole
from pydantic import BaseModel

from talentwizer_commons.app.engine import get_chat_engine

# Create an instance of APIRouter to handle chat-related routes
chat_router = r = APIRouter()

# Define a Pydantic model for Message data
class _Message(BaseModel):
    """
    The message data consisting of the role and content of the message.
    role: The role of the message. For eg. USER or SYSTEM.
    """
    role: MessageRole
    content: str

# Define a Pydantic model for ChatData
class _ChatData(BaseModel):
    messages: List[_Message]

# Endpoint to handle chat requests
@r.post("")
async def chat(
    request: Request,
    data: _ChatData,
    chat_engine: BaseChatEngine = Depends(get_chat_engine),
):
    """
    Send messages and receive chat responses in a streaming manner.

    :param request: Incoming request.
    :type request: Request
    :param data: Data containing messages to be sent.
    :type data: _ChatData
    :param chat_engine: Chat engine dependency.
    :type chat_engine: BaseChatEngine
    :raises HTTPException 400: If no messages provided or if last message is not from user.
    :return: Streaming response containing chat responses.
    :rtype: StreamingResponse
    """
    # check preconditions and get last message
    if len(data.messages) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided",
        )
    lastMessage = data.messages.pop()
    if lastMessage.role != MessageRole.USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Last message must be from user",
        )
    # convert messages coming from the request to type ChatMessage
    messages = [
        ChatMessage(
            role=m.role,
            content=m.content,
        )
        for m in data.messages
    ]

    prompt = lastMessage.content 

    # query chat engine
    response = await chat_engine.astream_chat(prompt, messages)
    
    # stream response
    async def event_generator():
        # print(str(response.async_response_gen()))
        async for token in response.async_response_gen():
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break
            yield token

    return StreamingResponse(event_generator(), media_type="text/plain")
