import os
import json
import zipfile
import importlib.util
import shutil
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.plugin import Plugin, PluginStatus
from app.schemas.plugin import PluginCreate, PluginUpdate

# Set up logger
logger = logging.getLogger(__name__)

class PluginService:
    def get_plugin(self, db: Session, plugin_id: int) -> Optional[Plugin]:
        """Get a plugin by ID."""
        return db.query(Plugin).filter(Plugin.id == plugin_id).first()
    
    def get_plugins(
        self, 
        db: Session, 
        category: Optional[str] = None,
        status: Optional[str] = None,
        is_free: Optional[bool] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Plugin]:
        """Get all plugins with optional filtering."""
        query = db.query(Plugin)
        
        if category:
            query = query.filter(Plugin.category == category)
            
        if status:
            query = query.filter(Plugin.status == status)
            
        if is_free is not None:
            query = query.filter(Plugin.is_free == is_free)
            
        return query.offset(skip).limit(limit).all()
    
    def create_plugin(self, db: Session, plugin_in: PluginCreate) -> Plugin:
        """Create a new plugin."""
        plugin = Plugin(**plugin_in.dict())
        db.add(plugin)
        db.commit()
        db.refresh(plugin)
        return plugin
    
    async def upload_plugin(self, db: Session, file: UploadFile) -> Plugin:
        """
        Upload and install a plugin from a zip file.
        The zip file should contain:
        - plugin.json: Plugin metadata
        - main.py: Main entry point
        - Other supporting files
        """
        if not file.filename.endswith('.zip'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plugin file must be a zip archive"
            )
        
        # Create plugins directory if it doesn't exist
        plugins_dir = os.path.join(settings.MODEL_PATH, "plugins")
        os.makedirs(plugins_dir, exist_ok=True)
        
        # Generate a unique ID for this plugin
        plugin_id = uuid.uuid4().hex
        plugin_dir = os.path.join(plugins_dir, plugin_id)
        os.makedirs(plugin_dir, exist_ok=True)
        
        # Save zip file
        zip_path = os.path.join(plugin_dir, "plugin.zip")
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            # Extract zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(plugin_dir)
            
            # Read plugin metadata
            plugin_json_path = os.path.join(plugin_dir, "plugin.json")
            if not os.path.exists(plugin_json_path):
                raise ValueError("Missing plugin.json file in plugin archive")
            
            with open(plugin_json_path, 'r') as f:
                plugin_metadata = json.load(f)
            
            # Validate required fields
            required_fields = ['name', 'version', 'category', 'author', 'entryPoint']
            for field in required_fields:
                if field not in plugin_metadata:
                    raise ValueError(f"Missing required field '{field}' in plugin.json")
            
            # Check if plugin with same name and version already exists
            existing_plugin = db.query(Plugin).filter(
                Plugin.name == plugin_metadata['name'],
                Plugin.version == plugin_metadata['version']
            ).first()
            
            if existing_plugin:
                # If the plugin exists and is active, raise an error
                if existing_plugin.status == PluginStatus.ACTIVE:
                    raise ValueError(f"Plugin {plugin_metadata['name']} v{plugin_metadata['version']} already exists")
                
                # If it exists but is inactive or deprecated, update it
                plugin = existing_plugin
            else:
                # Create new plugin record
                plugin_create = PluginCreate(
                    name=plugin_metadata['name'],
                    version=plugin_metadata['version'],
                    description=plugin_metadata.get('description', ''),
                    category=plugin_metadata['category'],
                    entry_point=plugin_metadata['entryPoint'],
                    package_path=plugin_dir,
                    author=plugin_metadata['author'],
                    license_type=plugin_metadata.get('license', 'MIT'),
                    is_free=plugin_metadata.get('isFree', True),
                    price=plugin_metadata.get('price', 0.0),
                    icon_url=plugin_metadata.get('iconUrl', ''),
                    config=plugin_metadata.get('config', {}),
                    requirements=plugin_metadata.get('requirements', {}),
                    is_system=False
                )
                
                plugin = Plugin(**plugin_create.dict())
            
            # Update package path and activation status
            plugin.package_path = plugin_dir
            plugin.status = PluginStatus.ACTIVE
            plugin.installed_at = datetime.utcnow()
            
            db.add(plugin)
            db.commit()
            db.refresh(plugin)
            
            return plugin
            
        except Exception as e:
            # Clean up directory if there was an error
            shutil.rmtree(plugin_dir, ignore_errors=True)
            logger.error(f"Error processing plugin upload: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing plugin upload: {str(e)}"
            )
    
    def update_plugin(self, db: Session, plugin: Plugin, plugin_in: PluginUpdate) -> Plugin:
        """Update an existing plugin."""
        update_data = plugin_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(plugin, field, value)
            
        db.add(plugin)
        db.commit()
        db.refresh(plugin)
        return plugin
    
    def delete_plugin(self, db: Session, plugin_id: int) -> None:
        """Delete a plugin."""
        plugin = db.query(Plugin).filter(Plugin.id == plugin_id).first()
        if plugin:
            # Delete the plugin files
            if os.path.exists(plugin.package_path):
                try:
                    shutil.rmtree(plugin.package_path, ignore_errors=True)
                except Exception as e:
                    logger.error(f"Error deleting plugin files: {str(e)}")
            
            # Delete from database
            db.delete(plugin)
            db.commit()
    
    def install_plugin(self, db: Session, plugin: Plugin, user_id: int) -> Plugin:
        """Install a plugin for a specific user."""
        # In a real implementation, this would add a user-plugin association
        # For the MVP, we'll just update the plugin's status and last_used_at
        
        plugin.last_used_at = datetime.utcnow()
        db.add(plugin)
        db.commit()
        db.refresh(plugin)
        return plugin
    
    def uninstall_plugin(self, db: Session, plugin: Plugin, user_id: int) -> Plugin:
        """Uninstall a plugin for a specific user."""
        # In a real implementation, this would remove a user-plugin association
        # For the MVP, we'll just update the plugin's status
        
        plugin.last_used_at = None  # Clear last used timestamp
        db.add(plugin)
        db.commit()
        db.refresh(plugin)
        return plugin
    
    def execute_plugin(self, plugin_id: int, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a plugin by dynamically loading and running it.
        
        Args:
            plugin_id: ID of the plugin to execute
            input_data: Input data for the plugin
            
        Returns:
            dict: Plugin execution results
        """
        # Get plugin from database
        db = SessionLocal()
        plugin = self.get_plugin(db, plugin_id)
        db.close()
        
        if not plugin:
            raise ValueError(f"Plugin with ID {plugin_id} not found")
        
        if plugin.status != PluginStatus.ACTIVE:
            raise ValueError(f"Plugin {plugin.name} is not active")
        
        # Construct the full path to the entry point file
        entry_point_path = os.path.join(plugin.package_path, plugin.entry_point)
        if not os.path.exists(entry_point_path):
            raise ValueError(f"Plugin entry point {entry_point_path} not found")
        
        try:
            # Dynamically load the plugin module
            spec = importlib.util.spec_from_file_location("plugin_module", entry_point_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if the module has the required execute function
            if not hasattr(module, "execute"):
                raise ValueError(f"Plugin {plugin.name} does not have an execute function")
            
            # Update last used timestamp
            db = SessionLocal()
            plugin.last_used_at = datetime.utcnow()
            db.add(plugin)
            db.commit()
            db.close()
            
            # Execute the plugin
            input_data = input_data or {}
            result = module.execute(input_data)
            return result
        
        except Exception as e:
            logger.error(f"Error executing plugin {plugin.name}: {str(e)}")
            raise ValueError(f"Error executing plugin {plugin.name}: {str(e)}")


# Create a plugin service instance
plugin_service = PluginService()


# Import for execute_plugin method
from app.db.session import SessionLocal
