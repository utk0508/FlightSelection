import pytest
from flask import Flask, render_template, session, request, redirect, url_for
import sqlite3
from app import app, init_db, sample_flights
import os
from app import generate_seat_map

@pytest.fixture

#Create a test client
def client():
    with app.test_client() as client:
        yield client

DATABASE_PATH = 'test_user_data.db'

# Test when user selects same location as departure location and destination
def test_valid_location_selection(client):
    response = client.post('/search_flights', data={
        'from_location': 'Toronto',
        'to_location': 'Vancouver' #different to_loaction
    })
    assert response.status_code == 302 # Check that the response redirects

# Test when user selects same location as departure location and destination
def test_invalid_location_selection(client):
    response = client.post('/search_flights', data={
        'from_location': 'Toronto',
        'to_location': 'Toronto' #same to_location
    })

    assert response.status_code == 302 # Check that the response redirects


#Test that any valid country input is accepted.
def test_valid_countryofresidence(client):
    print("\nTesting that a valid country of residence is accepted.")
    response = client.post('/info', data={
        'first_name': 'abc',
        'last_name': 'xyz',
        'residence': 'Canada',
        'nationality': 'Can',
        'gender': 'Female'
    })
    print(f"Response status code: {response.status_code}")

    # Check the response to ensure valid country names are accepted
    assert response.status_code == 302, "Expected redirect (302) on valid input."  # Check that the response redirects
    print("Test passed: Valid country of residence input was accepted and redirected successfully.")

#Test that any invalid country input is not accepted.
def test_invalid_countryofresidence(client):
    response = client.post('/info', data={
        'first_name': 'abc',
        'last_name': 'xyz',
        'residence': 'Table',
        'nationality': 'Can',
        'gender': 'Female'
    })

    # Check the response to ensure valid country names are accepted
    assert response.status_code == 200  # Ensure form submission is successful

# Valid location search with available flights
def test_display_flights_with_available_flights(client):
    with client.session_transaction() as session:
        session['from_location'] = 'Toronto'
        session['to_location'] = 'Vancouver'

    response = client.get('/display_flights')
    assert response.status_code == 200
    assert b'Available Flights from Toronto to Vancouver' in response.data  # Checks header text
    assert b'Select' in response.data  # Checks for flight selection options
    assert b'Flight Number' in response.data  # Ensures table header is displayed

# Valid location search with no available flights
def test_display_flights_with_no_flights(client):
    with client.session_transaction() as session:
        session['from_location'] = 'Toronto'
        session['to_location'] = 'NonexistentCity'  # Assuming this city pair does not exist

    response = client.get('/display_flights')
    assert response.status_code == 200
    assert b'No flights found.' in response.data  # Confirms message for no flights is displayed

#Test that a seat map generates properly
def test_generate_seat_map():
    seat_map = generate_seat_map()
    
    # Check total seats generated (15 rows * 6 columns)
    assert len(seat_map) == 90
    
    # Check first 4 rows are first-class seats
    for seat in seat_map[:24]:  # First 4 rows (4 * 6 = 24 seats)
        assert seat['class'] == 'first-class-seat'
    
    # Check remaining rows are economy seats
    for seat in seat_map[24:]:  # Remaining rows should be economy
        assert seat['class'] == 'economy-seat'

#Helper function to set up unavailable seats in the database for testing
def setup_unavailable_seat(flight_number, seat_number):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (first_name, last_name, nationality, residence, gender, flightNumber, seat_number) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   ('Test', 'User', 'TestCountry', 'TestCountry', 'Other', flight_number, seat_number))
    conn.commit()
    conn.close()

# GET request without selecting a flight
def test_seat_selection_without_flight_selected(client):
    
   print("\nTesting behavior when accessing seat selection without selecting a flight.")
   
   response = client.get('/seat_selection')
   
   print(f"Response status code: {response.status_code}")
   
   assert response.status_code == 400 , "Expected a 400 Bad Request response for missing flight selection."
   print("Test passed: Server returned 400 Bad Request as expected.")
   
   assert b"Flight not selected" in response.data  # Error message when no flight is selected

# GET request with unavailable seats
def test_seat_selection_with_unavailable_seats(client):

    print("\nTesting seat selection with unavailable seats.")
    
    # Set up session with selected flight
    flight_number = 'TV123'
    with client.session_transaction() as session:
        session['flight_selected'] = {'flight_number': flight_number}
    
    # Insert unavailable seat into database
    setup_unavailable_seat(flight_number, '1A')
    print(f"Seat '1A' marked as unavailable for flight {flight_number} in the database.")

    response = client.get('/seat_selection')
    assert response.status_code == 200  # Page should load successfully
    
    # Check for the presence of an unavailable seat in the seat map
    assert b'1A' in response.data  # Check if seat '1A' is present
    assert b'unavailable-seat' in response.data  # Check if 'unavailable-seat' class is in the response to mark unavailability
    print("Seat '1A' correctly marked as unavailable in the seat selection map.")

    response_with_seat = client.post('/seat_selection', data={})
    assert response_with_seat.status_code == 200

