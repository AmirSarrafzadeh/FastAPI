"""
Happy Restaurant Backend Application

Author: Amir Sarrafzadeh Arasi
Date: 2024-04-10

Purpose:
This script is used to create a FastAPI backend application for the Happy Restaurant. The script reads the database
name from the config.ini file and creates a SQLite database with the specified name. The script provides the following
endpoints to manage orders:
- POST /orders/: Create a new order
- GET /orders/{order_code}: Get an order by order code
- PUT /orders/{order_code}: Update an order by order code
- DELETE /orders/{order_code}: Delete an order by order code
The script also provides a default background image at the root URL.

Usage:
Run the script to start the FastAPI application.
"""

# Import necessary libraries
import io
import os
import sys
import sqlite3
import uvicorn
import logging
import configparser
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse, StreamingResponse

# Check if the folder exists
if not os.path.exists("logs"):
    # Create the folder
    os.makedirs("logs")
else:
    pass

# Configure logging
logging.basicConfig(filename='./logs/backend.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a ConfigParser object
config = configparser.ConfigParser()
try:
    # Read the configuration file
    config.read('config.ini')
    # Access values from the path section of the config file
    db_name = config.get('database', 'name')
    logging.info(f"Database name: {db_name} is read from the config file.")
except Exception as e:
    logging.error(f"Failed to read the configuration from the config file. Error: {e}")
    raise sys.exit(1)

# Create FastAPI app
app = FastAPI()

# SQLite database setup
DATABASE_FILE = f"./{db_name}.db"

# Create table if it doesn't exist
def create_table():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_code TEXT PRIMARY KEY,
            food_name TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            customer_surname TEXT NOT NULL,
            customer_id TEXT NOT NULL UNIQUE,
            delivery_address TEXT NOT NULL,
            payment_method TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    logging.info("Database table 'orders' created successfully.")

create_table()

# Pydantic model for request body
class OrderCreate(BaseModel):
    order_code: str
    food_name: str
    customer_name: str
    customer_surname: str
    customer_id: str
    delivery_address: str
    payment_method: str


class OrderUpdate(BaseModel):
    food_name: str = None
    customer_name: str = None
    customer_surname: str = None
    delivery_address: str = None
    payment_method: str = None


# Function to execute SQL query and fetch all rows
def fetch_all(query):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows


@app.get("/")
async def show_fullscreen_image():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body, html {
        height: 100%;
        margin: 0;
        overflow: hidden;
    }

    .fullscreen-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    </style>
    </head>
    <body>
    <img class="fullscreen-img" src="/image" />
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/image")
async def get_image():
    with open("./images/get.jpg", "rb") as f:
        image_data = f.read()
    return StreamingResponse(io.BytesIO(image_data), media_type="image/jpeg")


@app.get("/favicon.ico")
async def get_favicon():
    logging.info("GET request received at favicon.ico URL.")
    # Return a default favicon.ico file
    return FileResponse("./images/icon.ico")

@app.post("/orders/")
async def create_order(order: OrderCreate):
    logging.info("POST request received at /orders/ endpoint.")
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            order.order_code,
            order.food_name,
            order.customer_name,
            order.customer_surname,
            order.customer_id,
            order.delivery_address,
            order.payment_method
        ))
        conn.commit()
        logging.info("Order created successfully.")
    except sqlite3.IntegrityError:
        conn.close()
        logging.error("Failed to create order. Order code or customer ID already exists.")
        raise HTTPException(status_code=400, detail="Order code or customer ID already exists")
    conn.close()
    return order.dict()


@app.get("/orders/{order_code}")
async def read_order(order_code: str):
    logging.info(f"GET request received at /orders/{order_code} endpoint.")
    rows = fetch_all(f"SELECT * FROM orders WHERE order_code='{order_code}'")
    if not rows:
        logging.error(f"Order with order code {order_code} not found.")
        raise HTTPException(status_code=404, detail="Order not found")
    return rows


@app.put("/orders/{order_code}")
async def update_order(order_code: str, order_update: OrderUpdate):
    logging.info(f"PUT request received at /orders/{order_code} endpoint.")
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    update_fields = []
    for key, value in order_update.dict().items():
        if value is not None:
            update_fields.append((key, value))
    if not update_fields:
        conn.close()
        logging.error("No fields to update.")
        raise HTTPException(status_code=400, detail="No fields to update")
    try:
        cursor.execute(f"""
            UPDATE orders
            SET {', '.join([f"{field[0]}=?" for field in update_fields])}
            WHERE order_code=?
        """, tuple([field[1] for field in update_fields] + [order_code]))
        conn.commit()
        logging.info("Order updated successfully.")
    except sqlite3.IntegrityError:
        conn.close()
        logging.error("Failed to update order. Customer ID already exists.")
        raise HTTPException(status_code=400, detail="Customer ID already exists")
    conn.close()
    return dict(order_code=order_code, **order_update.dict())


@app.delete("/orders/{order_code}")
async def delete_order(order_code: str):
    logging.info(f"DELETE request received at /orders/{order_code} endpoint.")
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE order_code=?", (order_code,))
    if cursor.rowcount == 0:
        conn.close()
        logging.error(f"Order with order code {order_code} not found.")
        raise HTTPException(status_code=404, detail="Order not found")
    conn.commit()
    conn.close()
    logging.info("Order deleted successfully.")
    return {"message": "Order deleted successfully"}


# Run the FastAPI app
if __name__ == "__main__":
    logging.info("Starting the FastAPI server...")
    # TODO change the ip to server ip in production
    uvicorn.run(app, host="localhost", port=8000)

