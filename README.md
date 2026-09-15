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
- **Nginx** *(deployment work in progress)*

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

The application reads database configuration and secrets from environment variables rather than storing credentials in the repository.

---

## Production & Deployment Learning

I am currently working through running the Flask application in a more production-oriented setup using:

- Gunicorn as the WSGI server
- Nginx as a reverse proxy
- PostgreSQL as the database
- Gunicorn worker/thread configuration
- WSGI application configuration
- Local Linux/WSL deployment environment

The deployment setup is an ongoing part of the project as I learn how the individual components work together.

---

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

---

## Future Improvements

Planned improvements include:

- **pytest** and automated API testing
- **Redis** for token blocklists and rate limiting
- Service-layer separation for business logic
- Docker containerization
- API documentation
- Further production deployment improvements
- More robust production configuration

---

## Project Status

This project is actively developed.

The `main` branch contains the portfolio-ready version, while the `development` branch contains ongoing development and experimentation.

The goal is to continue evolving the project while using it to learn and apply increasingly production-oriented backend concepts.
