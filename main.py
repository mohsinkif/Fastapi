from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException
from databases import Database
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import random
import string
import asyncpg
import psycopg2
from typing import List
from typing import Optional
from starlette.exceptions import HTTPException as StarletteHTTPException


# Define your database connection information
DB_NAME = "koyebdb" or "postgres"
DB_USER = "koyeb-adm" or "postgres"
DB_PASSWORD = "ZxrN8iHGp7ev" or "root"
DB_PORT = None
DB_HOST = "ep-fancy-bread-a29iiap4.eu-central-1.pg.koyeb.app" or "localhost"


DATABASE_URL = f"postgresql+asyncpg://{
    DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

print(DATABASE_URL)

app = FastAPI()


# Database connection parameters


origins = [
    "http://localhost",
    "http://localhost:3001",  # Update with your React frontend URL
]
# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

database = Database(DATABASE_URL)

# Dependency to get database connection


async def get_database():
    await database.connect()
    try:
        yield database
    finally:
        await database.disconnect()


@app.get("/create_db")
async def create_db(db: Database = Depends(get_database)):
    res = await db.execute("""
select * from pg_tables where schemaname='public';
""")
    
    print(res)
    return res


@app.get("/fetch_coordinates")
async def fetch_coordinates(db: Database = Depends(get_database)):
    query = "SELECT latitude, longitude, predictionvalue FROM table3;"
    result = await db.fetch_all(query)
    return result


# @app.post("/register")
# async def register_user(user_data: UserRegistration):
#     try:
#         # Connect to the database
#         await database.connect()

#         # Execute SQL query to insert user data into the database
#         query = "INSERT INTO farmer (username, password) VALUES (:username, :password);"
#         values = {"username": user_data.username,
#                   "password": user_data.password}
#         await database.execute(query=query, values=values)

#         # Return success message
#         return {"message": "User registered successfully"}

#     finally:
#         # Close the database connection
#         await database.disconnect()


@app.get("/check-connection")
async def check_connection():
    return {"message": "FastAPI backend is connected"}


class UserRegistration(BaseModel):
    farmername: str
    farmeremail: str
    farmerusername: str
    password: str
    farmer_land: str
    farmerphonenumber: str
    crop_name: str


@app.post("/RegisterUser")
async def RegisterUser(userdata: UserRegistration):
    try:
        # connect to database
        await database.connect()
        # execute the query

        query = "insert into farmer_info (farmername,farmeremail,farmerusername,password,farmerphonenumber,farmer_land) values (:farmername,:farmeremail,:farmerusername,:password,:farmerphonenumber, :farmer_land)"
        values = {
            "farmername": userdata.farmername,
            "farmeremail": userdata.farmeremail,
            "farmerusername": userdata.farmerusername,
            "password": userdata.password,
            "farmer_land": userdata.farmer_land,
            "farmerphonenumber": userdata.farmerphonenumber,
        }
        await database.execute(query=query, values=values)
        print("Values successfully entered in farmer information table\n")
        query2 = "insert into crop_info (crop_name) values (:crop_name)"
        values2 = {
            "crop_name": userdata.crop_name,
        }
        await database.execute(query=query2, values=values2)
        print("Values successfully entered in crop information table\n")
        query3 = """
                INSERT INTO farmer_crop (farmerid, crop_id)
                SELECT f.farmerid, c.crop_id
                FROM farmer_info f
                JOIN crop_info c ON f.farmername = :farmername AND c.crop_name = :crop_name;
                """
        values3 = {
            "farmername": userdata.farmername,
            "crop_name": userdata.crop_name,
        }
        await database.execute(query=query3, values=values3)
        print("Values successfully entered in farmer_crop information table\n")
        print(userdata)
        return {"Message": "User Registered Successfully"}
    except Exception as e:
        # In case of any error, raise HTTPException with 500 status code
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Close the database connection
        await database.disconnect()


class LoginCredentials(BaseModel):
    email: str
    password: str


def authenticate_user(email: str, password: str) -> int:

    # Database connection parameters

    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()

    cur.execute(
        "SELECT farmerid FROM farmer_info WHERE farmeremail = %s AND password = %s", (email, password))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if user:
        return user[0]  # Returns the farmerid if authentication successful
    else:
        return None

