from fastapi import APIRouter, Response, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
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
def refresh(authorization : str = Header(None)):
    refresh_token = authorization.replace("Bearer ", "")
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

        return JSONResponse({"access_token": access_token})
    except JWTError:
        return Response(status_code= 401)
@router_get_user.get("/user")
def get_current_user(authorization : str = Header(None), conn = Depends(db)):
    if authorization is None: return None
    access_token = authorization.replace("Bearer ", "")
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
