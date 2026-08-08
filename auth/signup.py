from fastapi import APIRouter, Depends
from passlib.context import CryptContext
from models.model import SignUp
from database.db import db
router = APIRouter()

hashp = CryptContext(
    schemes = ["bcrypt"]
        )

@router.post("/signup")
def signup(data:SignUp, conn = Depends(db)):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM users
        WHERE email = %s
        """,
                   (data.email,)
                   )
    if cursor.fetchone() is None:
        cursor.execute("""
        INSERT INTO users (name, password, email) VALUES (%s,%s,%s)
        """,           (data.name, hashp.hash(data.password), data.email)
        )
        conn.commit()
        return {"status": True}
    else:
        return {"status" : False, "message" : "Your account already exists, Please log in"}

