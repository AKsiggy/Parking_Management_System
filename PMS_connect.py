import streamlit as st
import mysql.connector
from datetime import datetime, timedelta
import pandas as pd

#database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Kumaraayush123%",
    database="Parking_Management_System"
)
cursor = db.cursor()

#-------------------------------------------------------------------------------------------------------------------------------

#Streamlit
st.title("Parking Management System")

menu = st.sidebar.selectbox("Menu", ["Add User with Car Details", "Edit Parking Spot", "Make Reservation", "Exit Vehicle"])

#-------------------------------------------------------------------------------------------------------------------------------

if menu == "Add User with Car Details":
    st.header("Add User with Car Details")
    user_name = st.text_input("User Name")
    email = st.text_input("Email")
    license_plate = st.text_input("License Plate")
    vehicle_type = st.text_input("Vehicle Type")

    if st.button("Add User with Car"):
        cursor.execute("INSERT INTO User (UserName, Email) VALUES (%s, %s)", (user_name, email))
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO Vehicle (LicensePlate, OwnerName, VehicleType) VALUES (%s, %s, %s)",
                       (license_plate, user_name, vehicle_type))
        vehicle_id = cursor.lastrowid

        db.commit()
        st.success(f"User with ID {user_id} and Vehicle ID {vehicle_id} added successfully.")
    cursor.execute("SELECT * FROM User")
    users = cursor.fetchall()
    df_users = pd.DataFrame(users, columns=[i[0] for i in cursor.description])
    st.write("Users:")
    st.dataframe(df_users)

    cursor.execute("SELECT * FROM Vehicle")
    users = cursor.fetchall()
    df_users = pd.DataFrame(users, columns=[i[0] for i in cursor.description])
    st.write("Vehicle info:")
    st.dataframe(df_users)

#-------------------------------------------------------------------------------------------------------------------------

elif menu == "Edit Parking Spot":
    st.header("Edit Parking Spot")
    spot_number = st.number_input("Spot Number", min_value=1, step=1)

    if st.button("Add Parking Spot"):
        # Insert data into the ParkingSpot table
        cursor.execute("INSERT INTO ParkingSpot (SpotNumber, IsOccupied) VALUES (%s, %s)", (spot_number, 0))
        spot_id = cursor.lastrowid
        db.commit()
        st.success(f"Parking Spot with ID {spot_id} added successfully.")
    cursor.execute("SELECT * FROM Parkingspot")
    users = cursor.fetchall()
    df_users = pd.DataFrame(users, columns=[i[0] for i in cursor.description])
    st.write("Parkingspot:")
    st.dataframe(df_users)

    spot_to_delete = st.number_input("Enter Spot ID to delete:", min_value=1, step=1)
    if st.button("Delete Parking Spot"):
        cursor.execute("SELECT * FROM ParkingSpot WHERE SpotID = %s", (spot_to_delete,))
        existing_spot = cursor.fetchone()
        if existing_spot:
            cursor.execute("DELETE FROM ParkingSpot WHERE SpotID = %s", (spot_to_delete,))
            db.commit()
            st.success(f"Parking Spot with ID {spot_to_delete} deleted successfully.")
        else:
            st.warning("The specified parking spot does not exist.")

#---------------------------------------------------------------------------------------------------------------------------

elif menu == "Make Reservation":
    st.header("Make Reservation")
    user_id = st.number_input("User ID", min_value=1, step=1)
    spot_id = st.number_input("Spot ID", min_value=1, step=1)

    if st.button("Make Reservation"):
        # Check if the spot is available
        cursor.execute("SELECT IsSpotAvailable(%s)", (spot_id,))
        is_available = cursor.fetchone()[0]

        if is_available:
            reservation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE ParkingSpot SET IsOccupied = 1, EntryTime = %s WHERE SpotID = %s",
                           (reservation_time, spot_id))
            db.commit()
            cursor.execute("INSERT INTO Reservation (UserID, SpotID, ReservationTime) VALUES (%s, %s, %s)",
                           (user_id, spot_id, reservation_time))
            reservation_id = cursor.lastrowid
            db.commit()
            st.success(f"Reservation with ID {reservation_id} made successfully.")
        else:
            st.warning("The selected spot is not available.")
    cursor.execute("SELECT * FROM Reservation")
    users = cursor.fetchall()
    df_users = pd.DataFrame(users, columns=[i[0] for i in cursor.description])
    st.write("Reservations:")
    st.dataframe(df_users)

#--------------------------------------------------------------------------------------------------------------------------------

elif menu == "Exit Vehicle":
    st.header("Exit Vehicle")
    spot_id_exit = st.number_input("Spot ID", min_value=1, step=1)

    if st.button("Exit Vehicle"):
        # Update exit time and calculate payment
        cursor.execute("UPDATE ParkingSpot SET IsOccupied = 0 WHERE SpotID = %s", (spot_id_exit,))
        cursor.execute("SELECT EntryTime FROM ParkingSpot WHERE SpotID = %s", (spot_id_exit,))
        entry_time = cursor.fetchone()[0]

        exit_time = datetime.now()
        elapsed_time = exit_time - entry_time
        hours_parked = elapsed_time.total_seconds() / 3600

        payment_amount = round(hours_parked * 50, 2)

        cursor.execute("INSERT INTO Payment (ReservationID, Amount) VALUES (%s, %s)", (spot_id_exit, payment_amount))
        db.commit()

        st.success(f"Vehicle exited successfully. Payment of {payment_amount} INR generated.")
    cursor.execute("SELECT * FROM Payment")
    users = cursor.fetchall()
    df_users = pd.DataFrame(users, columns=[i[0] for i in cursor.description])
    st.write("Billing:")
    st.dataframe(df_users)
