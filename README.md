# Store Brands API

A FastAPI application for managing store brands with CRUD operations.

## Prerequisites

- Python 3.7 or higher
- PostgreSQL installed and running
- Git (optional)

## Setup Instructions for Windows

### 1. Create Virtual Environment
Open Command Prompt in your project directory and run:
python -m venv venv

### 2. Activate Virtual Environment
venv\Scripts\activate
You should see `(venv)` at the start of your command prompt.

### 3. Install Dependencies
With virtual environment activated, run:
pip install fastapi uvicorn sqlalchemy asyncpg python-dotenv pydantic
pip freeze > requirements.txt

### 4. Database Setup
1. Install PostgreSQL from: https://www.postgresql.org/download/windows/
2. During installation:
   - Remember the password you set
   - Keep default port (5432)
   - Complete the installation

3. Create `.env` file in project root with:
DATABASE_USER=your_username
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_NAME=store_brands_db

### 5. Start the Application
Make sure virtual environment is activated (`(venv)` shows in prompt), then run:
uvicorn main:app --reload

The API will be available at:
- API URL: http://127.0.0.1:8000
- Documentation: http://127.0.0.1:8000/docs

## Daily Development

### Starting Development
1. Open Command Prompt in project directory
2. Activate virtual environment:
venv\Scripts\activate
3. Start the server:
uvicorn main:app --reload

### Stopping Development
1. Press CTRL+C to stop the server
2. Type `deactivate` to exit virtual environment

## Project Structure
fastapi-tutorial/
├── app/
│ ├── api/ # API routes
│ ├── domain/ # Domain models
│ ├── infrastructure/ # Database setup
│ └── use_cases/ # Business logic
├── .env # Environment variables (not in git)
├── .gitignore
├── main.py # Application entry point
└── requirements.txt # Project dependencies

## API Endpoints

- `POST /store-brands` - Create new store brand
- `GET /store-brands` - List all store brands
- `GET /store-brands/{store_brand_id}` - Get specific store brand
- `PUT /store-brands/{store_brand_id}` - Update store brand
- `DELETE /store-brands/{store_brand_id}` - Delete store brand

## Important Notes

- Always activate virtual environment before working
- Never commit `.env` file
- If you install new packages:
pip freeze > requirements.txt