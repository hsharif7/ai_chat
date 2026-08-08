from database.save import save
from fastapi import APIRouter, Depends
from models.model import UserInput
from fastapi.responses import StreamingResponse
from groq import Groq
from services.streaming import stream
from dotenv import load_dotenv
from services.chats import get_chat_id
from database.db import db
import os

router = APIRouter()

load_dotenv()
client = Groq(api_key=os.getenv("API_KEY"))

@router.post('/ai')
def chat(mess: UserInput, chat_id: int =Depends(get_chat_id), conn = Depends(db)):
    mes = []
    if chat_id:
        logged_in = True
    else:
        logged_in = False
    if logged_in:
        mes.clear()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM messages WHERE chat_id = %s",
            (chat_id,)
        )
        for role, content in cursor.fetchall():
            mes.append({"role": role, "content": content })
        mes.append({"role": "user", "content": mess.text})
        save("user", mess.text, chat_id)
    else:
        mes = mess.links
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=mes,
        stream = True
    )

    response = StreamingResponse(stream(completion, chat_id,logged_in), media_type = "text/plain")
    return response