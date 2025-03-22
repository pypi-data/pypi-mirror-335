import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(scope="module")
def mongo():
    """Set up MongoDB connection for testing."""
    from niveda_agents.db.mongo import MongoDB
    mongo_db = MongoDB()
    yield mongo_db
    mongo_db.close_connection()


def test_insert_document(mongo):
    """Test inserting a single document."""
    document = {"name": "Alice", "email": "alice@example.com", "age": 30}
    doc_id = mongo.insert_document("users", document)
    assert doc_id is not None


def test_insert_multiple_documents(mongo):
    """Test inserting multiple documents."""
    documents = [
        {"name": "Bob", "email": "bob@example.com", "age": 25},
        {"name": "Charlie", "email": "charlie@example.com", "age": 28}
    ]
    doc_ids = mongo.insert_many("users", documents)
    assert len(doc_ids) == len(documents)


def test_find_document(mongo):
    """Test finding a single document."""
    query = {"email": "alice@example.com"}
    document = mongo.find_document("users", query)
    assert document is not None
    assert document["name"] == "Alice"


def test_find_all_documents(mongo):
    """Test finding all documents in a collection."""
    documents = mongo.find_all("users")
    assert len(documents) > 1  # There should be at least 2 users


def test_find_documents_with_filter(mongo):
    """Test finding documents with a specific condition."""
    query = {"age": {"$gt": 25}}  # Find users older than 25
    documents = mongo.find_all("users", query)
    assert len(documents) >= 2  # Alice and Charlie should match


def test_update_document(mongo):
    """Test updating a single document."""
    query = {"email": "alice@example.com"}
    update_values = {"age": 31}
    modified_count = mongo.update_documents("users", query, update_values)
    assert modified_count == 1


def test_update_multiple_documents(mongo):
    """Test updating multiple documents."""
    query = {"age": {"$lt": 30}}  # Update all users younger than 30
    update_values = {"status": "active"}
    modified_count = mongo.update_documents("users", query, update_values)
    assert modified_count >= 2  # Bob and Charlie should be updated


def test_delete_document(mongo):
    """Test deleting a single document."""
    query = {"email": "bob@example.com"}
    deleted_count = mongo.delete_document("users", query)
    assert deleted_count == 1


def test_delete_multiple_documents(mongo):
    """Test deleting multiple documents."""
    query = {"age": {"$lt": 30}}  # Delete all users younger than 30
    deleted_count = mongo.delete_document("users", query)
    assert deleted_count >= 1  # Charlie should be deleted


def test_count_documents(mongo):
    """Test counting the number of documents in a collection."""
    documents = mongo.find_all("users")
    assert len(documents) >= 1  # Alice should still be in the database


def test_delete_collection(mongo):
    """Test dropping an entire collection."""
    mongo.delete_collection("users")
    documents = mongo.find_all("users")
    assert len(documents) == 0  # Collection should be empty
