# Food Order APIs 🍽️

A backend REST API for a food ordering system, built for our college canteen as part of a group project. I worked on the seller-side server — handling menu items, orders, and users.

Built with **Python**, **FastAPI**, and **PostgreSQL**.

---

## What it does

- Create, update, and delete food orders by ID
- Manage products and users through separate, modular routes
- User authentication with password hashing
- Clean API schema validation using FastAPI's built-in schema system

---

## Project Structure

```
├── db/
│   └── tables.py         # Database tables, fields, and foreign key relationships
├── routes/
│   ├── items.py          # Routes for order items
│   ├── products.py       # Routes for products
│   └── users.py          # Routes for users
├── create.py             # All create operations
├── update.py             # All update operations
├── delete.py             # All delete operations
├── schemas.py            # FastAPI schemas used by routes and functions
├── database.py           # Database connection and initialization
├── hash.py               # Password hashing for user authentication
└── main.py               # Entry point — connects routers and starts the app
```

---

## Running locally

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Start the server**
```bash
uvicorn main:MyApp --reload
```

**3. Test the APIs**

Open your browser and go to:
```
http://localhost:8000/docs
```

This opens the interactive Swagger UI where you can test every endpoint with dummy data and see live responses — `200 OK` for success, error codes when things go wrong (and they will, ready to face them and learn).

---

## Load Testing

Tested using **Locust** with 300 concurrent users.

The first run exposed a few bottlenecks — the database schema had some poorly defined relationships between tables, which caused internal conflicts under load. After redesigning the schema and fixing the foreign key relationships, the API handled **50+ RPS with a 100% success rate**.

That debugging process taught me more about database design than any tutorial.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL |
| Auth | Password hashing (demo) |
| Load Testing | Locust |
