# Agricultural Transport Rental Platform

A web application for renting agricultural transport. Transport owners can post their vehicles with detailed information, while users can browse and select from available options.

## Features

- User registration and authentication
- CRUD operations for transport listings
- Filtering transport by location, category, and price

## Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migration Tool**: Alembic

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up PostgreSQL database
5. Create a `.env` file with required environment variables:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/dbname
   SECRET_KEY=your_secret_key
   ```
6. Run database migrations:
   ```
   alembic upgrade head
   ```
7. Start the application:
   ```
   uvicorn app.main:app --reload
   ```

## API Documentation

Once the application is running, visit http://localhost:8000/docs for Swagger documentation.
