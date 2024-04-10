"""
Happy Restaurant frontend Application

Author: Amir Sarrafzadeh Arasi
Date: 2024-04-10

Purpose:
This script is used to create a Streamlit frontend application for the Happy Restaurant. The script provides the following
functionalities to manage orders:
- Insert Order: Insert a new order
- View Order: View an order by order code
- Update Order: Update an order by order code
- Delete Order: Delete an order by order code

Usage:
Run the script to start the Streamlit application.
"""

# Import necessary libraries
import os
import sys
import logging
import requests
import configparser
import streamlit as st

# Check if the folder exists
if not os.path.exists("logs"):
    # Create the folder
    os.makedirs("logs")
else:
    pass

# Configure logging
logging.basicConfig(filename='./logs/frontend.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a ConfigParser object
config = configparser.ConfigParser()
try:
    # Read the configuration file
    config.read('config.ini')
    # Access values from the path section of the config file
    base_url = config.get('url', 'base_url')
    image_url = config.get('url', 'image_url')
    logging.info(f"Base URL: {base_url} is read from the config file.")
    logging.info(f"Image URL: {image_url} is read from the config file.")
except Exception as e:
    logging.error(f"Failed to read the configuration from the config file. Error: {e}")
    raise sys.exit(1)


# Streamlit UI
def main():
    st.title("Happy Restaurant 🍔")

    menu = ["Insert Order", "View Order", "Update Order", "Delete Order"]
    choice = st.sidebar.selectbox("Select the Section", menu)
    st.sidebar.write("Welcome to the Happy Restaurant")
    st.sidebar.image("./images/pizza.jpg", use_column_width=True)
    st.sidebar.image("./images/burger.jpg", use_column_width=True)

    st.markdown(
                """
        <style>
        .stApp {{
            background-image: url({}); 
            background-size: cover;
        }}
        </style>
        """.format(image_url),
        unsafe_allow_html=True
    )

    if choice == "Insert Order":
        st.subheader("Insert Order")
        logging.info("User accessed Insert Order section")
        order_code = st.text_input("Order Code")
        food_name = st.text_input("Food Name")
        customer_name = st.text_input("Customer Name")
        customer_surname = st.text_input("Customer Surname")
        customer_id = st.text_input("Customer ID")
        delivery_address = st.text_input("Delivery Address")
        payment_method = st.selectbox(
            "Payment Method", ["Cash", "Credit Card", "Online Transfer"]
        )
        if st.button("Insert"):
            payload = {
                "order_code": order_code,
                "food_name": food_name,
                "customer_name": customer_name,
                "customer_surname": customer_surname,
                "customer_id": customer_id,
                "delivery_address": delivery_address,
                "payment_method": payment_method,
            }
            response = requests.post(f"{base_url}/orders/", json=payload)
            if response.status_code == 200:
                st.success("Order inserted successfully!")
                logging.info("Order inserted successfully")
            else:
                st.error("Failed to insert order.")
                logging.error("Failed to insert order")

    elif choice == "View Order":
        st.subheader("View Order")
        logging.info("User accessed View Order section")
        order_code = st.text_input("Order Code")
        if st.button("View"):
            response = requests.get(f"{base_url}/orders/{order_code}")
            if response.status_code == 200:
                order = response.json()
                st.write(order)
                logging.info(f"Viewed order with code {order_code}")
            else:
                st.error("Order not found.")
                logging.error(f"Order with code {order_code} not found")

    elif choice == "Update Order":
        st.subheader("Update Order")
        logging.info("User accessed Update Order section")
        order_code = st.text_input("Order Code")
        food_name = st.text_input("Food Name")
        customer_name = st.text_input("Customer Name")
        customer_surname = st.text_input("Customer Surname")
        delivery_address = st.text_input("Delivery Address")
        payment_method = st.selectbox(
            "Payment Method", ["Cash", "Credit Card", "Online Transfer"]
        )
        if st.button("Update"):
            logging.info("User requested to update an order")
            payload = {}
            if food_name:
                payload["food_name"] = food_name
            if customer_name:
                payload["customer_name"] = customer_name
            if customer_surname:
                payload["customer_surname"] = customer_surname
            if delivery_address:
                payload["delivery_address"] = delivery_address
            if payment_method:
                payload["payment_method"] = payment_method

            if payload:
                logging.info("Payload for update: " + str(payload))
                response = requests.put(
                    f"{base_url}/orders/{order_code}", json=payload
                )
                if response.status_code == 200:
                    st.success("Order updated successfully!")
                    logging.info("Order updated successfully")
                else:
                    st.error("Failed to update order.")
                    logging.error("Failed to update order")
            else:
                st.warning("No fields to update.")
                logging.warning("No fields to update")

    elif choice == "Delete Order":
        st.subheader("Delete Order")
        logging.info("User accessed Delete Order section")
        order_code = st.text_input("Order Code")
        if st.button("Delete"):
            logging.info("User requested to delete an order")
            response = requests.delete(f"{base_url}/orders/{order_code}")
            if response.status_code == 200:
                st.success("Order deleted successfully!")
                logging.info("Order deleted successfully")
            else:
                st.error("Failed to delete order.")
                logging.error("Failed to delete order")


if __name__ == "__main__":
    main()

