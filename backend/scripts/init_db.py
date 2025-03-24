#!/usr/bin/env python3
"""
Database Initialization Script for Construction AI Platform

This script:
1. Creates the database tables
2. Seeds initial data (admin user, default materials, etc.)

Usage:
    python init_db.py [--drop-existing]

Options:
    --drop-existing    Drop existing tables before creating new ones (CAUTION!)
"""

import os
import sys
import argparse
from datetime import datetime
import logging

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import Base, engine, SessionLocal
from app.core.security import get_password_hash
from app.db.models.user import User, UserRole
from app.db.models.material import Material, MaterialCategory, MaterialUnit
from app.db.models.plugin import Plugin, PluginCategory, PluginStatus

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created successfully!")


def drop_tables():
    """Drop all database tables (CAUTION!)."""
    logger.warning("DROPPING ALL TABLES!")
    Base.metadata.drop_all(bind=engine)
    logger.info("Tables dropped successfully.")


def seed_admin_user(db):
    """Create an admin user."""
    logger.info("Creating admin user...")
    
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    if admin_user:
        logger.info("Admin user already exists, skipping.")
        return
        
    admin_user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("password"),  # Change this!
        full_name="Admin User",
        is_active=True,
        role=UserRole.ADMIN
    )
    
    db.add(admin_user)
    db.commit()
    logger.info("Admin user created successfully!")


def seed_default_materials(db):
    """Seed default construction materials."""
    logger.info("Seeding default materials...")
    
    materials_count = db.query(Material).count()
    if materials_count > 0:
        logger.info(f"Found {materials_count} existing materials, skipping.")
        return
    
    # Define default materials
    default_materials = [
        # Structural materials
        {
            "name": "Concrete",
            "description": "Standard structural concrete for foundations, slabs, etc.",
            "category": MaterialCategory.STRUCTURAL,
            "unit": MaterialUnit.CUBIC_YARD,
            "unit_cost": 150.00,
            "labor_rate": 65.00,
            "equipment_rate": 25.00,
            "overhead_percent": 10.0,
            "profit_percent": 15.0,
            "is_custom": False
        },
        {
            "name": "Steel Framing",
            "description": "Structural steel framing",
            "category": MaterialCategory.STRUCTURAL,
            "unit": MaterialUnit.TON,
            "unit_cost": 2200.00,
            "labor_rate": 350.00,
            "equipment_rate": 150.00,
            "overhead_percent": 10.0,
            "profit_percent": 15.0,
            "is_custom": False
        },
        {
            "name": "Wood Framing",
            "description": "Dimensional lumber for wood framing",
            "category": MaterialCategory.STRUCTURAL,
            "unit": MaterialUnit.BOARD_FEET,
            "unit_cost": 0.95,
            "labor_rate": 0.60,
            "equipment_rate": 0.10,
            "overhead_percent": 10.0,
            "profit_percent": 15.0,
            "is_custom": False
        },
        
        # Finish materials
        {
            "name": "Gypsum Board",
            "description": "5/8\" gypsum wallboard",
            "category": MaterialCategory.FINISHES,
            "unit": MaterialUnit.SQUARE_FEET,
            "unit_cost": 0.55,
            "labor_rate": 0.85,
            "equipment_rate": 0.05,
            "overhead_percent": 10.0,
            "profit_percent": 15.0,
            "is_custom": False
        },
        {
            "name": "Carpet",
            "description": "Commercial grade carpet",
            "category": MaterialCategory.FINISHES,
            "unit": MaterialUnit.SQUARE_FEET,
            "unit_cost": 3.50,
            "labor_rate": 1.25,
            "equipment_rate": 0.0,
            "overhead_percent": 10.0,
            "profit_percent": 15.0,
            "is_custom": False
        },
        {
            "name": "Interior Paint",
            "description": "Interior latex paint",
            "category": MaterialCategory.FINISHES,
            "unit": MaterialUnit.SQUARE_FEET,
            "unit_cost": 0.35,
            "labor_rate": 0.65,
            "equipment_rate": 0.05,
            "overhead_percent": 10.0,
            "profit_percent": 15.0,
            "is_custom": False
        },
        
        # MEP materials
        {
            "name": "Electrical Wiring",
            "description": "12/2 Romex electrical wiring",
            "category": MaterialCategory.ELECTRICAL,
            "unit": MaterialUnit.LINEAR_FEET,
            "unit_cost": 0.75,
            "labor_rate": 1.50,
            "equipment_rate": 0.0,
            "overhead_percent": 10.0,
            "profit_percent": 15.0,
            "is_custom": False
        },
        {
            "name": "Plumbing Pipe",
            "description": "3/4\" copper pipe",
            "category": MaterialCategory.PLUMBING,
            "unit": MaterialUnit.LINEAR_FEET,
            "unit_cost": 3.25,
            "labor_rate": 4.50,
            "equipment_rate": 0.0,
            "overhead_percent": 10.0,
            "profit_percent": 15.0,
            "is_custom": False
        },
        {
            "name": "HVAC Ductwork",
            "description": "Galvanized sheet metal ductwork",
            "category": MaterialCategory.HVAC,
            "unit": MaterialUnit.POUND,
            "unit_cost": 4.00,
            "labor_rate": 3.50,
            "equipment_rate": 0.25,
            "overhead_percent": 10.0,
            "profit_percent": 15.0,
            "is_custom": False
        },
        
        # Openings
        {
            "name": "Interior Door",
            "description": "Hollow core interior door, including frame and hardware",
            "category": MaterialCategory.FINISHES,
            "unit": MaterialUnit.EACH,
            "unit_cost": 175.00,
            "labor_rate": 95.00,
            "equipment_rate": 0.0,
            "overhead_percent": 10.0,
            "profit_percent": 15.0,
            "is_custom": False
        },
        {
            "name": "Window",
            "description": "Vinyl double-hung window",
            "category": MaterialCategory.FINISHES,
            "unit": MaterialUnit.SQUARE_FEET,
            "unit_cost": 35.00,
            "labor_rate": 15.00,
            "equipment_rate": 0.0,
            "overhead_percent": 10.0,
            "profit_percent": 15.0,
            "is_custom": False
        },
        
        # Other materials
        {
            "name": "Wall Insulation",
            "description": "R-19 fiberglass batt insulation",
            "category": MaterialCategory.FINISHES,
            "unit": MaterialUnit.SQUARE_FEET,
            "unit_cost": 0.65,
            "labor_rate": 0.45,
            "equipment_rate": 0.0,
            "overhead_percent": 10.0,
            "profit_percent": 15.0,
            "is_custom": False
        }
    ]
    
    # Add materials to database
    for material_data in default_materials:
        material = Material(**material_data)
        db.add(material)
    
    db.commit()
    logger.info(f"Added {len(default_materials)} default materials!")


