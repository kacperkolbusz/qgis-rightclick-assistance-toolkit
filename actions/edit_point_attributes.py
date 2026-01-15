"""
Edit Point Attributes Action for Right-click Utilities and Shortcuts Hub

Opens an editable window for point features where users can view and modify all attribute values.
Automatically handles edit mode for the layer.
"""

from .base_action import BaseAction
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                                 QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, 
                                 QComboBox, QCheckBox, QPushButton, QLabel, QScrollArea,
                                 QWidget, QMessageBox, QDateEdit, QTimeEdit)
from qgis.PyQt.QtCore import Qt, QDate, QTime, QDateTime
from qgis.PyQt.QtGui import QFont
from qgis.core import QgsField, QgsVectorLayer, QgsFeature
from qgis.utils import iface
import datetime


class AttributeEditDialog(QDialog):
    """Dialog for editing feature attributes."""
    
    def __init__(self, feature, layer, parent=None, show_success_messages=True, show_error_messages=True, show_warning_messages=True):
        super().__init__(parent)
        self.feature = feature
        self.layer = layer
        self.original_values = {}
        self.field_widgets = {}
        self.edit_mode_entered = False
        self.show_success_messages = show_success_messages
        self.show_error_messages = show_error_messages
        self.show_warning_messages = show_warning_messages
        
        self.setWindowTitle(f"Edit Attributes - {layer.name()}")
        self.setModal(True)
        self.resize(600, 700)
        
        # Apply QGIS-like styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
                color: #333333;
            }
            QLabel {
                color: #333333;
                font-weight: bold;
            }
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox, QDateEdit {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 4px;
                font-size: 11px;
            }
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QDateEdit:focus {
                border: 2px solid #4CAF50;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton#cancelButton {
                background-color: #f44336;
            }
            QPushButton#cancelButton:hover {
                background-color: #da190b;
            }
            QPushButton#cancelButton:pressed {
                background-color: #c41e3a;
            }
            QScrollArea {
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: white;
            }
            QFormLayout {
                spacing: 8px;
            }
        """)
        
        self.setup_ui()
        self.enter_edit_mode()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel(f"Feature ID: {self.feature.id()}")
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(12)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Scrollable form area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        form_layout = QFormLayout(scroll_widget)
        
        # Create form fields for each attribute
        fields = self.layer.fields()
        attributes = self.feature.attributes()
        
        for i, field in enumerate(fields):
            field_name = field.name()
            field_type = field.type()
            field_value = attributes[i] if i < len(attributes) else None
            
            # Store original value
            self.original_values[field_name] = field_value
            
            # Create appropriate widget based on field type
            widget = self.create_field_widget(field, field_value)
            self.field_widgets[field_name] = widget
            
            # Add to form
            form_layout.addRow(f"{field_name}:", widget)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Push buttons to the right
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.cancel_changes)
        
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)
    
    def create_field_widget(self, field, value):
        """Create appropriate widget for field type."""
        field_type = field.type()
        field_name = field.name()
        
        # Handle NULL values
        if value is None or value == "NULL":
            value = ""
        
        # Use field type name for more reliable type checking
        field_type_name = field.typeName().lower()
        
        # String fields
        if 'string' in field_type_name or 'text' in field_type_name:
            if field.length() > 100:  # Long text field
                widget = QTextEdit()
                widget.setPlainText(str(value))
                widget.setMaximumHeight(100)
            else:  # Short text field
                widget = QLineEdit()
                widget.setText(str(value))
            return widget
        
        # Integer fields
        elif 'int' in field_type_name and 'long' not in field_type_name:
            widget = QLineEdit()
            widget.setText(str(value) if value is not None else "0")
            return widget
        
        # Long integer fields
        elif 'long' in field_type_name or 'int64' in field_type_name:
            widget = QLineEdit()
            widget.setText(str(value) if value is not None else "0")
            return widget
        
        # Double/Real fields
        elif 'double' in field_type_name or 'real' in field_type_name or 'float' in field_type_name:
            widget = QLineEdit()
            widget.setText(str(value) if value is not None else "0.0")
            return widget
        
        # Boolean fields
        elif 'bool' in field_type_name:
            widget = QCheckBox()
            try:
                widget.setChecked(bool(value) if value is not None else False)
            except (ValueError, TypeError):
                widget.setChecked(False)
            return widget
        
        # Date fields
        elif 'date' in field_type_name and 'time' not in field_type_name:
            widget = QDateEdit()
            widget.setCalendarPopup(True)
            try:
                if value and str(value) != "":
                    if isinstance(value, str):
                        # Try to parse various date formats
                        for fmt in ['yyyy-MM-dd', 'dd/MM/yyyy', 'MM/dd/yyyy']:
                            try:
                                date = QDate.fromString(str(value), fmt)
                                if date.isValid():
                                    widget.setDate(date)
                                    break
                            except:
                                continue
                    else:
                        widget.setDate(QDate.fromString(str(value), 'yyyy-MM-dd'))
                else:
                    widget.setDate(QDate.currentDate())
            except:
                widget.setDate(QDate.currentDate())
            return widget
        
        # DateTime fields
        elif 'datetime' in field_type_name or 'timestamp' in field_type_name:
            widget = QDateEdit()
            widget.setCalendarPopup(True)
            widget.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
            try:
                if value and str(value) != "":
                    if isinstance(value, str):
                        # Try to parse datetime
                        try:
                            dt = QDateTime.fromString(str(value), 'yyyy-MM-dd hh:mm:ss')
                            if dt.isValid():
                                widget.setDateTime(dt)
                            else:
                                widget.setDateTime(QDateTime.currentDateTime())
                        except:
                            widget.setDateTime(QDateTime.currentDateTime())
                    else:
                        widget.setDateTime(QDateTime.currentDateTime())
                else:
                    widget.setDateTime(QDateTime.currentDateTime())
            except:
                widget.setDateTime(QDateTime.currentDateTime())
            return widget
        
        # Default to text field for unknown types
        else:
            widget = QLineEdit()
            widget.setText(str(value) if value is not None else "")
            return widget
    
    def get_widget_value(self, widget, field_type):
        """Get value from widget based on field type."""
        if isinstance(widget, QLineEdit):
            return widget.text()
        elif isinstance(widget, QTextEdit):
            return widget.toPlainText()
        elif isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QDateEdit):
            # Check if this is a datetime field by looking at the display format
            if widget.displayFormat() == "yyyy-MM-dd hh:mm:ss":
                return widget.dateTime().toString('yyyy-MM-dd hh:mm:ss')
            else:
                return widget.date().toString('yyyy-MM-dd')
        else:
            return str(widget.text()) if hasattr(widget, 'text') else ""
    
    def enter_edit_mode(self):
        """Enter edit mode for the layer."""
        if not self.layer.isEditable():
            if self.layer.startEditing():
                self.edit_mode_entered = True
            else:
                if self.show_error_messages:
                    QMessageBox.warning(self, "Edit Mode Error", 
                                      "Could not enter edit mode for this layer.")
                self.reject()
    
    def exit_edit_mode(self):
        """Exit edit mode for the layer if we entered it."""
        if self.edit_mode_entered and self.layer.isEditable():
            self.layer.commitChanges()
            self.edit_mode_entered = False
    
    def save_changes(self):
        """Save changes to the feature."""
        try:
            # Get field values
            fields = self.layer.fields()
            new_attributes = []
            
            for i, field in enumerate(fields):
                field_name = field.name()
                widget = self.field_widgets.get(field_name)
                
                if widget:
                    value = self.get_widget_value(widget, field.type())
                    new_attributes.append(value)
                else:
                    # Keep original value if no widget
                    original_value = self.original_values.get(field_name)
                    new_attributes.append(original_value)
            
            # Update feature attributes
            self.feature.setAttributes(new_attributes)
            
            # Update feature in layer
            if self.layer.updateFeature(self.feature):
                # Commit changes
                if self.layer.commitChanges():
                    # Show success message only if enabled in settings
                    if self.show_success_messages:
                        QMessageBox.information(self, "Success", 
                                              "Feature attributes updated successfully!")
                    self.accept()
                else:
                    # Show error message only if enabled in settings
                    if self.show_error_messages:
                        QMessageBox.warning(self, "Save Error", 
                                          "Could not save changes to the layer.")
                    self.layer.rollBack()
            else:
                # Show error message only if enabled in settings
                if self.show_error_messages:
                    QMessageBox.warning(self, "Update Error", 
                                      "Could not update the feature.")
                self.layer.rollBack()
                
        except Exception as e:
            # Show error message only if enabled in settings
            if self.show_error_messages:
                QMessageBox.critical(self, "Error", f"Failed to save changes: {str(e)}")
            self.layer.rollBack()
    
    def cancel_changes(self):
        """Cancel changes and close dialog."""
        self.layer.rollBack()
        self.reject()
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        self.layer.rollBack()
        super().closeEvent(event)


class EditPointAttributesAction(BaseAction):
    """Action to edit point feature attributes in a dialog window."""
    
    def __init__(self):
        super().__init__()
        
        # Required properties
        self.action_id = "edit_point_attributes"
        self.name = "Edit Point Attributes"
        self.category = "Editing"
        self.description = "Open an editable window to view and modify all attribute values for the selected point feature. Automatically handles edit mode for the layer and saves changes when confirmed."
        self.enabled = True
        
        # Action scoping - works on individual features
        self.set_action_scope('feature')
        self.set_supported_scopes(['feature'])
        
        # Feature type support - only works with points
        self.set_supported_click_types(['point', 'multipoint'])
        self.set_supported_geometry_types(['point', 'multipoint'])
    
    def get_settings_schema(self):
        """
        Define the settings schema for this action.
        
        Returns:
            dict: Settings schema with setting definitions
        """
        return {
            'show_success_messages': {
                'type': 'bool',
                'default': True,
                'label': 'Show Success Messages',
                'description': 'Display success popup messages when changes are saved',
            },
            'show_error_messages': {
                'type': 'bool',
                'default': True,
                'label': 'Show Error Messages',
                'description': 'Display error popup messages when something goes wrong',
            },
            'show_warning_messages': {
                'type': 'bool',
                'default': True,
                'label': 'Show Warning Messages',
                'description': 'Display warning popup messages for non-critical issues',
            },
            'confirm_save': {
                'type': 'bool',
                'default': False,
                'label': 'Confirm Before Saving',
                'description': 'Show confirmation dialog before saving attribute changes',
            },
            'auto_commit_changes': {
                'type': 'bool',
                'default': True,
                'label': 'Auto-commit Changes',
                'description': 'Automatically commit changes to the layer when saving',
            },
            'show_field_types': {
                'type': 'bool',
                'default': False,
                'label': 'Show Field Types',
                'description': 'Display field types in the attribute editing dialog',
            },
        }
    
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
    
    def execute(self, context):
        """Execute the edit point attributes action."""
        # Get settings
        show_success_messages = self.get_setting('show_success_messages', True)
        show_error_messages = self.get_setting('show_error_messages', True)
        show_warning_messages = self.get_setting('show_warning_messages', True)
        confirm_save = self.get_setting('confirm_save', False)
        auto_commit = self.get_setting('auto_commit_changes', True)
        
        # Extract context elements
        detected_features = context.get('detected_features', [])
        
        if not detected_features:
            if show_error_messages:
                self.show_error("Error", "No features found at this location")
            return
        
        # Get the first (closest) detected feature
        detected_feature = detected_features[0]
        feature = detected_feature.feature
        layer = detected_feature.layer
        
        # Check if layer is editable
        if not layer.isEditable() and not layer.startEditing():
            if show_error_messages:
                self.show_error("Edit Mode Error", 
                              f"Could not enter edit mode for layer '{layer.name()}'. "
                              "The layer may be read-only or locked.")
            return
        
        try:
            # Create and show the attribute editing dialog with popup settings
            dialog = AttributeEditDialog(
                feature, layer, iface.mainWindow(),
                show_success_messages=show_success_messages,
                show_error_messages=show_error_messages,
                show_warning_messages=show_warning_messages
            )
            
            if dialog.exec_() == QDialog.Accepted:
                # Changes were saved successfully
                if show_success_messages:
                    self.show_info("Success", 
                                 f"Attributes for feature ID {feature.id()} have been updated successfully.")
            else:
                # User cancelled or there was an error
                pass
                
        except Exception as e:
            if show_error_messages:
                self.show_error("Error", f"Failed to open attribute editor: {str(e)}")
            # Ensure we exit edit mode if there was an error
            if layer.isEditable():
                layer.rollBack()


# REQUIRED: Create global instance for automatic discovery
edit_point_attributes_action = EditPointAttributesAction()
