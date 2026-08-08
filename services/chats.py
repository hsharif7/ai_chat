from auth.tokens import get_current_user
from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from database.db import db
from models.model import RenameChat, UserInput
from groq import Groq
import os
router_display_chats = APIRouter()
router_new_chat = APIRouter()
router_load_messages = APIRouter()
router_llm_title = APIRouter()
router_rename_chat = APIRouter()
router_delete_chat = APIRouter()

def get_chat_id(chat_id: int | None = None , mess:UserInput | None = None, user_id: int = Depends(get_current_user) , conn = Depends(db)):
    if user_id:
        if chat_id:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chats WHERE user_id = %s AND id = %s", (user_id, chat_id))
            row = cursor.fetchone()
            if row:
                return chat_id
            else:
                raise HTTPException(status_code=401, detail="Chat not found")
        else:
            return create_new_chat(prompt=mess ,user_id=user_id ,conn=conn)
    else:
        return None
@router_new_chat.get("/new")
def create_new_chat(prompt:UserInput, user_id: int =Depends(get_current_user), conn = Depends(db)):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chats (title, user_id) VALUES (%s,%s) RETURNING id", (prompt.text, user_id))
    chat_id = cursor.fetchone()[0]
    conn.commit()
    return chat_id

@router_load_messages.get("/load")
def load_messages(chat_id:int = Depends(get_chat_id), conn = Depends(db)):
    print(chat_id, type(chat_id))
    messages = []
    cursor = conn.cursor()
    cursor.execute("SELECT (content) FROM messages WHERE chat_id = %s", (chat_id,))
    rows = cursor.fetchall()
    for row in rows:
        messages.append(row[0])

    return JSONResponse(messages)

@router_llm_title.post("/new/title")
async def llm_title(response:str, conn = Depends(db), chat_id = Depends(get_chat_id)):
    try:
        mes = []
        mes.append({"role": "user", "content": response})
        mes.append({"role": "user", "content":
            "generate a title suitable for the text above, your response should be no extra words but the title only"})
        client = Groq(api_key=os.getenv("API_KEY"))
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=mes,
            stream=False
        )
        response = completion.choices[0].message.content
        cursor = conn.cursor()
        cursor.execute("UPDATE chats SET title  = %s WHERE id = %s", (response, chat_id))
        conn.commit()
    except Exception:
        pass
@router_display_chats.get("/chats")
def display_chats(user_id: int = Depends(get_current_user), conn = Depends(db)):

    if user_id:
        chats = []
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM chats  WHERE user_id = %s", (user_id,))
        rows = cursor.fetchall()
        for row in rows:
            chats.append({"id": row[0], "title": row[1]})

        return JSONResponse(chats)

    else:
        return None

@router_rename_chat.post("/rename")
def rename_chat(new_name: RenameChat, chat_id: int = Depends(get_chat_id), conn = Depends(db)):
    cursor = conn.cursor()
    cursor.execute("UPDATE chats SET title  = %s WHERE id = %s", (new_name.text, chat_id))
    conn.commit()

@router_delete_chat.delete("/delete")
def delete_chat(chat_id: int = Depends(get_chat_id), conn = Depends(db)):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE chat_id = %s", (chat_id,))
    cursor.execute("DELETE FROM chats WHERE id = %s", (chat_id,))
    conn.commit()
