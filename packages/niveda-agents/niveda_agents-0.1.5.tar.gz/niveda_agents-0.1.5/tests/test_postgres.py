import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(scope="module")
def db():
    """Setup PostgreSQL connection for tests."""
    from niveda_agents.db.postgres import PostgresDB
    database = PostgresDB()
    yield database
    database.close_connection()


def test_dynamic_queries(db):
    """Test dynamic table creation, insertion, updating, and deletion."""
    table_name = "employees"
    columns = {
        "id": "SERIAL PRIMARY KEY",
        "name": "VARCHAR(100) NOT NULL",
        "email": "VARCHAR(255) UNIQUE",
        "age": "INTEGER",
        "salary": "DECIMAL(10,2)",
        "department": "VARCHAR(100)",
        "created_at": "TIMESTAMP DEFAULT NOW()",
        "updated_at": "TIMESTAMP DEFAULT NOW()"
    }

    db.create_table(table_name, columns)
    db.create_index(table_name, ["email", "age"])

    # Insert Data
    db.insert_data(table_name, {
        "name": "Alice",
        "email": "alice@example.com",
        "age": 30,
        "salary": 70000.50,
        "department": "Engineering"
    })

    # Update Data
    db.update_data(table_name, {"salary": 80000.00}, {
                   "email": "alice@example.com"})

    # Fetch & Verify Update
    result = db.fetch_results(
        f"SELECT salary FROM {table_name} WHERE email = %s;", ("alice@example.com",))
    assert result[0][0] == 80000.00

    # Delete Data
    db.delete_data(table_name, {"email": "alice@example.com"})

    # Verify Deletion
    result = db.fetch_results(
        f"SELECT * FROM {table_name} WHERE email = %s;", ("alice@example.com",))
    assert result == []

    # Empty Table
    db.empty_table(table_name)

    # Delete Table
    db.delete_table(table_name)

    print("✅ All dynamic PostgreSQL tests passed!")
