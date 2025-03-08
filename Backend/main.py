# main.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import mysql.connector
from mysql.connector import pooling
from datetime import datetime, timedelta
import math

app = FastAPI()

# Configure MySQL connection pool (adjust connection details as needed)
dbconfig = {
    "host": "localhost",
    "user": "root",
    "password": "P@ssw0rd",
    "database": "dogpark"
}
cnxpool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=10, **dbconfig)

# Constants for the dog park location (example: New York City)
DOG_PARK_LAT = 40.7128
DOG_PARK_LNG = -74.0060
# Define a radius in kilometers to consider a dog “present”
DOG_PARK_RADIUS_KM = 0.5

# Helper function to calculate distance between two coordinates (Haversine formula)
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Pydantic models for request/response validation
class DogRegister(BaseModel):
    name: str
    picture_url: str

class LocationUpdate(BaseModel):
    dog_id: int
    latitude: float
    longitude: float

class DogOut(BaseModel):
    id: int
    name: str
    picture_url: str
    latitude: float
    longitude: float
    last_updated: datetime

# Endpoint to register a new dog
@app.post("/api/register_dog")
def register_dog(dog: DogRegister):
    conn = cnxpool.get_connection()
    cursor = conn.cursor()
    try:
        query = """
        INSERT INTO dogs (name, picture_url, latitude, longitude, last_updated)
        VALUES (%s, %s, %s, %s, %s)
        """
        now = datetime.utcnow()
        # Initially set latitude and longitude to NULL (None) since location is unknown
        cursor.execute(query, (dog.name, dog.picture_url, None, None, now))
        conn.commit()
        return {"message": "Dog registered successfully", "dog_id": cursor.lastrowid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# Endpoint to update a dog's location
@app.post("/api/update_location")
def update_location(update: LocationUpdate):
    conn = cnxpool.get_connection()
    cursor = conn.cursor()
    try:
        query = """
        UPDATE dogs
        SET latitude = %s, longitude = %s, last_updated = %s
        WHERE id = %s
        """
        now = datetime.utcnow()
        cursor.execute(query, (update.latitude, update.longitude, now, update.dog_id))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Dog not found")
        return {"message": "Location updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# Endpoint to get dogs near the dog park
@app.get("/api/dogs_near_park", response_model=List[DogOut])
def get_dogs_near_park():
    conn = cnxpool.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Consider only dogs that have updated their location in the last 30 minutes
        cutoff = datetime.utcnow() - timedelta(minutes=30)
        query = "SELECT * FROM dogs WHERE last_updated >= %s"
        cursor.execute(query, (cutoff,))
        dogs = cursor.fetchall()

        # Filter by distance from the dog park using the haversine formula
        dogs_near = []
        for dog in dogs:
            if dog['latitude'] is None or dog['longitude'] is None:
                continue
            distance = haversine_distance(DOG_PARK_LAT, DOG_PARK_LNG, dog['latitude'], dog['longitude'])
            if distance <= DOG_PARK_RADIUS_KM:
                dogs_near.append(dog)

        return dogs_near
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
