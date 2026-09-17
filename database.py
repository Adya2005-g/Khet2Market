"""SQLite helpers for the Khet2Market prototype.

All functions use parameterized SQL and open a short-lived connection so this
module can be used safely from Flask route handlers.
"""

import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).with_name("khet2market.db")


def get_db_connection():
    """Return a connection with dictionary-like rows and foreign keys enabled."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    """Create all Khet2Market prototype tables if they do not exist yet."""
    connection = get_db_connection()
    try:
        with connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT UNIQUE,
                    password TEXT,
                    role TEXT,
                    location TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS produce_lots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    farmer_id INTEGER,
                    produce TEXT,
                    quantity REAL,
                    unit TEXT,
                    expected_price REAL,
                    quality TEXT,
                    harvest_date TEXT,
                    location TEXT,
                    storage_available INTEGER,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (farmer_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS buyers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    business_name TEXT,
                    buyer_type TEXT,
                    location TEXT,
                    verification_status TEXT,
                    required_produce TEXT,
                    required_quantity REAL,
                    quality_requirement TEXT
                );

                CREATE TABLE IF NOT EXISTS offers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lot_id INTEGER,
                    buyer_id INTEGER,
                    offered_price REAL,
                    quantity REAL,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (lot_id) REFERENCES produce_lots(id),
                    FOREIGN KEY (buyer_id) REFERENCES buyers(id)
                );

                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lot_id INTEGER,
                    buyer_id INTEGER,
                    farmer_id INTEGER,
                    final_price REAL,
                    quantity REAL,
                    status TEXT,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (lot_id) REFERENCES produce_lots(id),
                    FOREIGN KEY (buyer_id) REFERENCES buyers(id),
                    FOREIGN KEY (farmer_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER,
                    amount REAL,
                    payment_status TEXT,
                    transaction_id TEXT,
                    payment_date TIMESTAMP,
                    FOREIGN KEY (order_id) REFERENCES orders(id)
                );

                CREATE TABLE IF NOT EXISTS grievances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER,
                    issue_type TEXT,
                    description TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (order_id) REFERENCES orders(id)
                );
                """
            )
    finally:
        connection.close()


def add_user(name, phone=None, email=None, password=None, role=None, location=None):
    """Add a user and return the new user's ID."""
    connection = get_db_connection()
    try:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO users (name, phone, email, password, role, location)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (name, phone, email, password, role, location),
            )
            return cursor.lastrowid
    finally:
        connection.close()


def get_user_by_email(email):
    """Return one user row for an email address, or None if it is not found."""
    connection = get_db_connection()
    try:
        return connection.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        connection.close()


def get_user_by_id(user_id):
    """Return one user row for an ID, or None if it is not found."""
    connection = get_db_connection()
    try:
        return connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    finally:
        connection.close()


def add_produce_lot(
    farmer_id,
    produce,
    quantity,
    unit=None,
    expected_price=None,
    quality=None,
    harvest_date=None,
    location=None,
    storage_available=False,
    status="active",
):
    """Add a farmer's produce lot and return its ID."""
    connection = get_db_connection()
    try:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO produce_lots
                    (farmer_id, produce, quantity, unit, expected_price, quality,
                     harvest_date, location, storage_available, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    farmer_id,
                    produce,
                    quantity,
                    unit,
                    expected_price,
                    quality,
                    harvest_date,
                    location,
                    int(bool(storage_available)),
                    status,
                ),
            )
            return cursor.lastrowid
    finally:
        connection.close()


def get_produce_lots(farmer_id=None):
    """Return all lots, or only the lots belonging to one farmer."""
    connection = get_db_connection()
    try:
        if farmer_id is None:
            cursor = connection.execute(
                "SELECT * FROM produce_lots ORDER BY created_at DESC"
            )
        else:
            cursor = connection.execute(
                "SELECT * FROM produce_lots WHERE farmer_id = ? ORDER BY created_at DESC",
                (farmer_id,),
            )
        return cursor.fetchall()
    finally:
        connection.close()


def get_produce_lot_by_id(lot_id):
    """Return a produce lot by ID, or None when it does not exist."""
    connection = get_db_connection()
    try:
        return connection.execute(
            "SELECT * FROM produce_lots WHERE id = ?", (lot_id,)
        ).fetchone()
    finally:
        connection.close()


