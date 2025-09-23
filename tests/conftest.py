"""
Test configuration and fixtures
"""

import pytest
from app import create_app
from app.extensions import db
from app.models.customer import Customer
from app.models.mechanic import Mechanic
from app.models.inventory import InventoryItem


@pytest.fixture(scope="session")
def app():
    """Create application for testing"""
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
        }
    )

    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture(scope="function")
def clean_database(app):
    """Clean database before each test"""
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield
    with app.app_context():
        db.session.remove()


@pytest.fixture(scope="function")
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope="function")
def init_database(app, clean_database):
    """Initialize database with test data"""
    with app.app_context():
        # Create test customer
        # The 'clean_database' fixture ensures the DB is empty before this runs.
        customer = Customer(
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            phone_number="555-0101",
            address="123 Test St",
        )
        customer.set_password("password123")
        db.session.add(customer)

        # Create a second test customer
        customer2 = Customer(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@test.com",
            phone_number="555-0103",
            address="456 Test Ave",
        )
        customer2.set_password("password456")
        db.session.add(customer2)

        # Create test mechanic - FIXED: Using shop.com email to match test expectations
        mechanic = Mechanic(
            name="Mike Johnson",
            email="mike.johnson@shop.com",  # Changed from @test.com to @shop.com
            phone="555-0102",
            salary=75000.00,
            is_active=True,
            specializations="Engine, Brakes",
        )
        db.session.add(mechanic)

        # Create a second test mechanic
        mechanic2 = Mechanic(
            name="Sarah Lee",
            email="sarah.lee@shop.com",
            phone="555-0104",
            salary=80000.00,
            is_active=True,
            specializations="Transmission, Electrical",
        )
        db.session.add(mechanic2)

        # Create test inventory items
        inventory_item1 = InventoryItem(
            name="Engine Oil",
            description="5W-30 Engine Oil",
            quantity=50,
            price=25.99,
            supplier="AutoParts Inc",
            category="Fluids",
            reorder_level=10,
        )
        db.session.add(inventory_item1)

        inventory_item2 = InventoryItem(
            name="Brake Pads",
            description="Front brake pads",
            quantity=20,
            price=45.99,
            supplier="BrakeMax",
            category="Brakes",
            reorder_level=5,
        )
        db.session.add(inventory_item2)

        # Commit all changes (skip service ticket for now to avoid constraint issues)
        db.session.commit()

        return {
            "customer": customer,
            "customer2": customer2,
            "mechanic": mechanic,
            "mechanic2": mechanic2,
            "inventory_items": [inventory_item1, inventory_item2],
        }
