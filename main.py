from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException
from databases import Database
from pydantic import BaseModel

DATABASE_URL = "postgresql+asyncpg://postgres:root@localhost/postgres"

app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

database = Database(DATABASE_URL)

# Dependency to get database connection


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
    harvester_name: str
    harvester_email: str
    harvester_phone: str
    transporter_name: str
    transporter_email: str
    transporter_phone: str

@app.post("/RegisterUser")
async def RegisterUser(userdata: UserRegistration):
    try:
        #connect to database
        await database.connect()
        #execute the query

        query5 = """
                INSERT INTO transporter_information (transporter_name,transporter_email,transporter_phone)
                values (:transporter_name,:transporter_email,:transporter_phone)
                """
        values5 = {
            "transporter_name": userdata.transporter_name,
            "transporter_email": userdata.transporter_email,
            "transporter_phone": userdata.transporter_phone,
        }
        try:
            await database.execute(query=query5, values=values5)
            print("Values successfully entered in transporter information table\n")
            print(userdata)
        except Exception as e:
            print(f"Error inserting values into transporter information table: {str(e)}")
            print(userdata)

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
        query2="insert into crop_info (crop_name) values (:crop_name)"
        values2 = {
            "crop_name": userdata.crop_name,
        }
        await database.execute(query=query2, values=values2)
        print("Values successfully entered in crop information table\n")
        query3="""
                INSERT INTO farmer_crop (farmerid, crop_id)
                SELECT f.farmerid, c.crop_id
                FROM farmer_info f
                JOIN crop_info c ON f.farmername = :farmername AND c.crop_name = :crop_name;
                """
        values3={
            "farmername": userdata.farmername,
            "crop_name":userdata.crop_name,
        }
        await database.execute(query=query3, values=values3)

        print("Values successfully entered in farmer_crop information table\n")

        query5 = """
                insert into transporter_information (transporter_name,transporter_email,transporter_phone)
                values (:transporter_name,:transporter_email,:transporter_phone)
                """
        values5 = {
            "transporter_name": userdata.transporter_name,
            "transporter_email": userdata.transporter_email,
            "transporter_phone": userdata.transporter_phone,
        }
        await database.execute(query=query5, values=values5)
        print("Values successfully entered in transporter information table\n")






        query4 = """
        INSERT INTO harvester_information (harvester_name, harvester_email, harvester_phone)
        VALUES (  :harvester_name, :harvester_email, :harvester_phone);
        """

        values4 = {
        "harvester_name": userdata.harvester_name,
        "harvester_email": userdata.harvester_email,
        "harvester_phone": userdata.harvester_phone,
        }

        await database.execute(query=query4, values=values4)

        print("Values successfully entered in Harvester information table\n")

        query5="""
                insert into transporter_information (transporter_name,transporter_email,transporter_phone)
                values (:transporter_name,:transporter_email,:transporter_phone)
                """
        values5={
            "transporter_name":userdata.transporter_name,
            "transporter_email":userdata.transporter_email,
            "transporter_phone":userdata.transporter_phone,
        }
        await database.execute(query=query5,values=values5)
        print("Values successfully entered in transporter information table\n")

        query6="""
                INSERT INTO farmer_harvester_relation (farmerid, harvester_id)
                SELECT f.farmerid, c.harvester_id
                FROM farmer_info f
                JOIN harvester_information c ON f.farmername = :farmername AND c.harvester_name = :harvester_name;
                """
        values6={
            "farmername": userdata.farmername,
            "harvester_name": userdata.harvester_name,
        }

        await database.execute(query=query6,values=values6)

        print("Values successfully entered in farmer_harvester information table\n")

        query7="""
            INSERT INTO farmer_transporter_relation (farmerid, transporter_id)
            SELECT f.farmerid, c.transporter_id
            FROM farmer_info f
            JOIN transporter_information c ON f.farmername = :farmername AND c.transporter_name = :transporter_name ;                
            """
        values7={
            "farmername": userdata.farmername,
            "transporter_name": userdata.transporter_name
        }
        await database.execute(query=query7,values=values7)
        print("Values successfully entered in farmer_transporter information table\n")
        return {"Message":"User Registered Successfully"}
    except Exception as e:
        # In case of any error, raise HTTPException with 500 status code
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Close the database connection
        await database.disconnect()