def add_buyer(
    business_name,
    buyer_type=None,
    location=None,
    verification_status="pending",
    required_produce=None,
    required_quantity=None,
    quality_requirement=None,
):
    """Add a buyer profile and return its ID."""
    connection = get_db_connection()
    try:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO buyers
                    (business_name, buyer_type, location, verification_status,
                     required_produce, required_quantity, quality_requirement)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    business_name,
                    buyer_type,
                    location,
                    verification_status,
                    required_produce,
                    required_quantity,
                    quality_requirement,
                ),
            )
            return cursor.lastrowid
    finally:
        connection.close()


def get_buyers(verification_status=None):
    """Return buyer profiles, optionally filtered by verification status."""
    connection = get_db_connection()
    try:
        if verification_status is None:
            cursor = connection.execute("SELECT * FROM buyers ORDER BY id DESC")
        else:
            cursor = connection.execute(
                "SELECT * FROM buyers WHERE verification_status = ? ORDER BY id DESC",
                (verification_status,),
            )
        return cursor.fetchall()
    finally:
        connection.close()


def add_offer(lot_id, buyer_id, offered_price, quantity, status="pending"):
    """Add a buyer offer for a produce lot and return the offer ID."""
    connection = get_db_connection()
    try:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO offers (lot_id, buyer_id, offered_price, quantity, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (lot_id, buyer_id, offered_price, quantity, status),
            )
            return cursor.lastrowid
    finally:
        connection.close()


def get_offers(lot_id=None, buyer_id=None):
    """Return offers, with optional lot and buyer filters."""
    connection = get_db_connection()
    try:
        query = "SELECT * FROM offers"
        clauses = []
        values = []
        if lot_id is not None:
            clauses.append("lot_id = ?")
            values.append(lot_id)
        if buyer_id is not None:
            clauses.append("buyer_id = ?")
            values.append(buyer_id)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY created_at DESC"
        return connection.execute(query, values).fetchall()
    finally:
        connection.close()


def update_offer_status(offer_id, status):
    """Update an offer's status and return True when an offer was updated."""
    connection = get_db_connection()
    try:
        with connection:
            cursor = connection.execute(
                "UPDATE offers SET status = ? WHERE id = ?", (status, offer_id)
            )
            return cursor.rowcount > 0
    finally:
        connection.close()


def create_order(lot_id, buyer_id, farmer_id, final_price, quantity, status="confirmed"):
    """Create an order record and return its ID. No payment is processed here."""
    connection = get_db_connection()
    try:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO orders
                    (lot_id, buyer_id, farmer_id, final_price, quantity, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (lot_id, buyer_id, farmer_id, final_price, quantity, status),
            )
            return cursor.lastrowid
    finally:
        connection.close()


def get_orders(farmer_id=None, buyer_id=None):
    """Return orders, optionally filtered for a farmer and/or buyer."""
    connection = get_db_connection()
    try:
        query = "SELECT * FROM orders"
        clauses = []
        values = []
        if farmer_id is not None:
            clauses.append("farmer_id = ?")
            values.append(farmer_id)
        if buyer_id is not None:
            clauses.append("buyer_id = ?")
            values.append(buyer_id)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY order_date DESC"
        return connection.execute(query, values).fetchall()
    finally:
        connection.close()


def add_payment(order_id, amount, payment_status="pending", transaction_id=None, payment_date=None):
    """Store a demo payment record and return its ID; no payment is processed."""
    connection = get_db_connection()
    try:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO payments
                    (order_id, amount, payment_status, transaction_id, payment_date)
                VALUES (?, ?, ?, ?, ?)
                """,
                (order_id, amount, payment_status, transaction_id, payment_date),
            )
            return cursor.lastrowid
    finally:
        connection.close()


def get_payment(order_id):
    """Return the latest payment record for an order, or None if none exists."""
    connection = get_db_connection()
    try:
        return connection.execute(
            "SELECT * FROM payments WHERE order_id = ? ORDER BY id DESC LIMIT 1",
            (order_id,),
        ).fetchone()
    finally:
        connection.close()


def add_grievance(order_id, issue_type, description, status="open"):
    """Add a grievance for an order and return its ID."""
    connection = get_db_connection()
    try:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO grievances (order_id, issue_type, description, status)
                VALUES (?, ?, ?, ?)
                """,
                (order_id, issue_type, description, status),
            )
            return cursor.lastrowid
    finally:
        connection.close()


def get_grievances(order_id=None):
    """Return grievances, optionally only those associated with one order."""
    connection = get_db_connection()
    try:
        if order_id is None:
            cursor = connection.execute(
                "SELECT * FROM grievances ORDER BY created_at DESC"
            )
        else:
            cursor = connection.execute(
                "SELECT * FROM grievances WHERE order_id = ? ORDER BY created_at DESC",
                (order_id,),
            )
        return cursor.fetchall()
    finally:
        connection.close()
