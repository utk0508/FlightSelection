'''
Intention: This program allows user's to book a flight between Toronto, Vancouver, and Calagary on either December
20th or 22nd. User begins by inputting departure location and destination and program displays available flights 
from database. The user then selects a flight and the program generates a seat map so the user can pick a seat. 
The program stores user's chosen seat. The user is then able to select any flight add-ons, which are added to the flight
cost total. The user must then input personal information (Name, DOB, Country of Residence, Gender, and Nationality) 
and the program store's this information in a traveller database. The user is then directed to the payment page where
they can verify their flight information and enter their payment information. Finally the user is directed to the 
flight confirmation page. 
'''

from flask import Flask, render_template, session, request, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'group19'  # Secret key for session management

#Sample flights for database creation
sample_flights = [
    ('Toronto', 'Vancouver', 'TV123', '2024-12-20 12:00', '2024-12-20 17:15', 112 ),
    ('Toronto', 'Calgary', 'TC123', '2024-12-20 09:00', '2024-12-20 13:25', 289 ),
    ('Vancouver', 'Toronto', 'VT123', '2024-12-20 06:00', '2024-12-20 10:35', 89 ),
    ('Vancouver', 'Calgary', 'VC123', '2024-12-20 13:30', '2024-12-20 15:00', 128 ),
    ('Calgary', 'Toronto', 'CT123', '2024-12-20 22:00', '2024-12-20 13:55', 176 ),
    ('Calgary', 'Vancouver', 'CV123', '2024-12-20 07:00', '2024-12-20 08:40', 432 ),
    ('Toronto', 'Vancouver', 'TV456', '2024-12-22 18:00', '2024-12-22 23:15', 103 ),
    ('Toronto', 'Calgary', 'TC456', '2024-12-22 09:30', '2024-12-22 13:55', 135 ),
    ('Vancouver', 'Toronto', 'VT456', '2024-12-22 07:00', '2024-12-22 11:35', 333 ),
    ('Vancouver', 'Calgary', 'VC456', '2024-12-22 15:00', '2024-12-22 16:30', 342 ),
    ('Calgary', 'Toronto', 'CT456', '2024-12-22 12:00', '2024-12-22 15:55', 178 ),
    ('Calgary', 'Vancouver', 'CV456', '2024-12-22 02:00', '2024-12-22 03:40', 200 ),
]

#Connect to data base 
def init_db(database_path='user_data.db'):
    #Connect to sqlite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    #Create user table if it does not exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        nationality TEXT,
        residence TEXT,
        gender TEXT,
        seat_number TEXT,
        flightNumber TEXT
    )
    ''')

    #Create flight table if it does not exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_location TEXT,
        to_location TEXT,
        flight_number TEXT,
        departure_time TEXT,
        arrival_time TEXT,
        price INT
                
    )
    ''')

    #Insert sample flights if table is empty
    cursor.execute('SELECT COUNT(*) FROM flights')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO flights (from_location, to_location, flight_number, departure_time, arrival_time, price)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_flights)   

    #Commit chanegs and close connection
    conn.commit()
    conn.close()

#Route for home page (flight search)
@app.route('/')
def home():
    return render_template('searchFlights.html')

#Route for flight search
@app.route('/search_flights', methods=['POST'])
def search_flights():
    # Get search parameters from the form
    from_location = request.form.get('from_location')
    to_location = request.form.get('to_location')
    
    #Store the search locations in session
    session['from_location'] = from_location
    session['to_location'] = to_location

    print(f"Retrieved from_location: {from_location}")
    print(f"Retrieved to_location: {to_location}")
    
    #Redirect to flight display page
    return redirect(url_for('display_flights'))