# Function to generate a random token


def generate_token(length: int = 32) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
# Endpoint to handle login requests


@app.post("/login")
async def login(credentials: LoginCredentials):
    print(credentials)
    farmerid = authenticate_user(credentials.email, credentials.password)
    if farmerid:
        token = generate_token()
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO authentication (farmerid, expire, token) VALUES (%s, %s, %s)", (farmerid, False, token))
        conn.commit()
        print("Values entered in authentication table")
        print(farmerid)
        print(token)

        cur.close()
        conn.close()
        return {"token": token}
    else:
        raise HTTPException(
            status_code=401, detail="Invalid email or password")


class LoginCredentials(BaseModel):
    email: str
    password: str


def authenticate_admin(email: str, password: str) -> int:

    # Database connection parameters

    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()

    cur.execute(
        "SELECT adminid FROM adminlogin WHERE email = %s AND password = %s", (email, password))
    user = cur.fetchone()

    cur.close()
    conn.close()

    if user:
        return user[0]  # Returns the adminid if authentication successful
    else:
        return None


def generate_token_admin(length: int = 32) -> str:
    return 'admin' + ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@app.post("/adminlogin")
async def adminlogin(credentials: LoginCredentials):
    adminid = authenticate_admin(credentials.email, credentials.password)
    if adminid:
        token = generate_token_admin()
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO adminauthentication (adminid, expire, token) VALUES (%s, %s, %s)", (adminid, False, token))
        conn.commit()

        cur.close()
        conn.close()
        return {"token": token}
    else:
        raise HTTPException(
            status_code=401, detail="Invalid email or password")


class HarvesterRegistration(BaseModel):
    harvester_name: str
    harvester_phone: str
    harvester_email: str
    city: str


@app.post("/add_harvester")
async def RegisterHarvester(userdata: HarvesterRegistration):
    try:
        # connect to database
        await database.connect()
        # execute the query
        query = "insert into harvester_information (harvester_name,harvester_phone,harvester_email,city) values (:harvester_name,:harvester_phone,:harvester_email,:city)"
        values = {
            "harvester_name": userdata.harvester_name,
            "harvester_phone": userdata.harvester_phone,
            "harvester_email": userdata.harvester_email,
            "city": userdata.city,
        }
        await database.execute(query=query, values=values)
        print("Values successfully entered in harvester information table\n")
        print(userdata)
    except Exception as e:
        # In case of any error, raise HTTPException with 500 status code
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Close the database connection
        await database.disconnect()


class TransporterRegistration(BaseModel):
    transporter_name: str
    transporter_phone: str
    transporter_email: str
    tcity: str


@app.post("/add_transporter")
async def RegisterTransporter(userdata: TransporterRegistration):
    try:
        # connect to database
        await database.connect()
        # execute the query
        query = "insert into transporter_information (transporter_name,transporter_phone,transporter_email,tcity) values (:transporter_name,:transporter_phone,:transporter_email,:tcity)"
        values = {
            "transporter_name": userdata.transporter_name,
            "transporter_phone": userdata.transporter_phone,
            "transporter_email": userdata.transporter_email,
            "tcity": userdata.tcity,
        }
        await database.execute(query=query, values=values)
        print("Values successfully entered in transporter information table\n")
        print(userdata)
    except Exception as e:
        # In case of any error, raise HTTPException with 500 status code
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Close the database connection
        await database.disconnect()

# Database connection information


# Model for request body


class CityRequest(BaseModel):
    city: str

# Model for response


class HarvesterInfo(BaseModel):
    harvester_name: str
    harvester_phone: str
    harvester_email: str

# Function to fetch harvester information from database


