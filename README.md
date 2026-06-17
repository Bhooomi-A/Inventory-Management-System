# StockSense – Inventory Management System

A full-stack inventory management application built with **Python FastAPI**, **SQLite**, and **Vanilla HTML/CSS/JS**.

---

## Features

- **Add Products** — Add items with name, category, initial quantity, price, and a configurable low-stock alert threshold
- **Update Stock** — Add or remove stock units with an optional note for audit trail
- **Prevent Negative Stock** — Enforced at both layers: the frontend shows a live preview before you confirm, and the FastAPI backend independently rejects any request that would drop stock below zero
- **Display Products** — Responsive table with live search by name or category, category dropdown filter
- **Low Stock Alerts** — Products at or below their threshold show a warning badge; a dedicated filter displays only those items
- **Stock History** — Every stock change is logged in a `stock_history` table with before/after values (`GET /api/products/{id}/history`)
- **Dashboard Stats** — Summary cards: total products, total units, low stock count, out-of-stock count, categories

---

## Technology Stack

| Layer      | Technology                       | Why                                                     |
|------------|----------------------------------|---------------------------------------------------------|
| Backend    | Python + FastAPI                 | Fast, modern, auto-generates Swagger docs at `/docs`    |
| ORM        | SQLAlchemy                       | Maps Python classes to database tables                  |
| Validation | Pydantic v2                      | Validates request bodies and returns clear error messages|
| Database   | SQLite                           | Zero setup, file-based, perfect for local development   |
| Frontend   | HTML + CSS + Vanilla JavaScript  | No build tools needed — open directly in browser        |
| HTTP       | Fetch API (browser built-in)     | Native JS for calling the FastAPI backend               |

---

## Project Structure

```
inventory-surekha/
├── backend/
│   ├── main.py          # FastAPI app — all routes (CRUD + stock update)
│   ├── models.py        # SQLAlchemy models (Product, StockHistory tables)
│   ├── schemas.py       # Pydantic schemas for request/response validation
│   ├── database.py      # DB connection, session setup
│   └── requirements.txt
├── frontend/
│   └── index.html       # Complete UI — HTML + CSS + JS in one file
└── README.md
```

---

## Setup and Run Instructions

### Prerequisites
- Python 3.9 or above
- pip

### Step 1 — Clone the Repository
```bash
git clone <https://github.com/Bhooomi-A/Inventory-Management-System.git>
cd inventory-surekha
```

### Step 2 — Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 3 — Start the FastAPI Backend
```bash
uvicorn main:app --reload --port 5000
```

The API will be available at:
- **Base URL:** `http://localhost:5000`
- **Interactive Swagger Docs:** `http://localhost:5000/docs` 
- **SQLite DB** (`inventory.db`) is auto-created with 8 sample products on first run

### Step 4 — Open the Frontend
Open `frontend/index.html` directly in your browser — no server needed for the frontend.

> **Both the backend must be running** before opening the frontend.

---

## API Endpoints

| Method | Endpoint                              | Description                        |
|--------|---------------------------------------|------------------------------------|
| GET    | `/api/products`                       | List all products (with filters)   |
| POST   | `/api/products`                       | Add a new product                  |
| PUT    | `/api/products/{id}`                  | Update product details             |
| PATCH  | `/api/products/{id}/stock`            | Add or remove stock units          |
| DELETE | `/api/products/{id}`                  | Delete a product                   |
| GET    | `/api/products/{id}/history`          | View stock change history          |
| GET    | `/api/stats`                          | Dashboard summary stats            |

### Query Parameters for GET `/api/products`
- `?search=keyboard` — Filter by name or category (case-insensitive)
- `?category=Electronics` — Filter by exact category
- `?lowStock=true` — Show only products at or below their threshold

---

## Assumptions Made

1. **Price is in Indian Rupees (₹)** — formatted using `en-IN` locale
2. **Product names must be unique** — enforced at both API and DB level
3. **Low stock threshold defaults to 10** — configurable per product
4. **SQLite is used for simplicity** — for production, PostgreSQL (already familiar from Jio internship) would be the right choice
5. **No authentication** — assumed single-user internal tool; JWT auth can be added as an extension
6. **Negative stock is impossible** — blocked at both frontend (live preview) and backend (HTTP 400 with clear message)

---

## AI Tools Used and Development Approach

### Tools Used
- **Claude (Anthropic)** — Used as the primary AI-assisted development tool throughout the project

### How AI Helped
Claude was used to scaffold the initial project structure and suggest best practices for organizing a FastAPI application with separation of concerns across `main.py`, `models.py`, `schemas.py`, and `database.py`. Since I already had hands-on experience building REST APIs with FastAPI at Jio Platforms, I was able to critically evaluate, modify, and extend Claude's suggestions rather than accepting them blindly. Claude also helped draft the HTML/CSS frontend layout quickly, which I then refined to match the inventory domain. The AI accelerated repetitive tasks like writing Pydantic schemas and SQLAlchemy model definitions, freeing time to focus on domain-specific logic like the two-layer negative stock prevention.

### Challenges Encountered
The main challenge was ensuring the negative stock prevention was robust at both layers. The frontend needed to show a live preview of the new quantity before the user confirms, while the backend needed to independently re-validate this even if someone bypassed the UI and called the API directly. This mirrors real-world production patterns where you never trust client-side validation alone. Another consideration was the stock history audit trail — designing the `StockHistory` table with `quantity_before` and `quantity_after` fields means any stock discrepancy can be traced back to a specific action, which is a critical feature in real inventory systems.

---

## Possible Production Enhancements

- Replace SQLite with PostgreSQL (already used at Jio internship)
- Add JWT-based authentication and role management
- Email/SMS alerts when stock drops below threshold
- CSV export of inventory data
- Barcode scanner integration
- Supplier management module
- Deploy backend on AWS/GCP with Docker
