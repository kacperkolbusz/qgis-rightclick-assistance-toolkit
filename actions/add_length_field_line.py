"""
Add Length Field to Line Layer Action for Right-click Utilities and Shortcuts Hub

Adds calculated length field to line layers. Opens a dialog to confirm adding the length field,
then creates it with proper formula and populates all features with calculated values.
"""

from .base_action import BaseAction
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, 
                                 QPushButton, QLabel)
from qgis.PyQt.QtCore import Qt, QMetaType
from qgis.core import (QgsField, QgsExpression, QgsExpressionContext,
                      QgsExpressionContextUtils, QgsWkbTypes)
from qgis.PyQt.QtCore import QVariant
import math


class LengthFieldDialog(QDialog):
    """Dialog for confirming length field addition."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Length Field to Line Layer")
        self.setModal(True)
        self.resize(350, 200)
        
        # Length field information
        self.length_field = {
            "length": {
                "formula": "$length",
                "description": "Length of the line in layer CRS units",
                "type": QVariant.Double
            }
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Add length field to line layer:")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Field information
        field_info = self.length_field["length"]
        checkbox = QCheckBox("length")
        checkbox.setChecked(True)  # Pre-selected since it's the only option
        checkbox.setEnabled(False)  # Disabled since it's the only option
        checkbox.setToolTip(f"{field_info['description']}\nFormula: {field_info['formula']}")
        layout.addWidget(checkbox)
        
        # Description
        desc_label = QLabel(field_info['description'])
        desc_label.setStyleSheet("color: #666; font-style: italic; margin-left: 20px;")
        layout.addWidget(desc_label)
        
        # Add some spacing
        layout.addStretch()
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        self.create_btn = QPushButton("Create Length Field")
        self.create_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.create_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)


class AddLengthFieldLineAction(BaseAction):
    """Action to add length calculated field to line layers."""
    
    def __init__(self):
        """Initialize the action with metadata and configuration."""
        super().__init__()
        
        # Required properties
        self.action_id = "add_length_field_line"
        self.name = "Add Length Field"
        self.category = "Analysis"
        self.description = "Add calculated length field to line layer. Creates a length field with proper formula and populates all features with calculated values. Automatically handles edit mode."
        self.enabled = True
        
        # Action scoping - works on entire layers (affects all features in layer)
        self.set_action_scope('layer')
        self.set_supported_scopes(['layer'])
        
        # Feature type support - only works with lines
        self.set_supported_click_types(['line', 'multiline'])
        self.set_supported_geometry_types(['line', 'multiline'])
    
    def get_settings_schema(self):
        """Define the settings schema for this action."""
        return {
            'confirm_before_adding': {
                'type': 'bool',
                'default': True,
                'label': 'Confirm Before Adding Field',
                'description': 'Show confirmation dialog before adding length field to the layer',
            },
        }
    
    def get_setting(self, setting_name, default_value=None):
        """Get a setting value for this action."""
        from qgis.PyQt.QtCore import QSettings
        settings = QSettings()
        key = f"RightClickUtilities/{self.action_id}/{setting_name}"
        return settings.value(key, default_value)
    
    def execute(self, context):
        """Execute the add length field action."""
        # Get settings with proper type conversion
        try:
            confirm_before_adding = bool(self.get_setting('confirm_before_adding', True))
        except (ValueError, TypeError) as e:
            self.show_error("Error", f"Invalid setting values: {str(e)}")
            return
        
        # Extract context elements
        detected_features = context.get('detected_features', [])
        
        if not detected_features:
            self.show_error("Error", "No features found at this location")
            return
        
        # Get the first (closest) detected feature
        detected_feature = detected_features[0]
        feature = detected_feature.feature
        layer = detected_feature.layer
        
        # Verify it's a line layer
        if layer.geometryType() != QgsWkbTypes.LineGeometry:
            self.show_error("Error", "This action only works with line layers")
            return
        
        # Show length field dialog
        dialog = LengthFieldDialog()
        if dialog.exec_() != QDialog.Accepted:
            return
        
        # Check if length field already exists
        existing_field_index = layer.fields().indexOf("length")
        if existing_field_index >= 0:
            self.show_warning("Field Exists", "Length field already exists in the layer.")
            return
        
        # Confirm action if setting is enabled
        if confirm_before_adding:
            if not self.confirm_action(
                "Add Length Field",
                f"Are you sure you want to add a length field to layer '{layer.name()}'?\n\nThis will create a 'length' field and populate it with calculated values for all features."
            ):
                return
        
        # Handle edit mode
        edit_result = self.handle_edit_mode(layer, "adding length field")
        if edit_result[0] is None:  # Error occurred
            return
        
        was_in_edit_mode, edit_mode_entered = edit_result
        
        try:
            # Create length field
            length_field = QgsField("length", QMetaType.Double)
            fields_to_add = [length_field]
            
            # Add field to layer
            layer.dataProvider().addAttributes(fields_to_add)
            layer.updateFields()
            
            # Calculate field values directly
            try:
                total_features = layer.featureCount()
                if total_features == 0:
                    self.show_info("Success", "Successfully added length field to empty layer")
                    return
                
                # Create expression for length field
                expression = QgsExpression("$length")
                if expression.hasParserError():
                    self.show_error("Error", f"Expression error: {expression.parserErrorString()}")
                    return
                
                # Process each feature
                success_count = 0
                for i, feature in enumerate(layer.getFeatures()):
                    # Create expression context for this feature
                    context = QgsExpressionContext()
                    context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))
                    context.setFeature(feature)
                    
                    # Calculate length value
                    expression.prepare(context)
                    value = expression.evaluate(context)
                    
                    # Handle value and set attribute
                    if value is None:
                        feature.setAttribute("length", None)
                    elif isinstance(value, (int, float)):
                        if math.isnan(value) or math.isinf(value):
                            feature.setAttribute("length", None)
                        else:
                            feature.setAttribute("length", value)
                    else:
                        feature.setAttribute("length", str(value))
                    
                    # Update the feature
                    if layer.updateFeature(feature):
                        success_count += 1
                
                self.show_info("Success", f"Successfully added length field for {success_count}/{total_features} features")
                
            except Exception as calc_error:
                self.show_error("Error", f"Failed to calculate length values: {str(calc_error)}")
                # Rollback field addition
                try:
                    field_index = layer.fields().indexOf("length")
                    layer.dataProvider().deleteAttributes([field_index])
                    layer.updateFields()
                except Exception as rollback_error:
                    self.show_warning("Rollback Warning", f"Could not rollback field addition: {str(rollback_error)}")
                return
            
            # Commit changes
            if not self.commit_changes(layer, "adding length field"):
                return
            
        except Exception as e:
            self.show_error("Error", f"Failed to add length field: {str(e)}")
            self.rollback_changes(layer)
            
        finally:
            # Exit edit mode if we entered it
            self.exit_edit_mode(layer, edit_mode_entered)


# REQUIRED: Create global instance for automatic discovery
add_length_field_line_action = AddLengthFieldLineAction()