def get_harvesters_by_city(city: str) -> List[HarvesterInfo]:
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT harvester_name, harvester_phone, harvester_email FROM harvester_information WHERE city = '{
                city}'"
        )
        harvesters = cursor.fetchall()
        return [
            HarvesterInfo(
                harvester_name=harvester[0],
                harvester_phone=harvester[1],
                harvester_email=harvester[2],
            )
            for harvester in harvesters
        ]
    except Exception as e:
        print(f"Error fetching harvesters: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# API endpoint to fetch harvester information by city


@app.post("/viewharvester")
async def get_harvesters(city_request: CityRequest) -> List[HarvesterInfo]:
    city = city_request.city
    harvesters = get_harvesters_by_city(city)
    print(city)
    if not harvesters:
        raise HTTPException(
            status_code=404, detail="No harvesters found for the provided city")
    return harvesters


# Database connection information


# Function to delete harvester by email from database


class deleteharvester(BaseModel):
    harvester_email: str


def delete_harvester_by_email(harvester_email: str):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()
        print(harvester_email)
        cursor.execute(
            f"DELETE FROM harvester_information WHERE harvester_email = '{
                harvester_email}'"
        )
        conn.commit()
    except Exception as e:
        print(f"Error deleting harvester: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


class DeleteHarvester(BaseModel):
    harvester_email: str

# Assume `database` is your asyncpg connection pool

# Create an asyncpg connection pool


async def create_pool():
    return await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT
    )

# Initialize the connection pool
pool = None


@app.on_event("startup")
async def startup():
    global pool
    pool = await create_pool()

# Close the connection pool when the application stops


@app.on_event("shutdown")
async def shutdown():
    await pool.close()


