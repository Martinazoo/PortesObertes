from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select, update
from typing import Annotated
import bcrypt

import time


app = FastAPI()
class UserEmail(BaseModel):
    email: str
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
    

# if loggedinuser is none raise httpexception 422 

@app.post("/uuid_save")
async def get_uuid(uuid_data: NFCUuid, session: SessionDep):
    statement = select(NFCDB).where(NFCDB.uuid == uuid_data.uuid)
    res = session.exec(statement).first()
    if res is None:
        db_nfc = NFCDB(uuid=uuid_data.uuid, email=None)
        session.add(db_nfc)
        session.commit()
        return
    elif res.uuid and res.email:
        print(f"You're {res.email}")
        return res.model_dump() 
    else:
        print(res.uuid)
        raise HTTPException(status_code=404, detail="NFC not asigner")
        
        
@app.post("/whoamI")
async def who_am_i(nfc: NFCUuid, session: SessionDep):
    statement_nfc = select(NFCDB).where(NFCDB.uuid == nfc.uuid)
    db_nfc = session.exec(statement_nfc).first()
    
    if db_nfc:
        return db_nfc.model_dump()
    else:
        raise HTTPException(status_code=404, detail="NFC not found")

        
    
@app.post("/assignnfc")
async def assign_nfc_to_email(nfc: NFCUuid, user: UserEmail, session: SessionDep):
    
    statement_user = select(UserDB).where(UserDB.email == user.email)
    db_user = session.exec(statement_user).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    statement_nfc = select(NFCDB).where(NFCDB.uuid == nfc.uuid)
    db_nfc = session.exec(statement_nfc).first()
    
    if not db_nfc:
        raise HTTPException(status_code=404, detail="NFC not found")

    statement_exist = select(NFCDB).where(
        (NFCDB.email == user.email) & (NFCDB.uuid == nfc.uuid)
    )
    db_exist = session.exec(statement_exist).first()

    if db_exist:
        raise HTTPException(status_code=400, detail="NFC already assigned to the user")
    statement_update = update(NFCDB).where(NFCDB.uuid == nfc.uuid).values(email=user.email)
    result = session.exec(statement_update)

    if result:
        session.commit() 
        session.refresh(db_nfc)
        return {"message": "NFC assigned successfully", "nfc": db_nfc}
    else:
        raise HTTPException(status_code=404, detail="Failed to assign NFC")
    
    
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
            print(loggedinuser)
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

def get_uuid(uuid: str, session: SessionDep):
    statement = select(NFCUuid).where(NFCUuid.uuid == uuid)
    return session.exec(statement).first()

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def check_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
