# Right-click Utilities and Shortcuts Hub

A revolutionary, modular QGIS Python plugin that provides **universal right-click functionality** anywhere on the canvas. Built with extensibility in mind, it features an advanced detection system that automatically identifies features of any type and shows context-aware actions.

## 🚀 Key Features

### Custom Context Menu
- **🎯 Custom Context Menu**: Hides built-in QGIS options by default for cleaner interface
- **⚙️ User Control**: Toggle "Copy Coordinates" option in General Settings if needed
- **🎨 Clean Experience**: Focus on plugin actions without QGIS clutter
- **🔄 Flexible**: Restore original QGIS behavior with simple toggle

### Universal Detection System
- **🎯 Works Anywhere**: Right-click anywhere on the canvas - no layer selection required
- **🔍 Smart Feature Detection**: Automatically detects points, lines, polygons, and their multi-part variants
- **📏 Intelligent Tolerance**: Extended search area for points and lines (10px) for easy clicking
- **📊 Multi-Feature Support**: Handles overlapping features with hierarchical menus
- **👁️ Visibility Aware**: Only works on visible features
- **⚡ Performance Optimized**: Uses spatial indexing for large datasets

### Supported Feature Types
- **📍 Point Features**: Single point geometries
- **🎯 Multipoint Features**: Multiple points in one feature
- **📏 Line Features**: Single line geometries
- **🔀 Multiline Features**: Multiple lines in one feature
- **🔷 Polygon Features**: Single polygon geometries
- **🔶 Multipolygon Features**: Multiple polygons in one feature
- **🌐 Canvas Clicks**: Actions for empty canvas areas
- **🌟 Universal Actions**: Actions that work with any feature type

### Context-Aware Action System
- **🎛️ Modular Architecture**: Each action is a separate, self-contained module
- **🏷️ Smart Filtering**: Actions only appear for supported feature types
- **📂 Tabbed Settings**: Organized by click type for easy configuration
- **🔄 Automatic Discovery**: Actions are automatically loaded from the `actions/` directory
- **💾 Persistent Settings**: User preferences saved between sessions
- **🎯 General Settings tab** to control context menu behavior

### Hierarchical Action Scoping System
- **🎯 Feature Actions**: Actions that work on individual features (e.g., "Edit Attributes", "Delete Point")
- **📊 Layer Actions**: Actions that work on entire layers (e.g., "Select All Points", "Export Layer")
- **🌐 Universal Actions**: Actions that work everywhere (e.g., "Copy Coordinates", "Zoom to Feature")
- **🔧 Automatic Validation**: Action configuration is validated on load to ensure proper scoping
- **📋 Clear Organization**: Actions are organized by scope in the context menu for better user experience

## Table of Contents

