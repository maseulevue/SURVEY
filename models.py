from sqlmodel import Field , SQLModel

class survey(SQLModel, table=True):
    id: int|None = Field(default=None, primary_key=True)
    Name: str
    Age: int
    Birthday: str
    Gender: str
    Email: str
    CN: str
    Work: str
    YE: str
    Achivement: str
    Address:str

class account(SQLModel, table=True):
    id: int|None = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    password_hash: str

class register(SQLModel):
    username: str
    password: str
    confirm: str

class login(SQLModel):
    username: str
    password: str
