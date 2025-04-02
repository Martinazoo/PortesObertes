from fastapi import FastAPI
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select
import time


app = FastAPI()


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

class User(SQLModel, table=True):
    uuid: str = Field(primary_key=True)
    username: str|None

@app.post("/uuid_save")
async def get_uuid(uuid_data: str):
    print(uuid_data)
        
@app.get("/")
async def get_root():
    print("Hello World")