- [📋 Requirements](#-requirements)
- [💾 Installation](#-installation)
- [🎯 Usage](#-usage)
- [🏗️ Universal Detection System](#️-universal-detection-system)
- [⚙️ Architecture](#️-architecture)
- [🔧 Development](#-development)
- [📚 Documentation](#-documentation)
- [🤝 Contributing](#-contributing)
- [🐛 Troubleshooting](#-troubleshooting)
- [📄 License](#-license)

## 📋 Requirements

### System Requirements
- **QGIS**: Version 3.40 or higher (tested with QGIS 3.40 LTR)
- **Python**: Version 3.x (included with QGIS)
- **Operating System**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.15+

### Dependencies
- **PyQt5**: For GUI components (included with QGIS)
- **QGIS Core**: For spatial operations and layer management
- **QGIS GUI**: For map canvas and user interface integration

## 💾 Installation

### Method 1: Manual Installation

1. **Download the Plugin**:
   ```bash
   git clone [repository-url]
   cd RightClickUtilities
   ```

2. **Locate QGIS Plugins Directory**:
   - **Windows**: `C:\Users\[username]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`

3. **Copy Plugin Files**:
   ```bash
   cp -r RightClickUtilities [plugins-directory]/
   ```

4. **Enable the Plugin**:
   - Start QGIS
   - Go to `Plugins` → `Manage and Install Plugins...`
   - Switch to the `Installed` tab
   - Find "Right-click Utilities and Shortcuts Hub" and check the box to enable it

### Method 2: Development Installation

1. **Clone Repository**:
   ```bash
   git clone [repository-url]
   cd RightClickUtilities
   ```

2. **Install Plugin Reloader** (recommended for development):
   - Install the "Plugin Reloader" plugin from QGIS Plugin Manager
   - Use it to reload your plugin after making changes

3. **Copy to Plugins Directory**:
   ```bash
   cp -r . [plugins-directory]/RightClickUtilities
   ```

## 🎯 Usage

### Basic Usage

1. **Load Vector Layers** (Optional):
   - Add any vector layers to your QGIS project
   - **No layer selection required** - plugin works universally!

2. **Universal Right-Click**:
   - Right-click **anywhere** on the map canvas
   - **NEW**: Plugin now shows only its custom actions by default (cleaner interface!)
   - Plugin automatically detects what you clicked on:
     - 📍 On a point → Shows point actions
     - 📏 On a line → Shows line actions
     - 🔷 On a polygon → Shows polygon actions
     - 📊 On multiple features → Shows hierarchical menu
     - 🌐 On empty canvas → Shows canvas actions
     - 🌟 Universal actions appear everywhere

3. **Feature Selection Menu**:
   - When multiple features overlap, choose which one to work with
   - Features are listed alphabetically with layer information

4. **Context Menu Customization**:
   - **Default**: Built-in "Copy Coordinates" is hidden for cleaner experience
   - **Optional**: Enable "Copy Coordinates" in General Settings if needed
   - **Flexible**: Toggle between clean plugin-only menu and full QGIS menu

5. **Configure Actions**:
   - Go to `Plugins` → `Right-click Utilities` → `Configure Actions...`
   - **Tabbed interface** organized by feature type
   - Enable/disable individual actions as needed
   - Settings are automatically saved and persist between QGIS sessions

### Advanced Usage

#### Settings Configuration
- **Tabbed Interface**: Go to `Plugins` → `Right-click Utilities` → `Configure Actions...`
- **General Tab**:
  - 🎯 Show/Hide "Copy Coordinates" option in context menu
  - Control overall plugin behavior
- **Feature-Specific Tabs**:
  - 📍 Point Features
  - 🎯 Multipoint Features
  - 🔀 Multiline Features
  - 🔷 Polygon Features
  - 🌐 Canvas Clicks
  - 🌟 Universal Actions
- **Bulk Operations**: Select All, Deselect All, Reset to Defaults

#### Testing Multiple Actions
- Each feature type has 3 test actions to verify multi-action functionality
- Actions show detailed context information when executed
- Perfect for testing the detection system

#### Current Action Status
**Note**: The current actions in the `actions/` directory are **placeholder implementations** for demonstration purposes. They show the context information but do not perform actual operations. To make the plugin fully functional, you would need to:

1. **Replace placeholder actions** with real implementations
2. **Add actual functionality** to the `execute()` methods
3. **Test with real data** to ensure proper operation

The placeholder actions serve as:
- **Development templates** for creating new actions
- **Testing framework** for the universal detection system
- **Documentation examples** showing proper context handling

## 🏗️ Universal Detection System

### How It Works

The plugin features a revolutionary universal detection system that:

1. **Scans All Visible Layers**: Automatically checks all visible vector layers
2. **Applies Smart Tolerance**:
   - Points & Lines: 10-pixel search radius for easy clicking
   - Polygons: 5-pixel standard tolerance
3. **Prioritizes Features**: Points → Lines → Polygons (closest first)
4. **Handles Multi-Geometries**: Differentiates single vs multi-part features
5. **Builds Context Menus**: Shows appropriate actions based on detected features

### Detection Features

- **🎯 Universal Operation**: Works anywhere on canvas, no layer selection needed
- **📏 Smart Tolerance**: Extended search area for hard-to-click features
- **🔄 Multi-Feature Support**: Handles overlapping features gracefully
- **🏷️ Context-Aware Actions**: Actions specify which feature types they support
- **⚡ Automatic Prioritization**: Intelligent feature ordering
- **👁️ Visibility Checking**: Only detects features from visible layers

### 📋 Context Format Specification

**IMPORTANT**: All actions receive a standardized context dictionary. Here's the exact format that future actions should expect:

```python
context = {
    # Core click information (NEW UNIVERSAL FORMAT)
    'click_point': QgsPointXY,           # The clicked point coordinates
    'click_type': str,                   # Type of click: 'point', 'multipoint', 'line', 'multiline', 'polygon', 'multipolygon', 'canvas', 'mixed'
    'detected_features': List[DetectedFeature],  # All detected features at click location
    'has_features': bool,                # Whether any features were detected
    'feature_count': int,                # Number of detected features
    
    # Legacy compatibility (for backward compatibility)
    'feature': QgsFeature,               # First detected feature (if any)
    'layer': QgsVectorLayer,             # Layer of first detected feature (if any)
    'canvas': QgsMapCanvas,              # Map canvas instance
    'map_point': QgsPointXY,             # Same as click_point (legacy name)
    
    # Additional context (may be present)
    'error': str,                        # Error message if detection failed
}
```

**DetectedFeature Object Structure**:
```python
@dataclass
class DetectedFeature:
    feature: QgsFeature                  # The QGIS feature object
    layer: QgsVectorLayer               # The layer containing this feature
    geometry_type: str                  # 'point', 'multipoint', 'line', 'multiline', 'polygon', 'multipolygon'
    distance: float                     # Distance from click point (for prioritization)
```

**Action Implementation Pattern**:
```python
def execute(self, context):
    # Extract context elements
    click_point = context.get('click_point')
    click_type = context.get('click_type', 'canvas')
    detected_features = context.get('detected_features', [])
    
    # For single feature actions, get the first (closest) feature
    if detected_features:
        feature = detected_features[0].feature
        layer = detected_features[0].layer
        # Use feature and layer for your action logic
    else:
        # Canvas click - no features detected
        # Implement canvas-specific logic
```

**Click Type Values**:
- `'point'` - Single point features
- `'multipoint'` - Multipoint features  
- `'line'` - Single line features
- `'multiline'` - Multiline features
- `'polygon'` - Single polygon features
- `'multipolygon'` - Multipolygon features
- `'canvas'` - Canvas clicks (no features)
- `'mixed'` - Multiple overlapping features

**Geometry Type Values**:
- `'point'` - Point geometry
- `'multipoint'` - Multipoint geometry
- `'line'` - Line geometry
- `'multiline'` - Multiline geometry
- `'polygon'` - Polygon geometry
- `'multipolygon'` - Multipolygon geometry
- `'canvas'` - Canvas context

## ⚙️ Architecture

### Core Components

#### 1. Universal Feature Detector (`feature_detector.py`)
- **Purpose**: Smart feature detection at cursor position
- **Capabilities**:
  - Scans all visible vector layers
  - Applies geometry-specific tolerances
  - Handles multi-part geometries
  - Prioritizes detected features
  - Provides rich context information

#### 2. Context Menu Builder (`context_menu_builder.py`)
- **Purpose**: Dynamic context menu generation
- **Features**:
  - Builds hierarchical menus for multiple features
  - Filters actions by supported types
  - Handles universal actions
  - Creates user-friendly feature descriptions

#### 3. Action Registry (`action_registry.py`)
- **Purpose**: Centralized action management
- **Responsibilities**:
  - Loads actions from modular system
  - Manages enable/disable state
  - Provides settings persistence
  - Organizes actions by category

#### 4. Settings Dialog (`settings_dialog.py`)
- **Purpose**: Tabbed user interface for configuration
- **Features**:
  - Organizes actions by click type
  - Provides bulk operations
  - Filters actions appropriately
  - Saves settings persistently

#### 5. Modular Action System (`actions/` directory)
- **Purpose**: Individual action implementations
- **Components**:
  - `base_action.py`: Base class with common functionality
  - `action_loader.py`: Automatic action discovery
  - Individual action files: One per action
  - Placeholder and test actions

### Data Flow

1. **User Right-Click** → Feature Detector analyzes cursor position
2. **Feature Detection** → Identifies all features at click location
3. **Context Building** → Creates rich context object with feature information
4. **Menu Generation** → Context Menu Builder creates appropriate menu
5. **Action Filtering** → Only shows actions that support detected feature types
6. **Action Execution** → Selected action executes with full context
7. **User Feedback** → Action provides appropriate response/feedback

## 🔧 Development

### File Structure

```
RightClickUtilities/
├── __init__.py                    # Plugin entry point
├── right_click_utilities.py      # Main plugin class with universal detection
├── feature_detector.py           # Universal feature detection system
├── context_menu_builder.py       # Dynamic menu generation
├── action_registry.py            # Action management system
├── settings_dialog.py            # Tabbed settings interface
├── actions/                      # Modular action system
│   ├── __init__.py              # Actions package
│   ├── base_action.py           # Base class with context-aware support
│   ├── action_loader.py         # Automatic action discovery
│   ├── *_placeholder.py        # Core placeholder actions (6 files)
│   ├── *_action_*.py           # Test actions (24 files)
│   └── README.md                # Comprehensive action development guide
├── metadata.txt                   # Plugin metadata
├── resources.qrc                  # Resource definitions
├── resources.py                   # Generated resource file
├── icons/                        # Plugin icons
├── ui/                           # UI files directory
├── README.md                     # This comprehensive guide
├── INSTALLATION.md               # Detailed installation instructions
├── DEVELOPER_GUIDE.md            # Complete developer documentation
└── API_REFERENCE.md              # Full API documentation
```

### Action Scoping System

The plugin uses a hierarchical action scoping system that organizes actions into three distinct categories:

#### 🎯 Feature Actions
Actions that work on **individual features**:
- **Scope**: `'feature'`
- **Examples**: Edit Attributes, Delete Point, Move Feature, Calculate Area
- **Context**: Access to the specific clicked feature
- **Menu Position**: Top of context menu

#### 📊 Layer Actions  
Actions that work on **entire layers**:
- **Scope**: `'layer'`
- **Examples**: Select All Points, Export Layer, Layer Properties, Simplify Lines
- **Context**: Access to the layer containing the clicked feature
- **Menu Position**: Middle of context menu (after feature actions)

#### 🌐 Universal Actions
Actions that work **everywhere**:
- **Scope**: `'universal'`
- **Examples**: Copy Coordinates, Zoom to Feature, Show Information
- **Context**: Access to click location and all detected features
- **Menu Position**: Bottom of context menu (always visible)

### Creating Custom Actions

The plugin uses a modular action system where each action is a separate Python file in the `actions/` directory. Here's how to create a custom action:

#### Step 1: Create Action File
Create a new Python file in `RightClickUtilities/actions/` with a descriptive name:

```python
# actions/my_feature_action.py
"""
My Feature Action for Right-click Utilities and Shortcuts Hub

This action demonstrates how to create a feature-scoped action that works
on individual features using the universal detection system.
"""

from .base_action import BaseAction

class MyFeatureAction(BaseAction):
    """
    Example feature action that works on individual features.
    
    This action demonstrates the feature scope and shows how to access
    the clicked feature and its properties.
    """
    
    def __init__(self):
        super().__init__()
        # Required properties
        self.action_id = "my_feature_action"
        self.name = "My Feature Action"
        self.category = "My Category"
        self.description = "Description of what this action does"
        self.enabled = True
        
        # Action scoping configuration
        self.set_action_scope('feature')  # This is a feature action
        self.set_supported_scopes(['feature'])  # Only supports feature scope
        
        # Feature type support
        self.set_supported_click_types(['point', 'line', 'polygon'])
        self.set_supported_geometry_types(['point', 'line', 'polygon'])
    
    def execute(self, context):
        """
        Execute the action.
        
        Args:
            context (dict): Context containing:
                - click_point (QgsPointXY): The clicked point coordinates
                - click_type (str): Type of click ('point', 'line', 'polygon', 'canvas', etc.)
                - detected_features (List[DetectedFeature]): All detected features
                - has_features (bool): Whether any features were detected
                - feature_count (int): Number of detected features
                - feature (QgsFeature): First detected feature (legacy compatibility)
                - layer (QgsVectorLayer): Layer of first detected feature (legacy compatibility)
                - canvas (QgsMapCanvas): The map canvas
        """
        # Extract context elements using NEW UNIVERSAL FORMAT
        click_point = context.get('click_point')
        click_type = context.get('click_type', 'canvas')
        detected_features = context.get('detected_features', [])
        
        if not detected_features:
            self.show_error("Error", "No features found at this location")
            return
        
        # Get the first (closest) detected feature
        detected_feature = detected_features[0]
        feature = detected_feature.feature
        layer = detected_feature.layer
        geometry_type = detected_feature.geometry_type
        distance = detected_feature.distance
        
        try:
            # Your action logic here
            feature_id = feature.id()
            layer_name = layer.name()
            
            # Example: Show feature information
            self.show_info("Feature Action", 
                f"Action executed on {geometry_type} feature ID: {feature_id}\n"
                f"Layer: {layer_name}\n"
                f"Click point: ({click_point.x():.2f}, {click_point.y():.2f})\n"
                f"Distance: {distance:.2f} map units\n"
                f"Click type: {click_type}")
            
        except Exception as e:
            self.show_error("Error", f"Failed to execute action: {str(e)}")

# Create global instance for automatic discovery
my_feature_action = MyFeatureAction()
```

#### Step 2: Action Scoping Configuration

Each action must specify its scope using these methods:

```python
# For feature actions
self.set_action_scope('feature')
self.set_supported_scopes(['feature'])

# For layer actions  
self.set_action_scope('layer')
self.set_supported_scopes(['layer'])

# For universal actions
self.set_action_scope('universal')
self.set_supported_scopes(['universal'])
```

#### Step 3: Feature Type Support

Specify which feature types your action supports:

```python
# Support specific feature types
self.set_supported_click_types(['point', 'line', 'polygon'])
self.set_supported_geometry_types(['point', 'line', 'polygon'])

# Support all feature types (for universal actions)
self.set_supported_click_types(['universal'])
self.set_supported_geometry_types(['point', 'line', 'polygon', 'canvas'])
```

#### Step 4: Action Categories

Use these standard categories for organizing actions:

- **Editing**: Actions that modify features (delete, edit attributes, etc.)
- **Analysis**: Actions that analyze features (area, perimeter, statistics, etc.)
- **Navigation**: Actions that change the map view (zoom, pan, etc.)
- **Export**: Actions that export or save data
- **Information**: Actions that display information about features
- **Selection**: Actions that modify feature selection
- **Geometry**: Actions that modify feature geometry

### Action Context

The `context` parameter in `execute()` contains rich information. **Use the NEW UNIVERSAL FORMAT** for future actions:

**Important**: When multiple features overlap, the context menu system creates a feature-specific context for each selected feature, ensuring actions work on the exact feature you selected from the menu.

```python
def execute(self, context):
    # NEW UNIVERSAL FORMAT (recommended for new actions)
    click_point = context.get('click_point')           # QgsPointXY - The clicked point coordinates
    click_type = context.get('click_type', 'canvas')   # str - Type of click ('point', 'line', 'polygon', 'canvas', etc.)
    detected_features = context.get('detected_features', [])  # List[DetectedFeature] - All detected features
    has_features = context.get('has_features', False)         # bool - Whether any features were detected
    feature_count = context.get('feature_count', 0)           # int - Number of detected features
    
    # For single feature actions, get the first (and only) feature
    # Note: When multiple features overlap, detected_features contains only the selected feature
    if detected_features:
        feature = detected_features[0].feature         # QgsFeature - The clicked feature
        layer = detected_features[0].layer             # QgsVectorLayer - The layer containing the feature
        geometry_type = detected_features[0].geometry_type  # str - Geometry type
        distance = detected_features[0].distance       # float - Distance from click point
    else:
        # Canvas click - no features detected
        feature = None
        layer = None
    
    # Legacy compatibility (still available)
    canvas = context.get('canvas')                     # QgsMapCanvas - The map canvas
    map_point = context.get('map_point')               # QgsPointXY - Same as click_point (legacy)
```

### BaseAction Methods

The `BaseAction` class provides utility methods for common operations:

#### Dialog Methods
```python
self.show_info(title, message)        # Show information dialog
self.show_error(title, message)       # Show error dialog  
self.show_warning(title, message)     # Show warning dialog
self.confirm_action(title, message)   # Show confirmation dialog (returns bool)
```

#### Edit Mode Management
```python
# Handle edit mode for operations that modify data
edit_result = self.handle_edit_mode(layer, "operation name")
if edit_result[0] is None:  # Error occurred
    return

was_in_edit_mode, edit_mode_entered = edit_result

try:
    # Your operation here
    success = layer.addFeature(feature)
    
    # Commit changes
    if not self.commit_changes(layer, "operation name"):
        return
        
except Exception as e:
    self.rollback_changes(layer)
finally:
    self.exit_edit_mode(layer, edit_mode_entered)
```

### Action Validation

The system automatically validates action configuration on load:

- **Required Properties**: `action_id`, `name` must be specified
- **Valid Scopes**: Only `'feature'`, `'layer'`, `'universal'` are allowed
- **Scope Consistency**: `action_scope` must be in `supported_scopes`
- **Feature Type Support**: At least one click type and geometry type must be specified

Invalid actions are skipped with a warning message.

### Key Features for Developers

- **🔄 Automatic Discovery**: Just create a file, no registration needed
- **🏷️ Context-Aware**: Actions specify exactly what they support
- **🧑‍🔬 Rich Context**: Access to click location, features, layers, and more
- **🎯 Smart Filtering**: Actions only appear when appropriate
- **🔧 Easy Testing**: Built-in test actions and comprehensive examples
- **📚 Extensive Documentation**: Complete guides and API reference
- **✅ Automatic Validation**: Action configuration is validated on load
- **🎯 Hierarchical Scoping**: Clear organization by feature/layer/universal scope

## 📚 Documentation

### Complete Documentation Suite
- **📚 README.md**: This comprehensive overview (you're reading it!)
- **🔧 INSTALLATION.md**: Detailed installation instructions and troubleshooting
- **👨‍💻 DEVELOPER_GUIDE.md**: Complete developer documentation with examples
- **📋 API_REFERENCE.md**: Full API documentation for all classes and methods
- **🎯 actions/README.md**: Detailed guide for action development

### Key Documentation Features
- **Step-by-step guides** for all common tasks
- **Complete API reference** with examples
- **Troubleshooting guides** for common issues
- **Performance optimization** tips and techniques
- **Best practices** for development and extension

## 🤝 Contributing

### Development Setup

1. **Fork the Repository**
2. **Create Feature Branch**:
   ```bash
   git checkout -b feature/my-awesome-feature
   ```
3. **Install Development Tools**:
   - Plugin Reloader for QGIS
   - Python linter (flake8, pylint)
   - Code formatter (black)

### Contribution Guidelines

- **🐍 Python Style**: Follow PEP 8 guidelines
- **📝 Documentation**: Update docs for any new features
- **🧑‍🔬 Testing**: Test with various feature types and edge cases
- **🔍 Code Review**: All changes go through review process
- **📋 Issue Tracking**: Use GitHub issues for bugs and features

### Adding New Features

The modular architecture makes adding new features incredibly easy:

- **New Actions**: Just create a new action file
- **New Feature Types**: Extend the detection system
- **New UI Components**: Add to the settings dialog
- **New Capabilities**: Extend the base action class

## 🐛 Troubleshooting

### Common Issues

#### Plugin Not Loading
- **Check file permissions**: Ensure QGIS can read plugin files
- **Verify directory structure**: All required files must be present
- **Check Python console**: Look for error messages
- **Restart QGIS**: Sometimes required after installation

#### Universal Detection Not Working
- **Check layer visibility**: Only visible layers are detected
- **Verify click location**: Try clicking directly on features
- **Check tolerance settings**: Points/lines have extended search area
- **Test with different layers**: Try various geometry types

#### Actions Not Appearing
- **Check action settings**: Ensure actions are enabled in settings dialog
- **Verify action support**: Actions only appear for supported feature types
- **Check action discovery**: Look for errors in Python console
- **Test action loading**: Use the action registry to verify loading

#### Performance Issues
- **Large datasets**: Plugin automatically optimizes for large layers
- **Complex geometries**: Very complex features may cause delays
- **Memory usage**: Monitor QGIS memory with large datasets

### Debug Information

Enable debug output by checking the QGIS Python console:
1. Go to `View` → `Panels` → `Python Console`
2. Look for plugin debug messages
3. Check for errors or warnings
4. Use debug output to trace execution

### Getting Help

1. **📚 Check Documentation**: Review all documentation files
2. **🔍 Search Issues**: Look through existing GitHub issues
3. **🆕 Create Issue**: Report bugs with detailed information
4. **💬 Community Support**: Join QGIS community discussions

## 📄 License

[Add your license information here]

## 🎉 Conclusion

The Right-click Utilities and Shortcuts Hub represents a revolutionary approach to QGIS plugins, featuring:

- **🌟 Universal Detection**: Works anywhere on the canvas with any feature type
- **🎯 Context-Aware Actions**: Smart filtering based on what you clicked
- **🔧 Modular Architecture**: Incredibly easy to extend and customize
- **📚 Comprehensive Documentation**: Everything you need to get started and contribute

Whether you're a user looking for powerful right-click functionality or a developer wanting to extend QGIS capabilities, this plugin provides a solid foundation for spatial data interaction.

**Ready to get started?** Check out the [Installation Guide](INSTALLATION.md) and start exploring the universal detection system!

---

**🚀 Version 0.5.0** - Universal Detection System with Context-Aware Actions