def test_seat_selection_with_available_seats(client):
    with client.session_transaction() as session:
        session['flight_selected'] = {'flight_number': 'TV123'}
    response = client.post('/seat_selection', data={'selected_seat': 'A1'})
    assert response.status_code == 302

    with client.session_transaction() as session:
        assert session.get('selected_seat') == 'A1'
    assert response.status_code == 302 #Check for a redirect
    assert response.headers['Location'] == '/add_ons'

@pytest.fixture
def setup_database():
    # Set up and tear down the database for testing
    init_db(DATABASE_PATH)
    yield
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS flights")
    conn.commit()
    conn.close()

#Check if tables are created
def test_tables_created(setup_database):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    #Check if `users` table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    users_table = cursor.fetchone()
    assert users_table is not None  # Table should exist
    
    #Check if `flights` table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='flights'")
    flights_table = cursor.fetchone()
    assert flights_table is not None  # Table should exist
    
    conn.close()

#Check if flights table is populated with sample data if empty
def test_flights_table_populated_if_empty(setup_database):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Verify sample flights have been inserted
    cursor.execute("SELECT COUNT(*) FROM flights")
    flight_count = cursor.fetchone()[0]
    assert flight_count == len(sample_flights)  # Should match the sample data count
    
    conn.close()

#Test user info with valid inputs.
def test_valid_payment(client):
    response = client.post('/make_payment', data={
        'card_number': '0123456789123456', #add valid credit card info (16 digits)
        'expiry_date': '01/01/0001', #add valid expiry date
        'cvv': '123' #add valid cvv (3 digits)
    })
    assert response.status_code == 302  # Check that the response redirects

#Test user info with invalid inputs.
def test_invalid_payment(client):
    response = client.post('/make_payment', data={
        'card_number': '0123456789', #add invalid credit card info (less than 16 digits)
        'expiry_date': '01', #add invalid expiry date
        'cvv': '13' #add invalid cvv (less than 3 digits)
    })
    assert response.status_code == 302 # Check that the response redirects


#Test that selecting up to two bags add-ons are accepted.
def test_valid_bags(client):
    response = client.post('/add_ons', data={
        'firstClass': 'on',  # First Class add-on
        'insurance': 'on',   # Insurance add-on
        'baggage': '2'       # add 2 pieces of baggage
    })
    assert response.status_code == 200  # Check that the response redirects

#Test that when user selects a flight they are redirected to seat selection page 
def test_select_flight(client):

    print("\nTesting flight selection and redirection to seat selection page.")
    
    #Search for a valid fligh
    with client.session_transaction() as session:
        session['from_location'] = 'Toronto'
        session['to_location'] = 'Vancouver'
    print("Session with departure as Toronto and destination as Vancouver.")

    #Get available flights
    response = client.get('/display_flights')
    print(f"Response status code for displaying flights: {response.status_code}")
    assert response.status_code == 200, "Expected status code 200 for flight display."
    print("Available flights page loaded successfully.")
    assert b'Available Flights from Toronto to Vancouver' in response.data
    
    #User selects flight
    response = client.post('/display_flights', data={
        'flight_number': 'TV123'  
    })
    
    #Check if user is redirected to seat selection page
    print(f"Response status code after selecting flight: {response.status_code}")
    assert response.status_code == 302, "Expected a 302 redirect after selecting a flight."
    assert response.location.endswith('/seat_selection')

    #Check if flight info is stored in the session
    with client.session_transaction() as session:
        assert session.get('flight_selected') == {
            'flight_number': 'TV123',
            'departure_time': '2024-12-20 12:00',
            'arrival_time': '2024-12-20 17:15',
            'price': 112
        }
    print("Test passed: Flight information stored correctly in session.")

#Test flight confirmation route
def test_confirmation_route(client):
    #Send a GET request to the '/confirm' route
    response = client.get('/confirm')
    
    #Check response status code 
    assert response.status_code == 200
    
    #Check if the 'confirmation.html' template is rendered
    assert b'Confirmation' in response.data  

    #Test route for making payment
def test_make_payment_with_selected_flight(client):
    #Set up session with flight data 
    with client.session_transaction() as session:
        session['flight_selected'] = {
            'flight_number': 'TV123',
            'departure_time': '2024-12-20 12:00',
            'arrival_time': '2024-12-20 17:15',
            'price': 112
        }

    #Send a GET request to the '/make_payment' route
    response = client.get('/make_payment')
    
    #Check response status code
    assert response.status_code == 200
    
    #Check if the 'makePayment.html' template is rendered
    assert b'Make Payment' in response.data 
    
    # Check for the flight number in the response data 
    assert b'TV123' in response.data
    assert b'2024-12-20 12:00' in response.data




