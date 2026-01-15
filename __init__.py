"""
Right-click Utilities and Shortcuts Hub - QGIS Plugin

This plugin provides a context menu when right-clicking on polygon features
in the active layer. It's designed to be lightweight and extensible for
future functionality additions.

Author: Your Name
Version: 1.0.0
QGIS Minimum Version: 3.40
"""

def classFactory(iface):
    """
    Factory function that QGIS calls to instantiate the plugin.
    
    Args:
        iface: QGIS interface instance
        
    Returns:
        RightClickUtilities: Plugin instance
    """
    from .right_click_utilities import RightClickUtilities
    return RightClickUtilities(iface)
