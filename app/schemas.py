from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    username: str
    mot_de_passe: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    nom: str
    role: str
