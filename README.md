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

## Security Features

The API includes several security enhancements:

### Authentication Security
- **Argon2id Password Hashing**: Industry-leading password hashing with tunable memory, iterations and parallelism
- **Authentication Logging**: All login attempts (successful and failed) are tracked with timestamps and IP addresses
- **Rate Limiting**: Protects against brute-force attacks by limiting request frequency
- **JWT Token Security**:
  - UUID-based token identifiers to prevent token reuse
  - Timezone-aware expiration handling
  - HMAC-SHA256 signature algorithm
- **BCrypt Fallback**: Compatible with older password hashes while upgrading to newer algorithms
- **Secure Authentication Routes**: 
  - Form-based and JSON-based authentication endpoints
  - Protected endpoints using OAuth2 bearer token scheme

### API Security
- **CORS Protection**: Configurable Cross-Origin Resource Sharing
- **SQLite Security**: Protections against SQL injection via SQLAlchemy ORM
- **Input Validation**: Comprehensive validation on all input fields using Pydantic

## Using the Postman Collection

The project includes a Postman collection for easy API testing:

### Importing the Collection

1. Open Postman
2. Click "Import" in the top left corner
3. Select the file: `docs/postman_collection.json`
4. Click "Import"

### Setting Up the Environment

1. Click "Environments" in the left sidebar
2. Click "Create Environment" and name it "User Management API"
3. Add two variables:
   - `baseUrl`: Set value to `http://localhost:8000`
   - `token`: Leave empty (will be filled automatically)
4. Click "Save"
5. Select this environment from the dropdown in the top-right corner

### Testing the API

1. **Create a user**:
   - Use the "Create User" request
   - Provides username, email, and password in the request body
   
2. **Login**:
   - Use either "Login" or "Login with JSON" request
   - Provide your credentials
   - The authentication token will be automatically saved to the environment

3. **Access protected endpoints**:
   - All requests will automatically use the saved token
   - Try "List Users" to verify your authentication is working
   - Use "Get User by ID" with the appropriate user ID
   - Experiment with updating and deleting users

The collection automatically handles authentication tokens, making it easy to test all API endpoints.

## Running Tests

### With Docker

```bash
# Run all tests - Note: Uses a separate in-memory database
docker compose exec api pytest

# Run specific test file
docker compose exec api pytest tests/test_user_service.py

# Run tests with coverage report
docker compose exec api pytest --cov=src tests/
```

### Without Docker

```bash
# Make sure you're in the project root directory
export PYTHONPATH=$PYTHONPATH:$(pwd)
pytest
```

### Testing Note
The test suite uses an isolated in-memory SQLite database that's separate from 
your production database. Each test function gets its own database instance that
is completely destroyed after the test runs. No test data should ever appear in
your API's production database.

## Database Access

### Accessing SQLite CLI in Docker Container

To access and query the database directly:

```bash
docker compose exec api bash

# Check if SQLite is installed
which sqlite3

# If SQLite is not installed, install it
if [ ! -f /usr/bin/sqlite3 ]; then
    apt-get update
    apt-get install -y sqlite3
fi

# Inside the container, access the SQLite database
sqlite3 /app/data/user_management.db

# SQLite commands:
.headers on
.tables
SELECT * FROM users;
.schema users
.quit
```

## Test Coverage Reports

### Terminal Report

```bash
# Generate detailed coverage report in terminal
docker compose exec api pytest --cov=src --cov-report=term-missing tests/
```

### HTML Report

```bash
# Generate HTML coverage report
docker compose exec api pytest --cov=src --cov-report=html tests/

# If running locally, open the report
# For Docker, you need to copy it out of the container first
docker cp user-management-api:/app/htmlcov ./htmlcov
# Then open htmlcov/index.html in your browser
```
