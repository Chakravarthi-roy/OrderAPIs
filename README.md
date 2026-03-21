# Food Order APIs

A RESTful API for managing food orders built with FastAPI and PostgreSQL. Designed for hostel canteen use. It supports users, products, and orders with full CRUD operations.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Validation | Pydantic v2 |
| Password Hashing | Passlib + bcrypt |
| Load Testing | Locust |
| Server | Uvicorn |

---

## Folder Structure

```
├── CRUD/
│   ├── create.py        # Create logic for users, products, orders
│   ├── delete.py        # Delete logic
│   └── update.py        # Update logic
├── db/
│   ├── hash.py        # Password hashing utility
│   ├── schemas.py       # Pydantic request/response schemas
│   └── tables.py          # SQLAlchemy table definitions
├── routes/
│   ├── orders.py         # Order and order item endpoints
│   ├── products.py      # Product endpoints
│   └── users.py        # User endpoints
├── database.py          # DB engine and session setup
├── genData.py           # Seed script for generating test data
├── locustfile.py        # Load test configuration
├── main.py              # App entry point
├── requirements.txt
└── .gitignore
```

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Create and activate virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:
```bash
# Mac/Linux
touch .env
```
> **Windows:** Create a new file `.env` manually in the project root.

Then add your database URL inside it:
```
DATABASE_URL=postgresql+psycopg2://your_user:your_password@localhost/your_db_name
```

### 5. Run the application
```bash
uvicorn main:MyApp --reload
```

The API will be available at `http://localhost:8000` - You should see {"Hello Milma"}  
Interactive docs at `http://localhost:8000/docs`

---

## API Endpoints

### Users `/user`
| Method | Endpoint | Description |
|---|---|---|
| POST | `/user/` | Create a new user |
| GET | `/user/` | Get all users |
| GET | `/user/{user_id}` | Get user by ID |
| PATCH | `/user/{user_id}` | Update user details |
| DELETE | `/user/{user_id}` | Delete a user |

### Products `/products`
| Method | Endpoint | Description |
|---|---|---|
| POST | `/products/` | Create a new product |
| GET | `/products/` | Get all products |
| GET | `/products/{product_id}` | Get product by ID |
| PATCH | `/products/{product_id}` | Update product details |
| DELETE | `/products/{product_id}` | Delete a product |

### Orders `/orders`
| Method | Endpoint | Description |
|---|---|---|
| POST | `/orders/` | Create a new order |
| GET | `/orders/` | Get all orders |
| GET | `/orders/{order_id}` | Get order by ID |
| PATCH | `/orders/{order_id}` | Update order status |
| DELETE | `/orders/{order_id}` | Delete an order |
| POST | `/orders/{order_id}/items` | Add item to order |
| PUT | `/orders/{order_id}/items/{item_id}` | Update item quantity |
| DELETE | `/orders/{order_id}/items/{item_id}` | Remove item from order |

---

## Validations

- Passwords must be at least 8 characters with one uppercase, one lowercase, and one digit
- Duplicate usernames and emails are rejected
- Duplicate products are rejected
- Orders must have at least one item
- Product and user references are validated before creating an order
- Item quantities must be positive integers

---

## Database Seeding

Before load testing, the database needs sample data. 
`genData.py` generates 200 random orders with items using existing users and products.

Create some dummy users and products in the DB first (via Swagger UI at `/docs`), only then run (cannot run this one empty database):
```bash
python genData.py
```

This will seed:
- 200 orders assigned to random users
- 1-5 order items per order with random products and quantities
- Correct total amount calculated for each order

---

## Load Testing

Load testing is done using **Locust**. The `locustfile.py` simulates real user behaviour with weighted tasks:

| Task | Weight | Description |
|---|---|---|
| Create order | 3 | Most frequent — simulates order placement |
| Update order status | 2 | Simulates kitchen/delivery status updates |
| Get all orders | 1 | Read traffic |
| Get all products | 1 | Read traffic |
| Get all users | 1 | Read traffic |

### Running the load test

Make sure the FastAPI server is running first in one terminal:
```bash
uvicorn main:MyApp --reload
```

Then open a second terminal and run:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

Then open your browser and go to:
```
http://localhost:8089
```

### Using the Locust dashboard

Once you open `http://localhost:8089` you will see:

- **Number of users:** total concurrent users to simulate (e.g. 300)
- **Ramp up:** how many users to add per second (e.g. 10 means it reaches 300 users in 30 seconds)
- Click **Start swarming** to begin the test

While the test runs, the dashboard shows:

| Metric | What it means |
|---|---|
| RPS | Requests per second your API is handling |
| Failures % | Percentage of requests that failed |
| Median response time | Half of requests are faster than this |
| 95th percentile | 95% of requests are faster than this |
| Current users | How many virtual users are active |

Click **Stop** to end the test anytime. You can also download a CSV report of the results from the dashboard.

### My Results

| Test | Users | Ramp Up | RPS | Failures |
|---|---|---|---|---|
| Test 1 | 300 | 1 user/sec | 100+ RPS | 0% |
| Test 2 | 300 | 10 users/sec | 60-74 RPS | 0% |

Connection pool configured at `pool_size=20, max_overflow=40` to handle concurrent load without timeouts.

---

## Scaling Strategy

This API is designed with scalability in mind. Here is how it can be scaled progressively:

| Level | Approach | Change Required |
|---|---|---|
| Level 1 | Multiple Uvicorn workers | `--workers 4` flag only |
| Level 2 | PgBouncer connection pooler | Change DB URL only |
| Level 3 | Load balancer + multiple servers | Nginx config + deploy |
| Level 4 | PostgreSQL read replicas | Two DB engines in code |
| Level 5 | Redis caching | Cache layer in routes |
| Level 6 | Full async with asyncpg | Migrate to async SQLAlchemy |

---

## 📝 Notes

- `.env` file is required to run the app — never commit it to version control
- `genData.py` requires users and products to exist in the DB before seeding orders
- For production, replace `tables.Base.metadata.create_all()` with Alembic migrations
