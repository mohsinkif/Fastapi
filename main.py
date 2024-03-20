from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException
from databases import Database
from fastapi.middleware.cors import CORSMiddleware
DATABASE_URL = "postgresql+asyncpg://postgres:root@localhost/postgres"

app = FastAPI()

database = Database(DATABASE_URL)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:3000",
    # "http://localhost:5173/login#home"
    # "http://localhost:5173/login"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
async def get_database():
    await database.connect()
    try:
        yield database
    finally:
        await database.disconnect()
@app.get("/fetch_coordinates")
async def fetch_coordinates(db: Database = Depends(get_database)):
    query = "SELECT latitude, longitude, opacity FROM table2;"
    result = await db.fetch_all(query)
    return result


class UserRegistration(BaseModel):
    username: str
    password: str


@app.post("/register")
async def register_user(user_data: UserRegistration):
    try:
        # Connect to the database
        await database.connect()

        # Execute SQL query to insert user data into the database
        query = "INSERT INTO farmer (username, password) VALUES (:username, :password);"
        values = {"username": user_data.username,
                  "password": user_data.password}
        await database.execute(query=query, values=values)

        # Return success message
        return {"message": "User registered successfully"}

    finally:
        # Close the database connection
        await database.disconnect()


@app.get("/check-connection")
async def check_connection():
    return {"message": "FastAPI backend is connected"}
