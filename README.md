# Event Management API

## Overview
The Event Management API is a Django-based backend application designed to manage events and user registrations. It provides a robust set of features for creating, updating, and managing events, as well as handling user authentication and email notifications. The API is built with REST principles and includes JWT-based authentication for secure access.

## Features
- **Event Management**: Create, update, delete, and list events.
- **User Management**: Register users and authenticate them using JWT tokens.
- **Event Registration**: Allow users to register for events and receive email notifications.
- **Email Notifications**: Automatically send confirmation emails upon successful event registration or status updates.
- **API Documentation**: Interactive API documentation generated with Swagger (via `drf-spectacular`).
- **Search and Filtering**: Search and filter events based on title, location, organizer ID, or flexible date formats (year, month, or exact date).
- **Task Queue**: Asynchronous email notifications using Celery and Redis.
- **Permission Checks**: Ensure only event organizers can update or delete their events.

## Technologies Used
- **Backend Framework**: Django and Django REST Framework
- **Authentication**: JWT (via `djangorestframework-simplejwt`)
- **Task Queue**: Celery with Redis as the message broker
- **Database**: PostgreSQL
- **Email Testing**: MailDev for local email testing
- **Containerization**: Docker and Docker Compose
- **API Documentation**: Swagger (via `drf-spectacular`)

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed
- Python 3.11 or higher (if running locally without Docker)

### Local Development with Docker
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/jointoit.git
   cd jointoit
   ```

2. Create a `.env` file based on the `.env.sample` file:
   ```bash
   cp .env.sample .env
   ```

3. Update the `.env` file with your configuration (e.g., database credentials, email settings).

4. Build and start the Docker containers:
   ```bash
   docker-compose up --build
   ```

5. Access the application:
   - API: `http://127.0.0.1:8000/`
   - MailDev (for email testing): `http://127.0.0.1:1080/`

### Local Development without Docker
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Apply migrations:
   ```bash
   python manage.py migrate
   ```

3. Run the development server:
   ```bash
   python manage.py runserver
   ```

4. Access the API at `http://127.0.0.1:8000/`.

## Docker
1. Build the image:
   ```bash
   docker build -t event-management .
   ```

2. Run the container:
   ```bash
   docker-compose up
   ```

3. Access the API at `http://127.0.0.1:8000/`.

## Authentication

### Obtain JWT Token
Send a POST request to `/api/token/` with the following payload:
```json
{
    "username": "your_username",
    "password": "your_password"
}
```
Response:
```json
{
    "access": "your_access_token",
    "refresh": "your_refresh_token"
}
```

## API Endpoints
- **Events**:
  - `GET /events/`: List all events with optional filters:
    - `title`: Partial match for event title.
    - `date`: Filter by year (`YYYY`), year and month (`YYYY-MM`), or exact date (`YYYY-MM-DD`).
    - `location`: Partial match for event location.
    - `organizer`: Filter by organizer ID (exact match).
  - `POST /events/`: Create a new event (authenticated users only).
  - `GET /events/{id}/`: Retrieve event details.
  - `PUT /events/{id}/`: Update an event (only the organizer can update).
  - `PATCH /events/{id}/`: Partially update an event (only the organizer can update).
  - `DELETE /events/{id}/`: Delete an event (only the organizer can delete).

- **Event Registration**:
  - `POST /events/{id}/register/`: Register for an event.
  - `GET /registrations/`: List user registrations.
  - `GET /registrations/{id}/`: Retrieve a registration by ID.
  - `PUT /registrations/{id}/`: Update a registration by ID.
  - `PATCH /registrations/{id}/`: Partially update a registration by ID.
  - `DELETE /registrations/{id}/`: Cancel a registration (only the organizer can delete).

- **User Management**:
  - `POST /users/register/`: Register a new user.
  - `POST /api/token/`: Obtain JWT token.
  - `GET /users/me/`: Retrieve details of the authenticated user.
  - `PUT /users/me/`: Update the authenticated user's details.
  - `PATCH /users/me/`: Partially update the authenticated user's details.

## Bonus Features
- **Custom User Model**: Extend Django's default user model for flexibility.
- **Asynchronous Tasks**: Use Celery to handle background tasks like sending emails.
- **Email Testing**: Use MailDev to capture and test emails locally.
- **Rate Limiting**: Protect the API with throttling for anonymous and authenticated users.