def seed_default_plugins(db):
    """Seed default core plugins."""
    logger.info("Seeding default plugins...")
    
    plugin_count = db.query(Plugin).count()
    if plugin_count > 0:
        logger.info(f"Found {plugin_count} existing plugins, skipping.")
        return
    
    # Core system plugins
    default_plugins = [
        {
            "name": "Core Elements Detector",
            "version": "1.0.0",
            "description": "Core plugin for detecting basic structural elements in construction plans",
            "category": PluginCategory.GENERAL,
            "status": PluginStatus.ACTIVE,
            "author": "Construction AI",
            "license_type": "MIT",
            "is_free": True,
            "entry_point": "plugins/core/element_detector.py",
            "package_path": "plugins/core",
            "config": {
                "detection_threshold": 0.75,
                "enable_gpu": False
            },
            "is_system": True,
            "installed_at": datetime.utcnow()
        },
        {
            "name": "Basic Estimator",
            "version": "1.0.0",
            "description": "Core plugin for generating basic cost estimations",
            "category": PluginCategory.GENERAL,
            "status": PluginStatus.ACTIVE,
            "author": "Construction AI",
            "license_type": "MIT",
            "is_free": True,
            "entry_point": "plugins/core/basic_estimator.py",
            "package_path": "plugins/core",
            "config": {
                "pricing_source": "internal",
                "include_tax": True
            },
            "is_system": True,
            "installed_at": datetime.utcnow()
        }
    ]
    
    # Add plugins to database
    for plugin_data in default_plugins:
        plugin = Plugin(**plugin_data)
        db.add(plugin)
    
    db.commit()
    logger.info(f"Added {len(default_plugins)} default plugins!")


def main():
    """Main function to initialize the database."""
    parser = argparse.ArgumentParser(description="Initialize the Construction AI Platform database")
    parser.add_argument("--drop-existing", action="store_true", help="Drop existing tables before creating new ones (CAUTION!)")
    args = parser.parse_args()
    
    if args.drop_existing:
        drop_tables()
    
    create_tables()
    
    # Seed initial data
    db = SessionLocal()
    try:
        seed_admin_user(db)
        seed_default_materials(db)
        seed_default_plugins(db)
    finally:
        db.close()
    
    logger.info("Database initialization completed successfully!")


if __name__ == "__main__":
    main()
