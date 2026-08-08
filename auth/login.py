from fastapi import APIRouter, Depends
from models.model import Login
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi.responses import JSONResponse
from jose import jwt
from dotenv import load_dotenv
from database.db import db
import os
router = APIRouter()

load_dotenv()
key = os.getenv("TOKEN_KEY")
algo = "HS256"
hashp = CryptContext(
    schemes = ["bcrypt"]
        )
@router.post("/login")
def login(data:Login, conn = Depends(db)):
    now = datetime.now(timezone.utc)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM users
    WHERE email = %s
    """,
                   (data.email,)
    )

    row = cursor.fetchone()
    if row is None:
        response = JSONResponse(
            {"status": False, "message": "Please create your account first"}
        )
        return response
    else:
        if hashp.verify(data.password, row[3]):

            response = JSONResponse({"status": True})

            payload = {
                "sub": str(row[0]),
                "exp": now + timedelta(days=30),
            }
            refresh_token = jwt.encode(
                payload,
                key,
                algorithm=algo,
            )
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True
            )
            payload = {
                "sub": str(row[0]),
                "exp": now + timedelta(minutes=30),
            }
            access_token = jwt.encode(
                payload,
                key,
                algorithm=algo,
            )

            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True
            )

            return response
        else:
            return JSONResponse({"status": False, "message": "Incorrect password"})
