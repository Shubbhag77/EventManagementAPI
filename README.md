# Event Management API

A RESTful API for managing events and attendees built with FastAPI and MongoDB.

## Features

- Create, update, and manage events
- Register attendees for events
- Check-in attendees
- Automatic event status updates
- Bulk attendee check-in via CSV upload
- JWT Authentication

## Requirements

- Python 3.8+
- MongoDB
- Dependencies listed in requirements.txt

## Installation

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up environment variables in a `.env` file:
   ```
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=event_management
   SECRET_KEY=your_secret_key_here
   ```

## Running the API

```
uvicorn main:app --reload
```


## API Endpoints

### Events

- `POST /events/` - Create a new event
- `GET /events/{event_id}` - Get event details
- `PUT /events/{event_id}` - Update event
- `DELETE /events/{event_id}` - Delete event
- `GET /events/` - List events with optional filters

### Attendees

- `POST /attendees/` - Register an attendee for an event
- `GET /attendees/{attendee_id}` - Get attendee details
- `PUT /attendees/{attendee_id}` - Update attendee information
- `POST /attendees/{attendee_id}/check-in` - Check in an attendee
- `GET /attendees/event/{event_id}` - List attendees for an event
- `POST /attendees/event/{event_id}/bulk-check-in` - Bulk check-in via CSV

### Authentication

- `POST /token` - Get JWT token
- `GET /users/me` - Get current user information
