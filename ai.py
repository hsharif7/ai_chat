from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.signup import router as signup
from auth.login import router as login
from auth.tokens import router_get_user as user
from auth.tokens import router_refresh as refresh
from services.chats import router_display_chats as chats
from services.chats import router_load_messages as load
from services.chats import router_llm_title as title
from services.chats import router_new_chat as new
from services.chats import router_delete_chat as delete
from services.chats import router_rename_chat as rename
from services.llm import router as llm
from dotenv import load_dotenv
import os
load_dotenv()
url = os.getenv("FRONTEND_URL")
ai = FastAPI()
ai.include_router(signup)
ai.include_router(login)
ai.include_router(user)
ai.include_router(refresh)
ai.include_router(chats)
ai.include_router(load)
ai.include_router(title)
ai.include_router(new)
ai.include_router(delete)
ai.include_router(rename)
ai.include_router(llm)

ai.add_middleware(
    CORSMiddleware,
    allow_origins=[url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
