from pydantic import BaseModel

class UserInput(BaseModel):
    text: str
    links: list[dict] | None = None

class Login(BaseModel):
    email: str
    password: str

class SignUp(BaseModel):
    name: str
    email: str
    password: str

class RenameChat(BaseModel):
    text: str
