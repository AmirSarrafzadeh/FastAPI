# frontend.py
import streamlit as st
import requests

# Define base URL for API endpoints
BASE_URL = "http://localhost:8000"


# Streamlit UI
def main():
    st.title("Happy Restaurant 🍔")

    menu = ["Insert Order", "View Order", "Update Order", "Delete Order"]
    choice = st.sidebar.selectbox("Select the Section", menu)

    st.sidebar.write("Welcome to the Happy Restaurant")

    st.sidebar.image("pizza.jpg", use_column_width=True)

    st.sidebar.image("burger.jpg", use_column_width=True)

    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://content.fortune.com/wp-content/uploads/2019/05/tak-room-rendering-web.jpg"); 
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if choice == "Insert Order":
        st.subheader("Insert Order")
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
            response = requests.get(f"{BASE_URL}/orders/", json=payload)
            if response.status_code == 200:
                st.success("Order inserted successfully!")
            else:
                st.error("Failed to insert order.")

    elif choice == "View Order":
        st.subheader("View Order")
        order_code = st.text_input("Order Code")
        if st.button("View"):
            response = requests.get(f"{BASE_URL}/orders/{order_code}")
            if response.status_code == 200:
                order = response.json()
                st.write(order)
            else:
                st.error("Order not found.")

    elif choice == "Update Order":
        st.subheader("Update Order")
        order_code = st.text_input("Order Code")
        food_name = st.text_input("Food Name")
        customer_name = st.text_input("Customer Name")
        customer_surname = st.text_input("Customer Surname")
        delivery_address = st.text_input("Delivery Address")
        payment_method = st.selectbox(
            "Payment Method", ["Cash", "Credit Card", "Online Transfer"]
        )
        if st.button("Update"):
            payload = {
                "food_name": food_name,
                "customer_name": customer_name,
                "customer_surname": customer_surname,
                "delivery_address": delivery_address,
                "payment_method": payment_method,
            }
            response = requests.put(
                f"{BASE_URL}/orders/{order_code}", json=payload
            )
            if response.status_code == 200:
                st.success("Order updated successfully!")
            else:
                st.error("Failed to update order.")

    elif choice == "Delete Order":
        st.subheader("Delete Order")
        order_code = st.text_input("Order Code")
        if st.button("Delete"):
            response = requests.delete(f"{BASE_URL}/orders/{order_code}")
            if response.status_code == 200:
                st.success("Order deleted successfully!")
            else:
                st.error("Failed to delete order.")


if __name__ == "__main__":
    main()
