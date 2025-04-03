from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Annotated
import bcrypt

import time


app = FastAPI()

class NFCUuid(BaseModel):
    uuid: str

class NFCId(BaseModel):
    uuid: str   
    email: str
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserDB(SQLModel, table=True):
    email: str = Field(primary_key=True, nullable=False)
    username: str = Field(nullable=False)
    password: str = Field(nullable=False)

class NFCDB(SQLModel, table=True):
    uuid: str = Field(primary_key=True, nullable=False)
    email: str = Field(foreign_key="userdb.email", nullable=True)

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    
loggedinuser = None

# if loggedinuser is none raise httpexception 422 

@app.post("/uuid_save")
async def get_uuid(uuid_data: NFCUuid, session: SessionDep):
    statement = select(NFCDB).where(NFCDB.uuid == uuid_data.uuid)
    res = session.exec(statement).first()
    if res is None:
        db_nfc = NFCDB(uuid=uuid_data.uuid, email=None)
        session.add(db_nfc)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail="The card exists assign it to a person") 
        
        
 #Modificar esta funcio   
@app.post("/register_nfc")   
async def register_nfc(email: NFCId, session: SessionDep):
    statement = select(UserDB).where(UserDB.email == email.email)
    user = session.exec(statement).first()
    if user:
        statement_nfc = select(NFCDB).where(NFCDB.email == email.email)
        db_nfc = session.exec(statement_nfc).first()
        
        if db_nfc:
            db_nfc.uuid = email.uuid  # Actualiza el UUID
        else:
            db_nfc = NFCDB(uuid=email.uuid, email=email.email)  # Crea nuevo si no existe
            session.add(db_nfc)
        
        session.commit()
    else:
        raise HTTPException(status_code=404, detail="Email doesn't exist")

        
        
@app.post("/register")
async def register(user: UserRegister, session: SessionDep):
    u = get_user(user.email, session)
    if u is None:
        hashed_password = hash_password(user.password)
        db_user = UserDB(uuid=user.username, username=user.username, email=user.email, password=hashed_password)
        session.add(db_user)
        session.commit()
        return {"message": "User registered", "username": user.username}
    else:
        raise HTTPException(status_code=400, detail="Email already exists")
    
@app.post("/login")
async def login(user: UserLogin, session: SessionDep):
    u = get_user(user.email, session)
    if u:
        if check_password(user.password, u.password):
            loggedinuser = user.email
            return {"message": "User logged in", "email": user.email}
        else:
            raise HTTPException(status_code=401, detail="Invalid password")
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
@app.get("/users")
async def get_all_users(session: SessionDep):
    statement = select(UserDB)
    results = session.exec(statement).all()
    return [user.model_dump() for user in results]

@app.get("/getID")
async def get_all_nfc(session: SessionDep):
    statement = select(NFCDB)
    results = session.exec(statement).all()
    return [nfc.model_dump() for nfc in results] 
    
    
def get_user(email: str, session: SessionDep):
    statement = select(UserDB).where(UserDB.email == email)
    return session.exec(statement).first()

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def check_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
