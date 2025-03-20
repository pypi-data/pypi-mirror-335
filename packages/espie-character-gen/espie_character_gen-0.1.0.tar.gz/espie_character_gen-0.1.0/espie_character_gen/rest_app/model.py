from pydantic import BaseModel


class AppSession(BaseModel):
    username: str
