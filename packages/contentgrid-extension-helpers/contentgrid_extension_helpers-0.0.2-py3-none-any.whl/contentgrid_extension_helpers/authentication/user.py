from pydantic import BaseModel

class ContentGridUser(BaseModel):
    sub: str
    iss: str
    exp: float
    name: str | None = None
    email: str | None = None
    access_token: str