@app.delete("/deleteharvester")
async def delete_harvester(userdata: DeleteHarvester):
    try:
        async with pool.acquire() as conn:
            query = "DELETE FROM harvester_information WHERE harvester_email = $1"
            await conn.execute(query, userdata.harvester_email)
            print("Values successfully deleted in harvester information table\n")
            return {"message": f"Harvester with email {userdata.harvester_email} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @app.post("/add_transporter")
# async def RegisterTransporter(userdata: TransporterRegistration):
#     try:
#         # connect to database
#         await database.connect()
#         # execute the query
#         query = "insert into transporter_information (transporter_name,transporter_phone,transporter_email,tcity) values (:transporter_name,:transporter_phone,:transporter_email,:tcity)"
#         values = {
#             "transporter_name": userdata.transporter_name,
#             "transporter_phone": userdata.transporter_phone,
#             "transporter_email": userdata.transporter_email,
#             "tcity": userdata.tcity,
#         }
#         await database.execute(query=query, values=values)
#         print("Values successfully entered in transporter information table\n")
#         print(userdata)
#     except Exception as e:
#         # In case of any error, raise HTTPException with 500 status code
#         raise HTTPException(status_code=500, detail=str(e))

#     finally:
#         # Close the database connection
#         await database.disconnect()


# Define your database connection information


# Define your Pydantic models


class TransporterInfo(BaseModel):
    transporter_name: str
    transporter_phone: str
    transporter_email: str
    tcity: str


class CityRequest(BaseModel):
    tcity: str

# Function to fetch transporter information from the database


def get_transporters_by_city(tcity: str) -> List[TransporterInfo]:
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(
            "SELECT transporter_name, transporter_phone, transporter_email, tcity FROM transporter_information WHERE tcity = %s",
            (tcity,)
        )
        transporters = cursor.fetchall()
        print(transporters)
        if not transporters:
            raise HTTPException(
                status_code=404, detail="No transporters found for the provided city")
        return [
            TransporterInfo(
                transporter_name=transporter[0],
                transporter_phone=transporter[1],
                transporter_email=transporter[2],
                tcity=transporter[3]
            )
            for transporter in transporters
        ]
    except psycopg2.Error as e:
        print(f"Error fetching transporters: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# API endpoint to fetch transporter information by city
class DeleteTransporter(BaseModel):
    transporter_email: str


@app.post("/viewtransporter", response_model=List[TransporterInfo])
async def get_transporters_by_city_endpoint(city_request: CityRequest):
    return get_transporters_by_city(city_request.tcity)


@app.delete("/deletetransporter")
async def delete_transporter(userdata: DeleteTransporter):
    try:
        async with pool.acquire() as conn:
            query = "DELETE FROM transporter_information WHERE transporter_email = $1"
            await conn.execute(query, userdata.transporter_email)
            print("Values successfully deleted in transporter information table\n")
            return {"message": f"Transporter with email {userdata.transporter_email} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Define your database connection information


# Define your Pydantic models


class FarmerInfo(BaseModel):
    farmername: str
    farmerphonenumber: str
    farmeremail: str
    # Add additional attributes
    farmerusername: Optional[str] = None
    farmer_land: Optional[str] = None


class FarmerEmail(BaseModel):
    farmeremail: str

# Function to fetch farmer information from the database


def get_farmer_by_email(farmeremail: str) -> Optional[FarmerInfo]:
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT farmername, farmerphonenumber, farmeremail, farmerusername, farmer_land FROM farmer_info WHERE farmeremail = '{
                farmeremail}'"
        )
        farmer = cursor.fetchone()
        if farmer:
            return FarmerInfo(
                farmername=farmer[0],
                farmerphonenumber=farmer[1],
                farmeremail=farmer[2],
                farmerusername=farmer[3],
                farmer_land=farmer[4]
            )
        else:
            return None
    except Exception as e:
        print(f"Error fetching farmer: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# API endpoint to fetch farmer information by email


@app.post("/viewfarmer")
async def fetch_farmer_by_email(farmer_email: FarmerEmail) -> Optional[FarmerInfo]:
    farmeremail = farmer_email.farmeremail
    farmer_info = get_farmer_by_email(farmeremail)
    if not farmer_info:
        raise HTTPException(
            status_code=404, detail="Farmer with the provided email not found"
        )
    return farmer_info


# Define your database connection information


# Define your Pydantic models


class FarmerEmail(BaseModel):
    farmeremail: str

# Function to delete a farmer account by email


def delete_farmer_by_email(farmeremail: str) -> None:
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(
            f"DELETE FROM farmer_info WHERE farmeremail = '{farmeremail}'"
        )
        conn.commit()
    except Exception as e:
        print(f"Error deleting farmer account: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# API endpoint to delete a farmer account by email


@app.delete("/deletefarmer")
async def delete_farmer_by_email_endpoint(farmeremail: FarmerEmail):
    farmeremail = farmeremail.farmeremail
    delete_farmer_by_email(farmeremail)
    return {"message": f"Farmer account with email {farmeremail} deleted successfully"}


# Define Pydantic models
class TokenRequest(BaseModel):
    token: str


class HarvesterInfo(BaseModel):
    harvester_name: str
    harvester_phone: str
    harvester_email: str
    city: str

# Function to fetch the farmer's city based on the provided token


def get_farmer_city(token: str) -> str:
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT f.farmer_land FROM farmer_info f JOIN authentication a ON f.farmerid = a.farmerid WHERE a.token = '{
                token}'"
        )
        farmer_city = cursor.fetchone()
        if farmer_city:
            return farmer_city[0]
        else:
            raise HTTPException(
                status_code=404, detail="Farmer not found for the provided token")
    except Exception as e:
        print(f"Error fetching farmer's city: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Function to fetch harvesters belonging to the same city


def get_harvesters_by_city(city: str) -> list[HarvesterInfo]:
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT harvester_name, harvester_phone, harvester_email, city FROM harvester_information WHERE city = '{
                city}'"
        )
        harvesters = cursor.fetchall()
        return [
            HarvesterInfo(
                harvester_name=harvester[0],
                harvester_phone=harvester[1],
                harvester_email=harvester[2],
                city=harvester[3]
            )
            for harvester in harvesters
        ]
    except Exception as e:
        print(f"Error fetching harvesters: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# API endpoint to fetch harvesters based on token


@app.post("/get_harvesters")
async def fetch_harvesters(token_request: TokenRequest) -> list[HarvesterInfo]:
    token = token_request.token
    farmer_city = get_farmer_city(token)
    # print(farmer_city)
    harvesters = get_harvesters_by_city(farmer_city)
    # print(harvesters)
    if not harvesters:
        raise HTTPException(
            status_code=404, detail="No harvesters found for the farmer's city"
        )
    return harvesters


# Define your database connection information


# Define Pydantic models


class TransporterInfo1(BaseModel):
    transporter_name: str
    transporter_phone: str
    transporter_email: str
    tcity: str


def get_transporter_by_city(tcity: str) -> list[TransporterInfo1]:
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT transporter_name, transporter_phone, transporter_email, tcity FROM transporter_information WHERE tcity = '{
                tcity}'"
        )
        harvesters = cursor.fetchall()
        return [
            TransporterInfo1(
                transporter_name=harvester[0],
                transporter_phone=harvester[1],
                transporter_email=harvester[2],
                tcity=harvester[3]
            )
            for harvester in harvesters
        ]
    except Exception as e:
        print(f"Error fetching transporters: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# API endpoint to fetch harvesters based on token


@app.post("/get_transporter")
async def fetch_transporters(token_request: TokenRequest) -> list[TransporterInfo1]:
    token = token_request.token
    farmer_city = get_farmer_city(token)
    # print(farmer_city)
    transporters = get_transporter_by_city(farmer_city)
    # print(transporters)
    if not transporters:
        raise HTTPException(
            status_code=404, detail="No transporters found for the farmer's city"
        )
    return transporters

# Database configuration


@app.get("/predictioncount")
def get_prediction_count():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(
            "SELECT predictionvalue, COUNT(*) FROM table3 GROUP BY predictionvalue")
        counts = cursor.fetchall()
        prediction_counts = {
            str(prediction): count for prediction, count in counts}
        print(prediction_counts)
        return prediction_counts
    except Exception as e:
        print(f"Error fetching prediction counts: {e}")
        return {"error": "Internal server error"}
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Message model


class Message(BaseModel):
    message: str
    token: str

# Function to establish database connection


def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )

