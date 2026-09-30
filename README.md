# Candy Vending Machine API

A Flask-based backend for a candy vending machine system, built to explore real-world backend development concepts such as authentication, database design, transactions, validation, authorization, and production-oriented deployment.

The project started with SQLite and has since been migrated to PostgreSQL using Flask-Migrate/Alembic. I am also working through deploying the application with Gunicorn and Nginx.

---


## Features

### Authentication & Authorization
- User registration and login
- JWT authentication
- Access and refresh tokens
- Token revocation / blocklist
- Admin authorization with custom decorators

### Candy & Inventory
- Candy inventory management
- Stock handling
- Candy purchasing
- Candy image uploads
- Admin stock management

### Wallet & Transactions
- User wallets
- Balance management
- Purchase transactions
- Transaction/ledger records
- Purchase tickets
- Purchase history

### Validation & Error Handling
- Request validation with Marshmallow
- Custom application exceptions
- Centralized error handling
- Validation and HTTP error responses
- Rate limiting

### Database
- SQLAlchemy ORM
- PostgreSQL
- Flask-Migrate / Alembic
- Database relationships
- Database migrations
- Migrated the project from SQLite to PostgreSQL

---

## Tech Stack

- **Python**
- **Flask**
- **SQLAlchemy / Flask-SQLAlchemy**
- **PostgreSQL**
- **Flask-Migrate / Alembic**
- **Flask-JWT-Extended**
- **Marshmallow**
- **Flask-Limiter**
- **Gunicorn**
- **Nginx**

---


## Setup

### 1. Clone the repository

git clone https://github.com/Sakshi8520/Candy-Vending-Machine.git
cd Candy-Vending-Machine

### 2. Create and activate a virtual environment

Windows:

python -m venv venv
venv\Scripts\activate

Linux / macOS:

python3 -m venv venv
source venv/bin/activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Configure environment variables

Create a `.env` file in the project root:

DATABASE_URL=postgresql://username:password@localhost:5432/candy_db
JWT_SECRET_KEY=your-secret-key
FLASK_ENV=development

Replace the database credentials with your local PostgreSQL configuration.

### 5. Run database migrations

flask db upgrade

### 6. Start the application

python run.py

The API will be available at:

http://127.0.0.1:5000

---

## Architecture

The application uses Flask's application factory pattern and separates functionality using Blueprints.

The backend currently includes separate areas for:

- Authentication and user operations
- Administrative operations
- Database models and relationships
- Validation schemas
- Custom exceptions
- JWT token handling
- Middleware
- Configuration and environment management

Business operations such as purchases, wallet changes, stock handling, and transactions are handled on the backend rather than relying on client-side logic.

---

## Database

The project was initially developed using SQLite and later migrated to PostgreSQL.

Flask-Migrate and Alembic are used to manage database schema changes.

The application uses SQLAlchemy's database connection pooling to manage PostgreSQL connections efficiently. I explored and tested concepts including:

- Connection lifecycle
- Connection pool size
- Maximum overflow connections
- Active/current connections
- Connection checkout and check-in
- Connection timeouts
- Connection recycling
- Pool exhaustion
- Connection behavior under multiple requests

The application reads database configuration and secrets from environment variables rather than storing credentials in the repository.

---

## Production & Deployment

The application is being developed and tested in a production-oriented setup using:

- Gunicorn as the WSGI server
- Nginx as a reverse proxy
- PostgreSQL as the database
- Gunicorn worker configuration
- WSGI application configuration
- Nginx HTTPS/TLS configuration
- A local CA certificate for HTTPS testing
- HTTP to HTTPS redirection
- Security headers including HSTS
- Local Linux/WSL deployment environment

This setup is primarily a learning and development environment used to understand how a Flask application is served and secured behind Nginx.

---

## Testing

[![Tests](https://github.com/Sakshi8520/Candy-Vending-Machine/actions/workflows/tests.yml/badge.svg)](https://github.com/Sakshi8520/Candy-Vending-Machine/actions/workflows/tests.yml)

The project uses pytest for automated API testing.

Current tests cover:

- User login
- Candy purchase flow
- Purchase-related database behavior

Implemented CI with GitHub Actions to automatically run pytest against a PostgreSQL test database on pushes and pull requests

---

The test environment uses a separate PostgreSQL database to avoid interfering with development data.

## What I'm Learning Through This Project

This project has been used to go beyond basic Flask CRUD applications and understand how backend systems work internally.

Some of the concepts explored include:

- REST API design
- Authentication and authorization
- JWT lifecycle
- SQLAlchemy relationships and loading strategies
- Database transactions and consistency
- PostgreSQL
- Database migrations
- Error handling and custom exceptions
- Middleware
- Logging
- Rate limiting
- Pagination and filtering
- WSGI servers
- Gunicorn workers and threads
- Reverse proxies
- Application configuration and environment variables
- Automated API testing with pytest
- Database connection lifecycle and connection pooling
- Pool size, overflow, checkout/check-in, timeouts, and recycling
- HTTPS/TLS
- CA certificates and certificate validation
- Nginx TLS termination
- HTTP to HTTPS redirection
- HSTS

---

## Future Improvements

Planned improvements include:

- Expand pytest API test coverage
- Redis for token blocklists and rate limiting
- Service-layer separation for business logic
- Docker containerization
- API documentation
- Further production deployment improvements
- More robust production configuration
- Database performance and production tuning
---

## Project Status

This project is actively developed.

The `main` branch contains the portfolio-ready version, while the `development` branch contains ongoing development and experimentation.

The goal is to continue evolving the project while using it to learn and apply increasingly production-oriented backend concepts.
