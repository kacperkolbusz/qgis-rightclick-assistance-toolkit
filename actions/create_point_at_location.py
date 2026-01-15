"""
Create Point at Location Action for Right-click Utilities and Shortcuts Hub

Creates a point feature at the clicked location in a temporary layer.
Works universally on any canvas location with proper CRS handling.
"""

from .base_action import BaseAction


class CreatePointAtLocationAction(BaseAction):
    """Action to create a point at the clicked location in a temporary layer."""
    
    def __init__(self):
        """Initialize the action with metadata and configuration."""
        super().__init__()
        
        # Required properties
        self.action_id = "create_point_at_location"
        self.name = "Create Point at Location"
        self.category = "Editing"
        self.description = "Create a point feature at the clicked location in a temporary layer. The point is added to a new temporary layer that persists until QGIS is closed. Automatically handles CRS and adds the layer to the project."
        self.enabled = True
        
        # Action scoping - this works universally
        self.set_action_scope('universal')
        self.set_supported_scopes(['universal'])
        
        # Feature type support - works everywhere
        self.set_supported_click_types(['universal'])
        self.set_supported_geometry_types(['universal'])
    
    def get_settings_schema(self):
        """
        Define the settings schema for this action.
        
        Returns:
            dict: Settings schema with setting definitions
        """
        return {
            # LAYER SETTINGS
            'layer_name': {
                'type': 'str',
                'default': 'Points',
                'label': 'Layer Name',
                'description': 'Name for the temporary point layer. If layer already exists, points will be added to it.',
            },
            'add_to_existing_layer': {
                'type': 'bool',
                'default': True,
                'label': 'Add to Existing Layer',
                'description': 'If a layer with the same name exists, add points to it instead of creating a new layer',
            },
            
            # POINT SETTINGS
            'add_timestamp': {
                'type': 'bool',
                'default': False,
                'label': 'Add Timestamp',
                'description': 'Add timestamp field with creation date and time',
            },
            'add_coordinates': {
                'type': 'bool',
                'default': False,
                'label': 'Add Coordinates',
                'description': 'Add X and Y coordinate fields to the point attributes',
            },
            'add_id': {
                'type': 'bool',
                'default': True,
                'label': 'Add ID Field',
                'description': 'Add sequential ID field to each point',
            },
            
            # BEHAVIOR SETTINGS
            'auto_zoom': {
                'type': 'bool',
                'default': False,
                'label': 'Auto Zoom to Point',
                'description': 'Automatically zoom to the created point',
            },
            'show_confirmation': {
                'type': 'bool',
                'default': False,
                'label': 'Show Confirmation',
                'description': 'Show confirmation message when point is created',
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
        Execute the create point at location action.
        
        Args:
            context (dict): Context dictionary with click information
        """
        # Get settings with proper type conversion
        try:
            layer_name = str(self.get_setting('layer_name', 'Points'))
            add_to_existing_layer = bool(self.get_setting('add_to_existing_layer', True))
            add_timestamp = bool(self.get_setting('add_timestamp', False))
            add_coordinates = bool(self.get_setting('add_coordinates', False))
            add_id = bool(self.get_setting('add_id', True))
            auto_zoom = bool(self.get_setting('auto_zoom', False))
            show_confirmation = bool(self.get_setting('show_confirmation', False))
        except (ValueError, TypeError) as e:
            self.show_error("Error", f"Invalid setting values: {str(e)}")
            return
        
        # Extract context elements
        click_point = context.get('click_point')
        canvas = context.get('canvas')
        
        if not click_point:
            self.show_error("Error", "No click point available")
            return
        
        if not canvas:
            self.show_error("Error", "Map canvas not available")
            return
        
        try:
            # Get canvas CRS for proper coordinate handling
            canvas_crs = canvas.mapSettings().destinationCrs()
            
            # Check if layer already exists
            existing_layer = None
            if add_to_existing_layer:
                from qgis.core import QgsProject
                project = QgsProject.instance()
                layers = project.mapLayersByName(layer_name)
                for layer in layers:
                    if layer.geometryType() == 0:  # Point layer
                        existing_layer = layer
                        break
            
            if existing_layer:
                # Add point to existing layer
                self._add_point_to_layer(existing_layer, click_point, canvas_crs, {
                    'add_timestamp': add_timestamp,
                    'add_coordinates': add_coordinates,
                    'add_id': add_id,
                })
                
                # Refresh layer
                existing_layer.triggerRepaint()
                
                if show_confirmation:
                    self.show_info("Point Added", f"Point added to existing layer '{layer_name}'")
            else:
                # Create new temporary layer
                point_layer = self._create_point_layer(
                    layer_name, click_point, canvas_crs, {
                        'add_timestamp': add_timestamp,
                        'add_coordinates': add_coordinates,
                        'add_id': add_id,
                    }
                )
                
                if not point_layer:
                    self.show_error("Error", "Failed to create point layer")
                    return
                
                # Add layer to project
                from qgis.core import QgsProject
                project = QgsProject.instance()
                project.addMapLayer(point_layer)
                
                if show_confirmation:
                    self.show_info("Point Created", f"Point created in new layer '{layer_name}'")
            
            # Auto zoom if requested
            if auto_zoom:
                from qgis.core import QgsRectangle
                buffer_distance = canvas.mapSettings().mapUnitsPerPixel() * 50  # 50 pixels buffer
                extent = QgsRectangle(
                    click_point.x() - buffer_distance,
                    click_point.y() - buffer_distance,
                    click_point.x() + buffer_distance,
                    click_point.y() + buffer_distance
                )
                canvas.setExtent(extent)
                canvas.refresh()
            
        except Exception as e:
            self.show_error("Error", f"Failed to create point: {str(e)}")
    
    def _create_point_layer(self, layer_name, point, crs, settings):
        """
        Create a new temporary point layer with a point feature.
        
        Args:
            layer_name (str): Name for the layer
            point (QgsPointXY): Point to add
            crs: Coordinate reference system
            settings (dict): Settings dictionary
            
        Returns:
            QgsVectorLayer: Created layer or None if failed
        """
        try:
            from qgis.core import QgsVectorLayer, QgsFields, QgsField, QgsFeature, QgsGeometry, QgsProject
            from qgis.PyQt.QtCore import QVariant
            
            # Create memory layer
            crs_string = crs.authid() if crs.authid() else crs.toWkt()
            layer = QgsVectorLayer(f"Point?crs={crs_string}", layer_name, "memory")
            
            if not layer.isValid():
                self.show_error("Error", f"Failed to create valid temporary layer. CRS: {crs_string}")
                return None
            
            # Define fields
            fields = QgsFields()
            
            if settings['add_id']:
                fields.append(QgsField('id', QVariant.Int))
            
            if settings['add_coordinates']:
                fields.append(QgsField('x', QVariant.Double))
                fields.append(QgsField('y', QVariant.Double))
            
            if settings['add_timestamp']:
                fields.append(QgsField('created_at', QVariant.String))
            
            if fields.count() > 0:
                layer.dataProvider().addAttributes(fields.toList())
                layer.updateFields()
            
            # Create point feature
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPointXY(point))
            
            # Set attributes
            attributes = []
            if settings['add_id']:
                attributes.append(1)  # First point gets ID 1
            
            if settings['add_coordinates']:
                attributes.append(float(point.x()))
                attributes.append(float(point.y()))
            
            if settings['add_timestamp']:
                from datetime import datetime
                attributes.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            feature.setAttributes(attributes)
            
            # Add feature to layer
            layer.dataProvider().addFeature(feature)
            layer.updateExtents()
            
            return layer
            
        except Exception as e:
            self.show_error("Error", f"Failed to create point layer: {str(e)}")
            return None
    
    def _add_point_to_layer(self, layer, point, crs, settings):
        """
        Add a point to an existing layer.
        
        Args:
            layer (QgsVectorLayer): Existing layer to add point to
            point (QgsPointXY): Point to add
            crs: Coordinate reference system
            settings (dict): Settings dictionary
        """
        try:
            from qgis.core import QgsFeature, QgsGeometry, QgsField
            from qgis.PyQt.QtCore import QVariant
            
            # Transform point if CRS differs
            if layer.crs() != crs:
                from qgis.core import QgsCoordinateTransform, QgsProject
                transform = QgsCoordinateTransform(crs, layer.crs(), QgsProject.instance())
                try:
                    point = transform.transform(point)
                except Exception as e:
                    self.show_error("Error", f"CRS transformation failed: {str(e)}")
                    return
            
            # Get field indices
            field_indices = {}
            fields = layer.fields()
            
            if settings['add_id']:
                id_field_idx = fields.indexOf('id')
                if id_field_idx == -1:
                    # Add ID field if it doesn't exist
                    layer.dataProvider().addAttributes([QgsField('id', QVariant.Int)])
                    layer.updateFields()
                    id_field_idx = layer.fields().indexOf('id')
                field_indices['id'] = id_field_idx
            
            if settings['add_coordinates']:
                x_field_idx = fields.indexOf('x')
                y_field_idx = fields.indexOf('y')
                if x_field_idx == -1 or y_field_idx == -1:
                    # Add coordinate fields if they don't exist
                    layer.dataProvider().addAttributes([
                        QgsField('x', QVariant.Double),
                        QgsField('y', QVariant.Double)
                    ])
                    layer.updateFields()
                    x_field_idx = layer.fields().indexOf('x')
                    y_field_idx = layer.fields().indexOf('y')
                field_indices['x'] = x_field_idx
                field_indices['y'] = y_field_idx
            
            if settings['add_timestamp']:
                timestamp_field_idx = fields.indexOf('created_at')
                if timestamp_field_idx == -1:
                    # Add timestamp field if it doesn't exist
                    layer.dataProvider().addAttributes([QgsField('created_at', QVariant.String)])
                    layer.updateFields()
                    timestamp_field_idx = layer.fields().indexOf('created_at')
                field_indices['timestamp'] = timestamp_field_idx
            
            # Get next ID
            next_id = 1
            if settings['add_id'] and 'id' in field_indices:
                # Find max ID
                max_id = 0
                for feature in layer.getFeatures():
                    attrs = feature.attributes()
                    if field_indices['id'] < len(attrs):
                        try:
                            feature_id = int(attrs[field_indices['id']])
                            if feature_id > max_id:
                                max_id = feature_id
                        except:
                            pass
                next_id = max_id + 1
            
            # Create feature
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPointXY(point))
            
            # Set attributes
            attributes = [None] * len(layer.fields())
            
            if settings['add_id'] and 'id' in field_indices:
                attributes[field_indices['id']] = next_id
            
            if settings['add_coordinates']:
                if 'x' in field_indices:
                    attributes[field_indices['x']] = float(point.x())
                if 'y' in field_indices:
                    attributes[field_indices['y']] = float(point.y())
            
            if settings['add_timestamp'] and 'timestamp' in field_indices:
                from datetime import datetime
                attributes[field_indices['timestamp']] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            feature.setAttributes(attributes)
            
            # Add feature to layer
            layer.startEditing()
            layer.addFeature(feature)
            layer.commitChanges()
            
        except Exception as e:
            self.show_error("Error", f"Failed to add point to layer: {str(e)}")


# REQUIRED: Create global instance for automatic discovery
create_point_at_location_action = CreatePointAtLocationAction()