# Function to retrieve farmer email based on token


def get_farmer_email(token: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT farmeremail FROM farmer_info WHERE farmerid = (SELECT farmerid FROM authentication WHERE token = %s)",
            (token,)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Submit message endpoint


@app.post("/submit_message")
def submit_message(message_data: Message):
    try:
        # Get farmer email based on token
        farmer_email = get_farmer_email(message_data.token)
        if not farmer_email:
            raise HTTPException(status_code=400, detail="Invalid token")

        # Insert message into contacttable
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO contacttable (email, messagee) VALUES (%s, %s)",
            (farmer_email, message_data.message)
        )
        conn.commit()
        return {"message": "Message submitted successfully"}
    except Exception as e:
        print(f"Error submitting message: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Your database connection details


# Define a Pydantic model for the request body


class TokenData(BaseModel):
    token: str

# Function to fetch the crop name based on the token


def get_crop_name(token_data: TokenData):
    token = token_data
    print(token)
    try:
        # Connect to the database
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()

        # Query to fetch the farmerid based on the token
        cursor.execute(
            "SELECT farmerid FROM authentication WHERE token = %s",
            (token,)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="Invalid token")

        farmerid = row[0]
        print(farmerid)

        # Query to fetch the crop_id based on the farmerid
        cursor.execute(
            "SELECT crop_id FROM farmer_crop WHERE farmerid = %s",
            (farmerid,)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=404, detail="Crop not found for this user")

        crop_id = row[0]
        print("crop id", crop_id)

        # Query to fetch the crop_name based on the crop_id
        cursor.execute(
            "SELECT crop_name FROM crop_info WHERE crop_id = %s",
            (crop_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=404, detail="Crop name not found for this crop id")
        print(row)
        return row[0]  # Return the crop name
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# API endpoint to fetch the crop name


@app.post("/fetch_crop")
def fetch_crop(token_data: TokenData):
    crop_name = get_crop_name(token_data.token)
    return crop_name


# Database connection details


# Define a Pydantic model for the response body


class ContactEntry(BaseModel):
    email: str
    message: str

# Function to fetch contact entries from the database


def get_contact_entries():
    try:
        # Connect to the database
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()

        # Query to fetch email and message from the contact table
        cursor.execute("SELECT email, messagee FROM contacttable")

        # Fetch all rows
        rows = cursor.fetchall()

        # Map rows to ContactEntry objects
        contact_entries = [ContactEntry(
            email=row[0], message=row[1]) for row in rows]

        return contact_entries
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# API endpoint to fetch contact entries


@app.get("/contact_entries")
def fetch_contact_entries():
    contact_entries = get_contact_entries()
    return {"data": contact_entries}


print("Hello worlddd")


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except (HTTPException, StarletteHTTPException) as ex:
            if ex.status_code == 404:
                return await super().get_response("index.html", scope)
            else:
                raise ex


app.mount("/", SPAStaticFiles(directory="frontend", html=True), name="app")
