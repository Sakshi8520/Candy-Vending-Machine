#  Candy Vending Machine Backend

A backend API for a candy vending machine built with Flask. This project simulates how a vending machine manages users, wallets, candy inventory, purchases, tickets, and transaction history while keeping the database normalized through relationships.

## Features

- User registration and login
- JWT authentication
- Wallet created automatically for every user
- Candy inventory management
- Admin-only routes for adding and managing candies
- Purchase system with wallet balance checks
- Transaction history
- Ledger entries for every wallet transaction
- Ticket generation for purchases
- Database migrations using Flask-Migrate (Alembic)

## Tech Stack

- Python
- Flask
- SQLAlchemy
- Flask-Migrate
- Flask-JWT-Extended
- SQLite (currently), PostgreSQL (planned)

## Database

The project uses multiple related tables:

- User
- Wallet
- Ledger
- Candy
- Transaction
- Ticket

Relationships are implemented using SQLAlchemy ORM and foreign keys to maintain data integrity.

## Project Structure


app/
    admin/
    auth/
    models.py
    extensions.py
    config.py

migrations/
run.py
requirements.txt


## Future Improvements

- PostgreSQL support
- Redis caching
- Better error handling
- Unit tests
- Docker support
- REST API documentation

## Author

Built by Sakshi as a backend learning project while studying Flask, SQLAlchemy, authentication, and database design.
