# User Management API

A REST API for user management built with FastAPI, SQLite, and following hexagonal architecture principles.

## Features

- User authentication with JWT
- User CRUD operations with pagination
- Hexagonal architecture (ports and adapters)
- Comprehensive unit tests
- OpenAPI documentation
- Docker support

## Project Structure

The project follows a hexagonal architecture pattern with the following layers:

- **Domain**: Contains business entities, repository interfaces, and business rules
- **Application**: Contains use cases and DTOs for the application logic
- **Infrastructure**: Contains implementations of repositories, database connections, and web API

## Installation

### Using Docker (Recommended)

1. Clone the repository:

```bash
git clone https://github.com/jvictor-am/user_management_api.git
cd user_management_api
```

2. Start the application with Docker Compose:

```bash
docker-compose up -d
```

The API will be available at http://localhost:8000

### Manual Installation

1. Clone the repository:

```bash
git clone https://github.com/jvictor-am/user_management_api.git
cd user_management_api
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables (optional):

Create a `.env` file in the root directory with the following content:

```
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. Run the application:

```bash
uvicorn src.main:app --reload
```

## API Documentation

After starting the application, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /auth/login` - Authenticate user and get JWT token
- `POST /auth/login/json` - Authenticate user with JSON and get JWT token

### Users

- `POST /users/` - Create a new user
- `GET /users/` - List all users (paginated)
- `GET /users/{user_id}` - Get a specific user
- `PUT /users/{user_id}` - Update a user
- `DELETE /users/{user_id}` - Delete a user

## Running Tests

### With Docker

```bash
docker-compose exec api pytest
```

### Without Docker

```bash
pytest
```
