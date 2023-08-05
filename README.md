# FrontDeskApp Documentation
FrontDeskApp is a simple storage management application that allows you to create new storage customers, store boxes, retrieve boxes, and check the availability of the storage area.

## Prerequisites
- Python 3.11 or higher
- sqlite3

## Installation
To install FrontDeskApp: 
1. Clone the git repo:
    ```
    git clone add origin https://github.com/mryoshizaki/FrontDeskApp.git
    ```
2. Change directory to the FrontDeskApp directory:
    ```
    cd FrontDeskApp
    ```
3. Run the FrontDeskApp script:
    ```
    python FrontDeskApp.py
    ```

## Usage
Upon running the script, the FrontDeskApp interactive menu will start. You can then select from the following options:

    1. Create a new storage customer
    2. Store a box
    3. Box retrieval
    4. Check storage area availability
    5. Check availability at other facilities
    6. Exit

The following options are available in the FrontDeskApp program:
- Create a new storage customer: This option allows you to create a new storage customer. You need to enter the customer's first name, last name, and phone number.

- Store a box: This option allows you to store a box in the storage facility. You need to enter the box size (small, medium, or large) and the customer's first name and last name.

- Box retrieval: This option allows you to retrieve a box from the storage facility. You need to enter the box size and the customer's first name and last name.

- Check storage area availability: This option allows you to check the availability of the storage area for every box size.

- Check availability in other facilities: This option allows you to check the availability of other storage facilities for a specific box size.

- Exit: This option allows you to exit the FrontDeskApp program.

## Example
The following example shows how to create a new storage customer, store a box, and retrieve a box:

```
$ python FrontDeskApp.py

FrontDeskApp Menu:
1. Create a new storage customer
2. Store a box
3. Box retrieval
4. Check storage area availability
5. Check availability in other facilities
6. Exit

Enter your choice (1-6): 1

Enter the customer's first name: Michael
Enter the customer's last name: Scott
Enter the customer's phone number: 123-456-7890

Customer successfully added.

Enter your choice (1-6): 2

Enter the customer's first name: Michael
Enter the customer's last name: Scott
Enter the box size: Small

Box successfully stored.

Enter your choice (1-6): 3

Enter the customer's first name: Michael
Enter the customer's last name: Scott
Enter the box size: Small
Box successfully retrieved.
Enter your choice (1-6): 6
Exiting FrontDeskApp...
```