#Route to display flights based on user's search
@app.route('/display_flights', methods=['GET', 'POST'])
def display_flights():
    # Retrieve the from and to locations from session
    from_location = session.get('from_location')
    to_location = session.get('to_location')

    print(f"Retrieved from_location: {from_location}")
    print(f"Retrieved to_location: {to_location}")

    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    
    #Connect to database and find available flights matching user's search
    cursor.execute('''
    SELECT flight_number, departure_time, arrival_time, price
    FROM flights
    WHERE from_location = ? AND to_location = ? 
    ''', (from_location, to_location))
    
    flights = cursor.fetchall()
    conn.close()
    
    if request.method == 'POST':
        #Get selected flight number
        flight_number = request.form['flight_number']
        
        #Find selected flight in list
        selected_flight = next((flight for flight in flights if flight[0] == flight_number), None)
       
        #Store selected flight details in session
        if selected_flight:
            session['flight_selected'] = {
                'flight_number': selected_flight[0],
                'departure_time': selected_flight[1],
                'arrival_time': selected_flight[2],
                'price': selected_flight[3]
            }
            return redirect(url_for('seat_selection'))

    #Render template to display flights
    return render_template('displayFlights.html', flights=flights, from_location=from_location, to_location=to_location)

#Generate a seat map for flight
def generate_seat_map():
    rows = 15
    columns = ['A', 'B', 'C', 'D', 'E', 'F']
    seat_map = []

    for row in range(1, 16):
        for col in columns:
            seat = f"{row}{col}"
            seat_class = 'first-class-seat' if row <= 4 else 'economy-seat'
            seat_map.append({
                'seat': seat,
                'class': seat_class,
                'available': True  
            })
    return seat_map

#Route for seat selection 
@app.route('/seat_selection', methods=['GET', 'POST'])
def seat_selection():
    flight_number = session.get('flight_selected', {}).get('flight_number')
    
    #Verify that a flight has been selected
    if not flight_number:
        return "Flight not selected", 400

    if request.method == 'POST':
        selected_seat = request.form.get('selected_seat')
        if selected_seat:
            #Save selected seat in session
            session['selected_seat'] = selected_seat  
            return redirect(url_for('add_ons'))
        else:
            return render_template('seat_selection.html', error="Please select a seat.")

    #Get unavailable seats from the database
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT seat_number FROM users WHERE flightNumber = ?", (flight_number,))
    unavailable_seats = [row[0] for row in cursor.fetchall()]
    conn.close()

    #Generate seat map and mark unavailable seats
    seat_map = generate_seat_map()
    for seat in seat_map:
        if seat['seat'] in unavailable_seats:
            seat['available'] = False

    return render_template('seat_selection.html', seat_map=seat_map)

#Route to add-ons page 
@app.route('/add_ons',methods = ['GET', 'POST'])
def add_ons():
    return render_template('addOns.html')

def is_valid_country(country_name):
    # Connect to the database
    conn = sqlite3.connect('countries.db')
    cursor = conn.cursor()
    
    # Check if the country is in the database
    cursor.execute('SELECT name FROM countries WHERE name = ?', (country_name,))
    result = cursor.fetchone()
    
    conn.close()
    return result is not None

#Route for traveller's information
@app.route('/info', methods=['GET', 'POST'])
def traveller_info():
    if request.method == 'POST':
        #Get traveller's info from form
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        nationality = request.form['nationality']
        residence = request.form['residence']
        gender = request.form['gender']
        flight_number = session.get('flight_selected', {}).get('flight_number')
        seat_number = session.get('selected_seat')

        valid_residence = is_valid_country(residence)

        if not valid_residence:
            return render_template('travellerInfo.html', 
                               error_message = "Invalid country entered. Please check your inputs.")

        #Insert traveller infor into database
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO users (first_name, last_name, nationality, residence, gender, flightNumber, seat_number)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, nationality, residence, gender, flight_number, seat_number))
        conn.commit()
        conn.close()

        return redirect(url_for('make_payment'))

    return render_template('travellerInfo.html')

#Route for making payment
@app.route('/make_payment', methods=['GET', 'POST'])
def make_payment():
    flight_selected = session.get('flight_selected')
    
    #Log the flight data to check if it's correctly stored in session
    print(f"Flight Selected: {flight_selected}")
    
    #Verify flight has been selected
    if not flight_selected:
        return redirect(url_for('home'))
    
    return render_template('makePayment.html', flight=flight_selected)

#Route for flight confirmation
@app.route('/confirm', methods=['GET', 'POST'])
def confirmation():
    return render_template('confirmation.html')


def create_app():
    return app

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
