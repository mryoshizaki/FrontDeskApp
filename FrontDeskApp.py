import sqlite3
from tabulate import tabulate

# Connect to the SQLite database
conn = sqlite3.connect('FrontDeskApp.db')
cur = conn.cursor()

# Create the Customer table
cur.execute('''
    CREATE TABLE IF NOT EXISTS Customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone_number TEXT NOT NULL
    )''')

# Create Storage table
cur.execute('''
    CREATE TABLE IF NOT EXISTS Storage (
        id INTEGER PRIMARY KEY,
        size_name TEXT UNIQUE,
        capacity INTEGER
    )
''')

# Create Boxes table
cur.execute('''
    CREATE TABLE IF NOT EXISTS Boxes (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        box_size INTEGER,
        FOREIGN KEY (customer_id) REFERENCES Customers (id),
        FOREIGN KEY (box_size) REFERENCES Storage (id)
    )
''')

# Insert Storage data capacity
cur.executemany('''
    INSERT OR IGNORE INTO Storage (size_name, capacity)
    VALUES (?, ?)
''', [
    ("Small", 92),  # Capacity: 92
    ("Medium", 28),  # Capacity: 28
    ("Large", 24)  # Capacity: 24
])

#Create Table for Other Storage Facilities
#The capacities have default values 92, 28, 24 for small, medium, and large boxes
#The spaces left for each box areas are randomized
cur.execute('''
        CREATE TABLE IF NOT EXISTS OtherStorageFacilities (
            id INTEGER PRIMARY KEY,
            facility_name TEXT NOT NULL,
            small_capacity INTEGER DEFAULT 92,
            small_space_left INTEGER DEFAULT (92 - ABS(RANDOM() % 30)),
            medium_capacity INTEGER DEFAULT 28,
            medium_space_left INTEGER DEFAULT (28 - ABS(RANDOM() % 8)),
            large_capacity INTEGER DEFAULT 24,
            large_space_left INTEGER DEFAULT (24 - ABS(RANDOM() % 6))
        )
    ''')

#Create table for Reservations to other facilities
cur.execute('''
    CREATE TABLE IF NOT EXISTS Reservations (
        id INTEGER PRIMARY KEY,
        facility_name TEXT NOT NULL,
        box_size TEXT NOT NULL,
        customer_id INTEGER NOT NULL,
        FOREIGN KEY (facility_name) REFERENCES OtherStorageFacilities (id),
        FOREIGN KEY (customer_id) REFERENCES Customers (id)
    )
''')

conn.commit()

# Create new storage customer
def create_customer(first_name, last_name, phone_number):
    try:
        cur.execute('''
            INSERT INTO customers (first_name, last_name, phone_number)
            VALUES (?, ?, ?)
        ''', (first_name, last_name, phone_number))
        conn.commit()
        return 'Customer successfully added'
    except Exception as e:
        raise ValueError from None

# Check the availability of the storage area
def check_availability():
    cur.execute('''
            SELECT size_name, capacity FROM Storage
        ''')
    box_sizes_data = cur.fetchall()

    availability_dict = {}
    for size_name, capacity in box_sizes_data:
        cur.execute('''
            SELECT COUNT(*) FROM Boxes
            WHERE box_size_id = (
                SELECT id FROM Storage WHERE size_name = ?
            )
        ''', (size_name,))
        used_boxes = cur.fetchone()[0]
        remaining_boxes = capacity - used_boxes
        availability_dict[size_name] = remaining_boxes

    return availability_dict

# Check the availability of specific box size
def check_box_size_availability(box_size):
    cur.execute('''
            SELECT capacity FROM Storage
            WHERE size_name = ?
        ''', (box_size,))
    result = cur.fetchone()
    if not result:
        return 0

    capacity = result[0]
    cur.execute('''
        SELECT COUNT(*) FROM Boxes
        WHERE box_size_id = (
            SELECT id FROM Storage WHERE size_name = ?
        )
    ''', (box_size,))
    used_boxes = cur.fetchone()[0]
    remaining_boxes = capacity - used_boxes
    return remaining_boxes

# Store a box
def store(box_size, first_name, last_name):
    remaining_boxes = check_box_size_availability(box_size)
    if remaining_boxes > 0:
        customer_id = get_customer(first_name, last_name)
        cur.execute('''
                SELECT facility_name
                FROM OtherStorageFacilities
                WHERE box_size = ?
                AND customer_id IS NULL
                ORDER BY facility_name
                LIMIT 1
            ''', (box_size,))
        facility_name = cur.fetchone()[0]
        if customer_id != "Customer not existing":
            cur.execute('''
                INSERT INTO Boxes (box_size_id, customer_id)
                VALUES (
                    (SELECT id FROM Storage WHERE size_name = ?),
                    ?
                )
            ''', (box_size, customer_id))
            conn.commit()
            return True
        else:
            print(customer_id)
    else: 
        facility_name = get_facility_name(box_size)
        reserve_spot_in_other_facility(facility_name,box_size,first_name,last_name)
        conn.commit()
        print("Reserved a space at", facility_name)
    return False

