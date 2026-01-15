"""
Base Action Class for Right-click Utilities and Shortcuts Hub

This module provides a base class that all right-click actions should inherit from.
It provides common functionality and ensures consistent behavior across all actions.
"""

from abc import ABC, abstractmethod
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsFeature, QgsVectorLayer, QgsPointXY
from qgis.gui import QgsMapCanvas


class BaseAction(ABC):
    """
    Base class for all right-click actions.
    
    All actions should inherit from this class and implement the execute method.
    This ensures consistent behavior and provides common functionality.
    """
    
    def __init__(self):
        """Initialize the base action."""
        self.action_id = None
        self.name = None
        self.category = None
        self.description = None
        self.enabled = True
        
        # Feature type support metadata
        self.supported_geometry_types = []  # List of supported geometry types: 'point', 'line', 'polygon', 'canvas'
        self.supported_click_types = []     # List of supported click types: 'point', 'line', 'polygon', 'canvas', 'mixed'
        
        # Action scope metadata - NEW
        self.action_scope = 'feature'  # 'feature', 'layer', 'universal'
        self.supported_scopes = ['feature']  # List of supported scopes
        
        # Valid scope options - enforced by the system
        self.VALID_SCOPES = ['feature', 'layer', 'universal']
        
    @abstractmethod
    def execute(self, context):
        """
        Execute the action.
        
        Args:
            context (dict): Context containing:
                - feature (QgsFeature): The clicked feature
                - layer (QgsVectorLayer): The active layer
                - canvas (QgsMapCanvas): The map canvas
                - map_point (QgsPointXY): The clicked point
        """
        pass
    
    def get_action_info(self):
        """
        Get action information for registration.
        
        Returns:
            dict: Action information dictionary
        """
        return {
            'id': self.action_id,
            'name': self.name,
            'callback': self.execute,
            'enabled': self.enabled,
            'category': self.category,
            'description': self.description,
            'supported_geometry_types': self.supported_geometry_types,
            'supported_click_types': self.supported_click_types
        }
    
    def supports_geometry_type(self, geometry_type: str) -> bool:
        """
        Check if this action supports a specific geometry type.
        
        Args:
            geometry_type: Geometry type to check ('point', 'line', 'polygon', 'canvas')
            
        Returns:
            True if the action supports this geometry type
        """
        return geometry_type in self.supported_geometry_types
    
    def supports_click_type(self, click_type: str) -> bool:
        """
        Check if this action supports a specific click type.
        
        Args:
            click_type: Click type to check ('point', 'line', 'polygon', 'canvas', 'mixed')
            
        Returns:
            True if the action supports this click type
        """
        return click_type in self.supported_click_types
    
    def is_available_for_context(self, context: dict) -> bool:
        """
        Check if this action is available for the given context.
        
        Args:
            context: Context dictionary containing click information
            
        Returns:
            True if the action is available for this context
        """
        click_type = context.get('click_type', 'canvas')
        
        # Universal actions are available for any context
        if self.supports_click_type('universal'):
            return True
        
        # Check if action supports the specific click type
        return self.supports_click_type(click_type)
    
    def set_supported_geometry_types(self, geometry_types: list):
        """
        Set the supported geometry types for this action.
        
        Args:
            geometry_types: List of supported geometry types
        """
        self.supported_geometry_types = geometry_types
    
    def set_supported_click_types(self, click_types: list):
        """
        Set the supported click types for this action.
        
        Args:
            click_types: List of supported click types
        """
        self.supported_click_types = click_types
    
    def set_action_scope(self, scope: str):
        """
        Set the primary action scope for this action.
        
        Args:
            scope: Action scope ('feature', 'layer', 'universal')
            
        Raises:
            ValueError: If scope is not valid
        """
        if scope not in self.VALID_SCOPES:
            raise ValueError(f"Invalid action scope '{scope}'. Must be one of: {self.VALID_SCOPES}")
        self.action_scope = scope
    
    def set_supported_scopes(self, scopes: list):
        """
        Set the supported scopes for this action.
        
        Args:
            scopes: List of supported scopes ('feature', 'layer', 'universal')
            
        Raises:
            ValueError: If any scope is not valid
        """
        for scope in scopes:
            if scope not in self.VALID_SCOPES:
                raise ValueError(f"Invalid supported scope '{scope}'. Must be one of: {self.VALID_SCOPES}")
        self.supported_scopes = scopes
    
    def supports_scope(self, scope: str) -> bool:
        """
        Check if this action supports a specific scope.
        
        Args:
            scope: Scope to check ('feature', 'layer', 'universal')
            
        Returns:
            True if the action supports this scope
        """
        return scope in self.supported_scopes
    
    def validate_action_configuration(self) -> bool:
        """
        Validate that the action is properly configured.
        
        Returns:
            True if action is properly configured
            
        Raises:
            ValueError: If action configuration is invalid
        """
        # Check required properties
        if not self.action_id:
            raise ValueError("Action ID is required")
        if not self.name:
            raise ValueError("Action name is required")
        
        # Check scope configuration
        if self.action_scope not in self.VALID_SCOPES:
            raise ValueError(f"Invalid action scope '{self.action_scope}'. Must be one of: {self.VALID_SCOPES}")
        
        if not self.supported_scopes:
            raise ValueError("At least one supported scope must be specified")
        
        for scope in self.supported_scopes:
            if scope not in self.VALID_SCOPES:
                raise ValueError(f"Invalid supported scope '{scope}'. Must be one of: {self.VALID_SCOPES}")
        
        # Check that action_scope is in supported_scopes
        if self.action_scope not in self.supported_scopes:
            raise ValueError(f"Action scope '{self.action_scope}' must be included in supported_scopes: {self.supported_scopes}")
        
        # Check click types and geometry types
        if not self.supported_click_types:
            raise ValueError("At least one supported click type must be specified")
        
        if not self.supported_geometry_types:
            raise ValueError("At least one supported geometry type must be specified")
        
        return True
    
    def show_error(self, title, message):
        """
        Show an error message dialog.
        
        Args:
            title (str): Dialog title
            message (str): Error message
        """
        QMessageBox.critical(None, title, message)
    
    def show_info(self, title, message):
        """
        Show an information message dialog.
        
        Args:
            title (str): Dialog title
            message (str): Information message
        """
        QMessageBox.information(None, title, message)
    
    def show_warning(self, title, message):
        """
        Show a warning message dialog.
        
        Args:
            title (str): Dialog title
            message (str): Warning message
        """
        QMessageBox.warning(None, title, message)
    
    def confirm_action(self, title, message):
        """
        Show a confirmation dialog.
        
        Args:
            title (str): Dialog title
            message (str): Confirmation message
            
        Returns:
            bool: True if user confirmed, False otherwise
        """
        reply = QMessageBox.question(
            None,
            title,
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    
    def handle_edit_mode(self, layer, operation_name="operation"):
        """
        Handle edit mode for the layer.
        
        Args:
            layer (QgsVectorLayer): The layer to handle edit mode for
            operation_name (str): Name of the operation for error messages
            
        Returns:
            tuple: (was_in_edit_mode, edit_mode_entered)
        """
        was_in_edit_mode = layer.isEditable()
        edit_mode_entered = False
        
        if not was_in_edit_mode:
            if not layer.startEditing():
                self.show_error(
                    "Error",
                    f"Failed to start editing the layer for {operation_name}. "
                    "The layer may be read-only or locked."
                )
                return None, None
            edit_mode_entered = True
        
        return was_in_edit_mode, edit_mode_entered
    
    def commit_changes(self, layer, operation_name="operation"):
        """
        Commit changes to the layer.
        
        Args:
            layer (QgsVectorLayer): The layer to commit changes for
            operation_name (str): Name of the operation for error messages
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not layer.commitChanges():
            self.show_error(
                "Error",
                f"Failed to commit changes for {operation_name}. "
                "The changes may not have been saved."
            )
            layer.rollBack()
            return False
        return True
    
    def rollback_changes(self, layer):
        """
        Rollback changes to the layer.
        
        Args:
            layer (QgsVectorLayer): The layer to rollback changes for
        """
        try:
            if layer.isEditable():
                layer.rollBack()
        except Exception:
            pass  # Ignore rollback errors
    
    def exit_edit_mode(self, layer, edit_mode_entered):
        """
        Exit edit mode if we entered it.
        
        Args:
            layer (QgsVectorLayer): The layer to exit edit mode for
            edit_mode_entered (bool): Whether we entered edit mode
        """
        if edit_mode_entered and layer.isEditable():
            try:
                layer.commitChanges()
                layer.stopEditing()
            except Exception:
                pass  # Ignore errors when stopping edit mode
    
    def get_settings_schema(self):
        """
        Define the settings schema for this action.
        
        This method should be overridden by subclasses to define their customizable settings.
        
        Returns:
            dict: Settings schema with setting definitions
        """
        return {}
    
    def get_setting(self, setting_name, default_value=None):
        """
        Get a setting value for this action.
        
        Args:
            setting_name (str): Name of the setting to retrieve
            default_value: Default value if setting not found
            
        Returns:
            Setting value or default_value
        """
        from qgis.PyQt.QtCore import QSettings
        settings = QSettings()
        key = f"RightClickUtilities/{self.action_id}/{setting_name}"
        return settings.value(key, default_value)
    
    def set_setting(self, setting_name, value):
        """
        Set a setting value for this action.
        
        Args:
            setting_name (str): Name of the setting to set
            value: Value to set
        """
        from qgis.PyQt.QtCore import QSettings
        settings = QSettings()
        key = f"RightClickUtilities/{self.action_id}/{setting_name}"
        settings.setValue(key, value)
    
    def reset_settings_to_defaults(self):
        """
        Reset all settings for this action to their default values.
        """
        schema = self.get_settings_schema()
        for setting_name, setting_def in schema.items():
            default_value = setting_def.get('default')
            if default_value is not None:
                self.set_setting(setting_name, default_value)
    
    def get_all_settings(self):
        """
        Get all current settings for this action.
        
        Returns:
            dict: Dictionary of all current settings
        """
        schema = self.get_settings_schema()
        settings = {}
        for setting_name, setting_def in schema.items():
            default_value = setting_def.get('default')
            settings[setting_name] = self.get_setting(setting_name, default_value)
        return settings
    
    def validate_setting(self, setting_name, value):
        """
        Validate a setting value.
        
        Args:
            setting_name (str): Name of the setting to validate
            value: Value to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        schema = self.get_settings_schema()
        if setting_name not in schema:
            return False, f"Unknown setting: {setting_name}"
        
        setting_def = schema[setting_name]
        setting_type = setting_def.get('type')
        
        # Type validation
        if setting_type == 'bool':
            if not isinstance(value, bool):
                return False, "Value must be True or False"
        elif setting_type in ['int', 'float']:
            try:
                if setting_type == 'int':
                    int(value)
                else:
                    float(value)
            except (ValueError, TypeError):
                return False, f"Value must be a valid {setting_type}"
            
            # Range validation
            min_val = setting_def.get('min')
            max_val = setting_def.get('max')
            if min_val is not None and value < min_val:
                return False, f"Value must be at least {min_val}"
            if max_val is not None and value > max_val:
                return False, f"Value must be at most {max_val}"
        elif setting_type == 'str':
            if not isinstance(value, str):
                return False, "Value must be a string"
        elif setting_type == 'choice':
            options = setting_def.get('options', [])
            if value not in options:
                return False, f"Value must be one of: {', '.join(options)}"
        
        # Custom validation
        validation_func = setting_def.get('validation')
        if validation_func and callable(validation_func):
            return validation_func(value)
        
        return True, ""