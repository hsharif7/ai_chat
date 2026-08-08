from fastapi import APIRouter, Cookie, Response, HTTPException, Depends
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
from dotenv import load_dotenv
from database.db import db
import os

router_refresh = APIRouter()
router_get_user = APIRouter()

load_dotenv()
key = os.getenv("TOKEN_KEY")
algo = "HS256"

@router_refresh.get("/refresh")
def refresh(refresh_token : str = Cookie(None)):
    try:
        now = datetime.now(timezone.utc)
        payload = jwt.decode(refresh_token, key=key, algorithms=[algo])
        payload = {
            "sub": payload["sub"],
            "exp": now + timedelta(minutes=30),
        }
        access_token = jwt.encode(
            payload,
            key,
            algorithm=algo,
        )
        response = Response(status_code= 200)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True
        )
        return response
    except JWTError:
        return Response(status_code= 401)
@router_get_user.get("/user")
def get_current_user(access_token : str = Cookie(None), conn = Depends(db)):
    if access_token is None: return None
    try:
        payload =jwt.decode(access_token, key=key, algorithms=[algo])
        user_id = payload["sub"]
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        if row:
            return  user_id
        else:
            raise HTTPException(status_code=401, detail="User not found")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