# Retrieve box
def retrieve(box_size, first_name, last_name):
    customer_id = get_customer_id(first_name, last_name)
    if customer_id == "Customer not existing":
        print("Customer not existing") 
        return False

    cur.execute('''
        SELECT COUNT(*) FROM Boxes
        WHERE box_size_id = (
            SELECT id FROM Storage WHERE size_name = ?
        ) AND customer_id = ?
    ''', (box_size, customer_id))
    count = cur.fetchone()[0]
    if count > 0:
        cur.execute('''
            DELETE FROM Boxes
            WHERE id IN (
                SELECT id FROM Boxes
                WHERE box_size_id = (
                    SELECT id FROM Storage WHERE size_name = ?
                ) AND customer_id = ?
                LIMIT 1
            )
        ''', (box_size, customer_id))
        conn.commit()
        return True
    return False

# Retrieve customer based on customer id
def get_customer(first_name, last_name):
    customer_id = get_customer_id(first_name, last_name)
    if not customer_id:
        return "Customer not existing"
    return customer_id

# Retrieve customer id
def get_customer_id(first_name, last_name):
    cur.execute('''
        SELECT id FROM Customers
        WHERE first_name = ? AND last_name = ?
    ''', (first_name, last_name))
    result = cur.fetchone()
    return result[0] if result else None

# Retrieve facility name
def get_facility_name(box_size):
    if box_size == "Small":
        cur.execute('''
            SELECT facility_name
            FROM OtherStorageFacilities
            WHERE small_space_left > 0
            ORDER BY facility_name
            LIMIT 1
        ''')
        facility_name = cur.fetchone()[0]
    elif box_size == "Medium":
        cur.execute('''
            SELECT facility_name
            FROM OtherStorageFacilities
            WHERE medium_space_left > 0
            ORDER BY facility_name
            LIMIT 1
        ''')
        facility_name = cur.fetchone()[0]
    elif box_size == "Large":
        cur.execute('''
            SELECT facility_name
            FROM OtherStorageFacilities
            WHERE large_space_left > 0
            ORDER BY facility_name
            LIMIT 1
        ''')
        facility_name = cur.fetchone()[0]
    else:
        facility_name = None
    return facility_name

# Check other facilities for availability
def check_other_facility_availability(box_size):
        cur.execute('''
            SELECT facility_name, small_space_left, medium_space_left, large_space_left
            FROM OtherStorageFacilities
        ''')
        facilities_data = cur.fetchall()

        availability_dict = {}
        for facility_name, small_capacity, medium_capacity, large_capacity in facilities_data:
            if box_size == "Small":
                cur.execute('''
                    SELECT COUNT(*) FROM Reservations
                    WHERE facility_name = ? AND box_size = ? AND customer_id IS NULL
                ''', (facility_name, 1))
                remaining_boxes = small_capacity - cur.fetchone()[0] - get_reservation_count(facility_name, "Small")
            elif box_size == "Medium":
                cur.execute('''
                    SELECT COUNT(*) FROM Reservations
                    WHERE facility_name = ? AND box_size = ? AND customer_id IS NULL
                ''', (facility_name, 2))
                remaining_boxes = medium_capacity - cur.fetchone()[0] - get_reservation_count(facility_name, "Medium")
            elif box_size == "Large":
                cur.execute('''
                    SELECT COUNT(*) FROM Reservations
                    WHERE facility_name = ? AND box_size = ? AND customer_id IS NULL
                ''', (facility_name, 3))
                remaining_boxes = large_capacity - cur.fetchone()[0] - get_reservation_count(facility_name, "Large")

            availability_dict[facility_name] = remaining_boxes
        return availability_dict

#Reserve a spot in other facilities
def reserve_spot_in_other_facility(facility_name, box_size, first_name, last_name):
    customer_id = get_customer_id(first_name, last_name)
    if customer_id == "Customer not existing":
        return False

    cur.execute('''
        INSERT INTO Reservations (facility_name, box_size, customer_id)
        VALUES (?, ?, ?)
    ''', (facility_name, box_size, customer_id))
    conn.commit()

    return True

# Count the number of reservations per facility per box size
def get_reservation_count(facility_name, box_size):
    cur.execute('''
        SELECT COUNT(*) FROM Reservations
        WHERE facility_name = ? AND box_size = ?
    ''', (facility_name, box_size))
    return cur.fetchone()[0]


def main():
    while True:
        print("\nFrontDeskApp Menu:")
        print("1. Create a new storage customer")
        print("2. Store a box")
        print("3. Box retrieval")
        print("4. Check storage area availability")
        print("5. Check availability in other facilities")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            first_name = input("Enter customer's first name: ")
            last_name = input("Enter customer's last name: ")
            phone_number = input("Enter customer's phone number: ")
            create_customer(first_name, last_name, phone_number)
            print("Customer created successfully!")

        elif choice == "2":
            first_name = input("Enter customer's first name: ")
            last_name = input("Enter customer's last name: ")
            box_size = input("Enter box size (Small/Medium/Large): ")
            if store(box_size, first_name, last_name):
                print("Box stored successfully!")
            else:
                print("Box not accepted")

        elif choice == "3":
            first_name = input("Enter customer's first name: ")
            last_name = input("Enter customer's last name: ")
            box_size = input("Enter box size (Small/Medium/Large): ")
            if retrieve(box_size, first_name, last_name):
                print("Box retrieved successfully!")
            else:
                print("Box not retrieved")
                
        elif choice == "4":
            print(check_availability())

        elif choice == "5":
            print("Small: ", check_other_facility_availability("Small"))
            print("Medium: ", check_other_facility_availability("Medium"))
            print("Large: ", check_other_facility_availability("Large"))

        elif choice == "6":
            print("Exiting FrontDeskApp. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

    conn.close()


if __name__ == "__main__":
    main()
