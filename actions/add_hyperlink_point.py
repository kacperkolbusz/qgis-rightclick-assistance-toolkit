"""
Add Hyperlink to Point Action for Right-click Utilities and Shortcuts Hub

Adds a clickable hyperlink to point features. User can input a URL that will be stored
with the feature. When the feature is clicked (using the hyperlink map tool), the URL opens in a browser.
"""

from .base_action import BaseAction
from qgis.core import QgsField, QgsWkbTypes, QgsFeature, QgsPointXY, QgsGeometry, QgsRectangle
from qgis.gui import QgsMapTool
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFormLayout, QLineEdit, QMessageBox
)
from qgis.PyQt.QtCore import QVariant, QMetaType, Qt
from qgis.PyQt.QtGui import QCursor
import re
import webbrowser
from urllib.parse import urlparse


class HyperlinkInputDialog(QDialog):
    """Dialog for user input of hyperlink URL with option to open it."""
    
    def __init__(self, parent=None, current_url=None, field_name="hyperlink", can_open=True):
        super().__init__(parent)
        self.setWindowTitle("Add/Open Hyperlink to Point")
        self.setModal(True)
        self.resize(500, 200)
        
        # Store original URL for "Open Current Link" button
        self.original_url = current_url
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # URL input
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://example.com or http://example.com")
        if current_url:
            self.url_edit.setText(str(current_url))
        form_layout.addRow("URL:", self.url_edit)
        
        url_help = QLabel("Enter a valid URL (http:// or https://). Leave empty to remove existing hyperlink.")
        url_help.setStyleSheet("color: gray; font-size: 10px;")
        url_help.setWordWrap(True)
        form_layout.addRow("", url_help)
        
        layout.addLayout(form_layout)
        
        # Open link option (show if can_open is True)
        if can_open:
            from qgis.PyQt.QtWidgets import QGroupBox, QCheckBox
            open_group = QGroupBox("Open Link")
            open_layout = QVBoxLayout()
            
            self.open_link_checkbox = QCheckBox("Open this link in browser after setting")
            self.open_link_checkbox.setChecked(False)
            if current_url:
                self.open_link_checkbox.setToolTip("Check to open the URL after setting it (works with current or new URL)")
            else:
                self.open_link_checkbox.setToolTip("Check to open the URL after setting it")
            open_layout.addWidget(self.open_link_checkbox)
            
            open_group.setLayout(open_layout)
            layout.addWidget(open_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Set Hyperlink")
        if can_open and current_url:
            self.open_button = QPushButton("Open Current Link")
            self.open_button.clicked.connect(self.open_current_and_close)
            button_layout.addWidget(self.open_button)
        self.cancel_button = QPushButton("Cancel")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Set focus to URL input
        self.url_edit.setFocus()
        self.url_edit.selectAll()
    
    def get_url(self):
        """Get the input URL."""
        url = self.url_edit.text().strip()
        return url if url else None
    
    def should_open_link(self):
        """Check if user wants to open the link."""
        return hasattr(self, 'open_link_checkbox') and self.open_link_checkbox.isChecked()
    
    def open_current_and_close(self):
        """Open the original current URL and close the dialog without saving."""
        url = self.original_url
        if url:
            try:
                import webbrowser
                from urllib.parse import urlparse
                
                url_str = str(url).strip()
                # Validate and open URL
                parsed = urlparse(url_str)
                if parsed.scheme in ('http', 'https'):
                    webbrowser.open(url_str)
                else:
                    # Try to fix URL
                    if not url_str.startswith(('http://', 'https://')):
                        url_str = 'https://' + url_str
                        webbrowser.open(url_str)
            except Exception:
                pass
        self.reject()  # Close without saving
    
    def validate_url(self, url):
        """Validate URL format."""
        if not url:
            return True, None  # Empty URL is valid (removes hyperlink)
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if url_pattern.match(url):
            return True, None
        else:
            # Try to fix common issues
            if not url.startswith(('http://', 'https://')):
                fixed_url = 'https://' + url
                if url_pattern.match(fixed_url):
                    return True, fixed_url
            return False, "Invalid URL format. Must start with http:// or https://"


class OpenHyperlinkMapTool(QgsMapTool):
    """Custom map tool for opening hyperlinks when clicking features."""
    
    def __init__(self, canvas, parent_action, field_name="hyperlink"):
        super().__init__(canvas)
        self.canvas = canvas
        self.parent_action = parent_action
        self.field_name = field_name
        self.original_tool = None
        
        # Set cursor to indicate hyperlink mode
        self.setCursor(QCursor(Qt.PointingHandCursor))
    
    def canvasPressEvent(self, event):
        """Handle canvas press to open hyperlink if feature has one."""
        if event.button() == 1:  # Left click
            # Get click point
            click_point = self.toMapCoordinates(event.pos())
            
            # Find features at click location
            from qgis.core import QgsProject
            
            # Search radius in map units (small search area)
            search_radius = self.canvas.mapUnitsPerPixel() * 5  # 5 pixels
            
            # Create search rectangle
            search_rect = QgsRectangle(
                click_point.x() - search_radius,
                click_point.y() - search_radius,
                click_point.x() + search_radius,
                click_point.y() + search_radius
            )
            
            # Get all layers
            project = QgsProject.instance()
            layers = project.mapLayers().values()
            
            clicked_feature = None
            clicked_layer = None
            min_distance = float('inf')
            
            # Search through all vector layers
            for layer in layers:
                if not hasattr(layer, 'fields') or not hasattr(layer, 'getFeatures'):
                    continue
                
                # Check if layer has hyperlink field
                field_index = layer.fields().indexOf(self.field_name)
                if field_index < 0:
                    continue
                
                # Get features in search area
                request = layer.getFeatures(search_rect)
                
                for feature in request:
                    geometry = feature.geometry()
                    if not geometry:
                        continue
                    
                    # Check if click point is on/near the feature
                    if geometry.type() == QgsWkbTypes.PointGeometry:
                        point = geometry.asPoint()
                        distance = click_point.distance(point)
                        if distance <= search_radius:
                            if distance < min_distance:
                                min_distance = distance
                                clicked_feature = feature
                                clicked_layer = layer
                    elif geometry.type() == QgsWkbTypes.LineGeometry:
                        # For lines, check distance to line
                        distance = geometry.distance(QgsGeometry.fromPointXY(click_point))
                        if distance <= search_radius:
                            if distance < min_distance:
                                min_distance = distance
                                clicked_feature = feature
                                clicked_layer = layer
                    elif geometry.type() == QgsWkbTypes.PolygonGeometry:
                        # For polygons, check if point is inside
                        if geometry.contains(QgsGeometry.fromPointXY(click_point)):
                            clicked_feature = feature
                            clicked_layer = layer
                            min_distance = 0
                            break
                        else:
                            # Check distance to boundary
                            distance = geometry.boundary().distance(QgsGeometry.fromPointXY(click_point))
                            if distance <= search_radius:
                                if distance < min_distance:
                                    min_distance = distance
                                    clicked_feature = feature
                                    clicked_layer = layer
            
            # If feature found, try to open URL
            if clicked_feature and clicked_layer:
                field_index = clicked_layer.fields().indexOf(self.field_name)
                if field_index >= 0:
                    url = clicked_feature.attribute(field_index)
                    if url and str(url).strip():
                        url = str(url).strip()
                        try:
                            # Validate and open URL
                            parsed = urlparse(url)
                            if parsed.scheme in ('http', 'https'):
                                webbrowser.open(url)
                                if self.parent_action.get_setting('show_open_success_message', True):
                                    self.parent_action.show_info("Hyperlink Opened", f"Opening URL:\n{url}")
                            else:
                                # Try to fix URL
                                if not url.startswith(('http://', 'https://')):
                                    url = 'https://' + url
                                    webbrowser.open(url)
                                    if self.parent_action.get_setting('show_open_success_message', True):
                                        self.parent_action.show_info("Hyperlink Opened", f"Opening URL:\n{url}")
                                else:
                                    self.parent_action.show_warning("Invalid URL", f"Invalid URL format: {url}")
                        except Exception as e:
                            self.parent_action.show_error("Error", f"Failed to open URL: {str(e)}")
                    else:
                        if self.parent_action.get_setting('show_no_hyperlink_message', False):
                            self.parent_action.show_info("No Hyperlink", f"Feature ID {clicked_feature.id()} does not have a hyperlink set.")
            else:
                if self.parent_action.get_setting('show_no_feature_message', False):
                    self.parent_action.show_info("No Feature", "No feature with hyperlink found at this location.")
        
        elif event.button() == 2:  # Right click to deactivate
            self._deactivate()
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self._deactivate()
        else:
            super().keyPressEvent(event)
    
    def _deactivate(self):
        """Deactivate the hyperlink tool."""
        # Restore original map tool
        if self.original_tool:
            self.canvas.setMapTool(self.original_tool)
        else:
            self.canvas.unsetMapTool(self)
        
        if self.parent_action.get_setting('show_deactivation_message', False):
            self.parent_action.show_info("Hyperlink Tool Deactivated", "Right-click or press ESC to deactivate.")


class AddHyperlinkPointAction(BaseAction):
    """
    Action to add a clickable hyperlink to point features.
    
    This action allows users to associate a URL with a point feature. The URL is stored
    in a field called 'hyperlink' (or configurable field name). Users can then use the
    hyperlink map tool to click on features and open their associated URLs.
    """
    
    def __init__(self):
        """Initialize the action with metadata and configuration."""
        super().__init__()
        
        # Required properties
        self.action_id = "add_hyperlink_point"
        self.name = "Add/Open Hyperlink to Point"
        self.category = "Editing"
        self.description = "Add or open a clickable hyperlink for the selected point feature. User can input a URL that will be stored with the feature. Option to open the link immediately in browser. After setting, you can activate the click tool to click on features and open their hyperlinks."
        self.enabled = True
        
        # Action scoping - this works on individual features
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
            # FIELD SETTINGS
            'hyperlink_field_name': {
                'type': 'str',
                'default': 'hyperlink',
                'label': 'Hyperlink Field Name',
                'description': 'Name of the field to store hyperlink URLs',
            },
            'auto_create_field': {
                'type': 'bool',
                'default': True,
                'label': 'Auto-create Field',
                'description': 'Automatically create the hyperlink field if it does not exist',
            },
            
            # BEHAVIOR SETTINGS
            'confirm_before_adding': {
                'type': 'bool',
                'default': False,
                'label': 'Confirm Before Adding',
                'description': 'Show confirmation dialog before adding/updating hyperlink',
            },
            'show_success_message': {
                'type': 'bool',
                'default': True,
                'label': 'Show Success Message',
                'description': 'Display a message when hyperlink is added successfully',
            },
            'auto_commit_changes': {
                'type': 'bool',
                'default': True,
                'label': 'Auto-commit Changes',
                'description': 'Automatically commit changes after adding hyperlink (recommended)',
            },
            'handle_edit_mode_automatically': {
                'type': 'bool',
                'default': True,
                'label': 'Handle Edit Mode Automatically',
                'description': 'Automatically enter/exit edit mode as needed',
            },
            'rollback_on_error': {
                'type': 'bool',
                'default': True,
                'label': 'Rollback on Error',
                'description': 'Rollback changes if operation fails',
            },
            
            # CLICK TOOL SETTINGS
            'activate_click_tool_after_adding': {
                'type': 'bool',
                'default': True,
                'label': 'Activate Click Tool After Adding',
                'description': 'Automatically activate the click-to-open tool after adding a hyperlink',
            },
            'show_open_success_message': {
                'type': 'bool',
                'default': True,
                'label': 'Show Open Success Message',
                'description': 'Display a message when hyperlink is opened successfully',
            },
            'show_no_hyperlink_message': {
                'type': 'bool',
                'default': False,
                'label': 'Show No Hyperlink Message',
                'description': 'Display a message when clicking a feature without a hyperlink',
            },
            'show_no_feature_message': {
                'type': 'bool',
                'default': False,
                'label': 'Show No Feature Message',
                'description': 'Display a message when clicking where no feature is found',
            },
            'show_deactivation_message': {
                'type': 'bool',
                'default': False,
                'label': 'Show Deactivation Message',
                'description': 'Display a message when deactivating the hyperlink tool',
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
        """
        Execute the add hyperlink action.
        
        Args:
            context (dict): Context dictionary with click information
        """
        # Get settings with proper type conversion
        try:
            field_name = str(self.get_setting('hyperlink_field_name', 'hyperlink'))
            auto_create_field = bool(self.get_setting('auto_create_field', True))
            confirm_before_adding = bool(self.get_setting('confirm_before_adding', False))
            show_success = bool(self.get_setting('show_success_message', True))
            auto_commit = bool(self.get_setting('auto_commit_changes', True))
            handle_edit_mode = bool(self.get_setting('handle_edit_mode_automatically', True))
            rollback_on_error = bool(self.get_setting('rollback_on_error', True))
        except (ValueError, TypeError) as e:
            self.show_error("Error", f"Invalid setting values: {str(e)}")
            return
        
        # Extract context elements
        detected_features = context.get('detected_features', [])
        
        if not detected_features:
            self.show_error("Error", "No point features found at this location")
            return
        
        # Get the first (closest) detected feature
        detected_feature = detected_features[0]
        feature = detected_feature.feature
        layer = detected_feature.layer
        
        # Get current URL if field exists
        current_url = None
        field_index = layer.fields().indexOf(field_name)
        if field_index >= 0:
            current_url = feature.attribute(field_name)
        
        # Show input dialog
        dialog = HyperlinkInputDialog(None, current_url=current_url, field_name=field_name, can_open=True)
        
        dialog_result = dialog.exec_()
        
        if dialog_result != QDialog.Accepted:
            return  # User cancelled
        
        # Get the user input URL
        url = dialog.get_url()
        
        # Check if we should open the link after setting it
        should_open = dialog.should_open_link()
        
        # Validate URL
        is_valid, fixed_url = dialog.validate_url(url)
        if not is_valid:
            self.show_error("Invalid URL", "Please enter a valid URL starting with http:// or https://")
            return
        
        # Use fixed URL if validation suggested one
        if fixed_url:
            url = fixed_url
            reply = QMessageBox.question(
                None,
                "URL Fixed",
                f"URL was automatically corrected to:\n{url}\n\nUse this URL?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Confirm if enabled
        if confirm_before_adding:
            if url:
                message = f"Set hyperlink for point feature ID {feature.id()}?\n\nURL: {url}"
            else:
                message = f"Remove hyperlink from point feature ID {feature.id()}?"
            
            if not self.confirm_action("Add Hyperlink", message):
                return
        
        # Handle edit mode
        edit_result = None
        was_in_edit_mode = False
        edit_mode_entered = False
        
        if handle_edit_mode:
            edit_result = self.handle_edit_mode(layer, "adding hyperlink")
            if edit_result[0] is None:  # Error occurred
                return
            was_in_edit_mode, edit_mode_entered = edit_result
        
        try:
            # Check if field exists
            field_index = layer.fields().indexOf(field_name)
            
            if field_index < 0:
                # Field doesn't exist - create it if enabled
                if auto_create_field:
                    new_field = QgsField(field_name, QMetaType.QString)
                    layer.dataProvider().addAttributes([new_field])
                    layer.updateFields()
                    field_index = layer.fields().indexOf(field_name)
                else:
                    self.show_error("Error", f"Field '{field_name}' does not exist. Enable 'Auto-create Field' in settings to create it automatically.")
                    return
            
            # Set the URL attribute
            feature.setAttribute(field_index, url if url else None)
            
            # Update the feature
            if not layer.updateFeature(feature):
                self.show_error("Error", "Failed to update feature with hyperlink")
                return
            
            # Commit changes if enabled
            if auto_commit and handle_edit_mode:
                if not self.commit_changes(layer, "adding hyperlink"):
                    return
            
            # Show success message if enabled
            if show_success:
                if url:
                    self.show_info("Success", f"Hyperlink added to point feature ID {feature.id()}\n\nURL: {url}")
                else:
                    self.show_info("Success", f"Hyperlink removed from point feature ID {feature.id()}")
            
            # Open link if requested
            if should_open and url:
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    if parsed.scheme in ('http', 'https'):
                        webbrowser.open(url)
                    else:
                        if not url.startswith(('http://', 'https://')):
                            url = 'https://' + url
                        webbrowser.open(url)
                    if show_success:
                        self.show_info("Hyperlink Opened", f"Opening URL:\n{url}")
                except Exception as e:
                    self.show_error("Error", f"Failed to open URL: {str(e)}")
            
            # Activate click tool if enabled
            activate_click_tool = bool(self.get_setting('activate_click_tool_after_adding', True))
            if activate_click_tool and url:
                canvas = context.get('canvas')
                if canvas:
                    try:
                        # Check if tool is already active
                        current_tool = canvas.mapTool()
                        if isinstance(current_tool, OpenHyperlinkMapTool):
                            # Already active, just show message
                            pass
                        else:
                            # Activate the hyperlink map tool
                            hyperlink_tool = OpenHyperlinkMapTool(canvas, self, field_name)
                            hyperlink_tool.original_tool = current_tool
                            canvas.setMapTool(hyperlink_tool)
                            self.show_info("Click Tool Activated", 
                                "Click on features to open their hyperlinks.\n\n"
                                "Right-click or press ESC to deactivate.")
                    except Exception as e:
                        # Silently fail if can't activate tool
                        pass
            
        except Exception as e:
            self.show_error("Error", f"Failed to add hyperlink: {str(e)}")
            if rollback_on_error and handle_edit_mode:
                self.rollback_changes(layer)
        
        finally:
            # Exit edit mode if we entered it
            if handle_edit_mode:
                self.exit_edit_mode(layer, edit_mode_entered)


# REQUIRED: Create global instance for automatic discovery
add_hyperlink_point = AddHyperlinkPointAction()

