# backend.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import uvicorn

# Create FastAPI app
app = FastAPI()

# SQLite database setup
DATABASE_FILE = "./restaurant.db"

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
async def read_root():
    # Return a default background image
    return FileResponse("back.jpg", media_type="image/jpeg")

@app.get("/favicon.ico")
async def get_favicon():
    # Return a default favicon.ico file
    return FileResponse("re.ico")

@app.post("/orders/")
async def create_order(order: OrderCreate):
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
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Order code or customer ID already exists")
    conn.close()
    return order.dict()


@app.get("/orders/{order_code}")
async def read_order(order_code: str):
    rows = fetch_all(f"SELECT * FROM orders WHERE order_code='{order_code}'")
    if not rows:
        raise HTTPException(status_code=404, detail="Order not found")
    return rows


@app.put("/orders/{order_code}")
async def update_order(order_code: str, order_update: OrderUpdate):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    update_fields = []
    for key, value in order_update.dict().items():
        if value is not None:
            update_fields.append((key, value))
    if not update_fields:
        conn.close()
        raise HTTPException(status_code=400, detail="No fields to update")
    try:
        cursor.execute(f"""
            UPDATE orders
            SET {', '.join([f"{field[0]}=?" for field in update_fields])}
            WHERE order_code=?
        """, tuple([field[1] for field in update_fields] + [order_code]))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Customer ID already exists")
    conn.close()
    return dict(order_code=order_code, **order_update.dict())


@app.delete("/orders/{order_code}")
async def delete_order(order_code: str):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE order_code=?", (order_code,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")
    conn.commit()
    conn.close()
    return {"message": "Order deleted successfully"}


# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
