import json
import string
from datetime import datetime
from db import get_db_connection


class Customer:
    def __init__(self, name="", email="", phone_number="", student=0):
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.student = student

    def input_details(self):
        self.name = input("Enter name: ")
        self.email = input("Enter email address: ")
        self.phone_number = input("Enter phone number (10 digits): ")

        # Ensure phone number is 10 digits
        while len(self.phone_number) != 10 or not self.phone_number.isdigit():
            print("Phone number should contain exactly 10 digits.")
            self.phone_number = input("Enter phone number (10 digits): ")

        self.student = input("Is student? [0] No  [1] Yes: ")

        # Validate student status
        while self.student not in ['0', '1']:
            print("Invalid input. Please enter 0 for No or 1 for Yes.")
            self.student = input("Is student? [0] No  [1] Yes: ")

    def save_to_db(self):
        # Use centralized db connection from get_db_connection()
        mydb = get_db_connection()
        if mydb is None:
            print("Failed to connect to the database.")
            return

        mycursor = mydb.cursor()

        # SQL query to insert customer details
        insert = ("INSERT INTO customer (name, email, phone_number, student) "
                  "VALUES (%s, %s, %s, %s)")
        values = (self.name, self.email, self.phone_number, self.student)

        try:
            # Execute and commit
            mycursor.execute(insert, values)
            mydb.commit()
            print(mycursor.rowcount, "record inserted.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Close cursor and connection
            mycursor.close()
            mydb.close()


class Movie:
    def __init__(self, title="", genre="", rating="", imdb="", duration="", year_of_release=""):
        self.title = title
        self.genre = genre
        self.rating = rating
        self.imdb = imdb
        self.duration = duration
        self.year_of_release = year_of_release

    def input_details(self):
        self.title = input("Enter movie title: ")
        self.genre = input("Enter movie genre: ")
        self.rating = input("Enter movie rating: ")
        self.imdb = float(input("Enter imdb score: "))
        self.duration = int(input("Enter duration in minutes: "))
        self.year_of_release = int(input("Enter year of release: "))

    def save_to_db(self):
        # Use centralized db connection from get_db_connection()
        mydb = get_db_connection()
        if mydb is None:
            print("Failed to connect to the database.")
            return

        mycursor = mydb.cursor()

        # SQL query to insert movie details
        insert = ("INSERT INTO movie (title, genre, rating, imdb, duration, year_of_release) "
                  "VALUES (%s, %s, %s, %s, %s, %s)")
        values = (self.title, self.genre, self.rating, self.imdb, self.duration, self.year_of_release)

        try:
            # Execute and commit
            mycursor.execute(insert, values)
            mydb.commit()
            print(mycursor.rowcount, "record inserted.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Close cursor and connection
            mycursor.close()
            mydb.close()

    def get_showtimes(self):
        pass


class Theatre:
    def __init__(self, theatre_id="", screen="", layout=None):
        self.theatre_id = theatre_id
        self.screen = screen
        self.layout = layout if layout else {}   # ensures that self.layout always holds a valid dictionary

    def input_details(self):
        self.theatre_id = input("Enter theatre name: ")
        self.screen = input("Enter screen type (3D/2D): ")

        # Validate screen type
        while self.screen not in ['2D', '3D']:
            print("Invalid input. Please enter 2D/3D.")
            self.screen = input("Enter screen type (3D/2D): ")

        # Prompting user to input layout as a dictionary in JSON format
        layout_str = input("Enter layout as a dictionary (e.g., {\"A\": 10, \"B\": 12}): ")
        while True:
            try:
                self.layout = json.loads(layout_str)
                break  # Exit loop on success

            except json.JSONDecodeError:
                print("Invalid layout format. Please enter a valid dictionary in JSON format.")
                return

    def load_from_db(self, theatre_id):
        # Use centralized db connection from get_db_connection()
        mydb = get_db_connection()
        if mydb is None:
            print("Failed to connect to the database.")
            return False

        try:
            mycursor = mydb.cursor(dictionary=True)

            # SQL query to retrieve theatre details
            select = "SELECT * FROM theatre WHERE theatre_id = %s"
            mycursor.execute(select, (theatre_id,))
            result = mycursor.fetchone()

            # If a valid record is found, it loads the theatre ID, screen type, and layout into the object
            if result:
                self.theatre_id = result["theatre_id"]
                self.screen = result["screen"]
                layout_str = result["layout"]

                # Check if layout is empty or not
                if layout_str:
                    try:
                        self.layout = json.loads(layout_str)  # Parse the layout from string to dictionary
                    except json.JSONDecodeError:
                        print(f"Invalid JSON format in layout: {layout_str}")
                        return False
                else:
                    print("Layout is empty. Please provide a valid layout.")
                    return False

                return True
            else:
                print(f"No theatre found with ID: {theatre_id}")
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
        finally:
            # Close cursor and connection
            mycursor.close()
            mydb.close()

    def save_to_db(self):
        # Use centralized db connection from get_db_connection()
        mydb = get_db_connection()
        if mydb is None:
            print("Failed to connect to the database.")
            return

        mycursor = mydb.cursor()

        # Format layout as a valid JSON string
        layout_str = json.dumps(self.layout)  # Use json.dumps to ensure valid JSON format

        # SQL query to insert theatre details
        insert = ("INSERT INTO theatre (theatre_id, screen, layout) "
                  "VALUES (%s, %s, %s)")
        values = (self.theatre_id, self.screen, layout_str)

        try:
            # Execute and commit
            mycursor.execute(insert, values)
            mydb.commit()
            print(mycursor.rowcount, "record inserted.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Close cursor and connection
            mycursor.close()
            mydb.close()

    def get_seating_chart(self, selected_seats=None):
        if selected_seats is None:
            selected_seats = []

        print("             ====================================================")
        print("                                   SCREEN")
        print("             ====================================================")

        if not self.layout:
            print("Layout is empty. Please provide a valid layout.")
            return

        # Determine the maximum number of seats in any row
        max_range = max(self.layout.values())
        rows = len(self.layout)

        # seat letter - row label
        seat = string.ascii_uppercase

        for i in range(rows):
            row_letter = seat[i]

            # Get number of seats in the current row
            num_seats = self.layout.get(row_letter, 0)

            # Generate a list of seat numbers for a particular row
            seats = [f"{row_letter}{j}" for j in range(1, num_seats + 1)]

            # Mark the selected seats with **
            for selected_seat in selected_seats:
                if selected_seat in seats:
                    seats[seats.index(selected_seat)] = "**"

            # Converting seat numbers to a single string separated by spaces
            seat_row = '  '.join(seats)

            # Calculate padding to center the seat row
            seat_row_width = len(seat_row)
            padding = (max_range * 5 - seat_row_width) // 2

            print((' ' * padding) + seat_row)


class Showtime:
    def __init__(self, showtime_id="", movie_id="", theatre_id="", show_date="", start_time=""):
        self.showtime_id = showtime_id
        self.movie_id = movie_id
        self.theatre_id = theatre_id
        self.show_date = show_date
        self.start_time = start_time

    def input_details(self):
        self.showtime_id = input("Enter Show Time ID (e.g WE-N): ").strip().upper()
        self.movie_id = input("Enter movie id (e.g 701): ")
        self.theatre_id = input("Enter theatre id (e.g IIB): ").strip().upper()
        self.show_date = input("Enter date (dd/mm/yyyy): ")
        self.show_date = datetime.strptime(self.show_date, "%d/%m/%Y").date()
        self.start_time = input("Enter time (hh:mm): ")
        self.start_time = datetime.strptime(self.start_time, "%H:%M").time()

    def save_to_db(self):
        # Use centralized db connection from get_db_connection()
        mydb = get_db_connection()
        if mydb is None:
            print("Failed to connect to the database.")
            return

        mycursor = mydb.cursor()

        # SQL query to insert movie details
        insert = ("INSERT INTO show_time (showtime_id, movie_id, theatre_id, show_date, start_time) "
                  "VALUES (%s, %s, %s, %s, %s)")
        values = (self.showtime_id, self.movie_id, self.theatre_id, self.show_date, self.start_time)

        try:
            # Execute and commit
            mycursor.execute(insert, values)
            mydb.commit()
            print(mycursor.rowcount, "record inserted.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Close cursor and connection
            mycursor.close()
            mydb.close()


class Seat:
    def __init__(self, theatre):
        self.theatre = theatre  # Reference to the Theatre instance
        self.selected_seats = []

    def select_seat(self):
        while True:
            # Display the seating chart with the current selected seats
            self.theatre.get_seating_chart(self.selected_seats)

            # Prompt the user to select a seat
            selected_seat = input("\nSelect a seat (e.g., A1) or type 'q' to quit: ").strip().upper()

            if selected_seat.lower() == 'q':
                break

            # Extract row letter and seat number
            if len(selected_seat) > 1:
                row = selected_seat[0]
                number = selected_seat[1:]

                # Validate the seat selection
                if row in self.theatre.layout and number.isdigit() and 1 <= int(number) <= self.theatre.layout[row]:
                    if selected_seat not in self.selected_seats:
                        # Add the seat to the list of selected seats
                        self.selected_seats.append(selected_seat)

                        # Save the seat to the database
                        self.save_to_db(selected_seat, row, number)
                    else:
                        print("Seat already selected. Choose a different seat.")
                else:
                    print("Invalid seat number. Please try again.")
            else:
                print("Invalid seat format. Please try again.")

        if self.selected_seats:
            print(f"Your selected seats are: {self.selected_seats}")
        else:
            print("No selected seats.")

    def save_to_db(self, seat_id, row_letter, number):
        # Use centralized db connection from get_db_connection()
        mydb = get_db_connection()
        if mydb is None:
            print("Failed to connect to the database.")
            return

        mycursor = mydb.cursor()

        # SQL query to insert seat details
        insert = ("INSERT INTO seat (seat_id, theatre_id, row_letter, number) "
                  "VALUES (%s, %s, %s, %s)")
        values = (seat_id, self.theatre.theatre_id, row_letter, int(number))

        try:
            # Execute and commit
            mycursor.execute(insert, values)
            mydb.commit()
            print(f"Seat {seat_id} saved successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Close cursor and connection
            mycursor.close()
            mydb.close()


class Price:
    pass
