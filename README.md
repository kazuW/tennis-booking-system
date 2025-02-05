# README.md

# Tennis Booking System

This project is a web application built using Streamlit for managing tennis court bookings and participant information. It allows users to view booking statuses, manage participant details, and handle reservations efficiently.

## Features

- **Booking Details Display**: View who is participating in reserved time slots and which courts are booked.
- **Participant Information Management**: Manage participant details such as name, contact information, and the number of participants for each booking.
- **User Authentication**: Secure login functionality to manage user sessions.

## Project Structure

```
tennis-booking-system
├── src
│   ├── app.py                  # Main entry point of the Streamlit 
├── data                        # Resavation Data
│   ├── bookings.csv
│   ├── participats.csv
└── README.md                    # Documentation for the project
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd tennis-booking-system
   ```

2. Install the required dependencies:
   ```
   poetry install
   ```

3. Run the application:
   ```
   ./venv/Sciypts/streamlit.exe run src/app.py 
      --server.headless true  #サーバーを自動起動しない
      --browser.gatherUsageStats false #データを自動取集しない
   
   ```

## Usage

- Access the application through the provided URL after running the Streamlit server.
- Use the booking form to reserve courts and manage participant information.
- Log in to access user-specific features.

## License

This project is licensed under the MIT License.