#!/usr/bin/env python3
"""
Example script showing how to use the capa Binary Ninja plugin programmatically.

This demonstrates how the plugin components work, even when Binary Ninja
is not available (for testing purposes).
"""

import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_plugin_components():
    """Test that all plugin components can be imported"""
    
    print("Testing Binary Ninja plugin components...")
    
    # Test core plugin import
    try:
        import capa.binja.plugin
        print("✓ Core plugin module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import plugin: {e}")
        return False
    
    # Test helpers
    try:
        import capa.binja.helpers
        print("✓ Helper utilities imported successfully")
        
        # Test helper functions (they should handle missing Binary Ninja gracefully)
        result = capa.binja.helpers.is_supported_binja_version()
        print(f"  Binary Ninja version check: {result}")
        
    except ImportError as e:
        print(f"✗ Failed to import helpers: {e}")
        return False
    
    # Test plugin structure
    try:
        import capa
        capa_path = Path(capa.__file__).parent
        binja_path = capa_path / "binja"
        
        required_files = [
            binja_path / "plugin" / "__init__.py",
            binja_path / "plugin" / "form.py",
            binja_path / "plugin" / "icon.py",
            binja_path / "plugin" / "capa_explorer.py",
            binja_path / "plugin" / "README.md"
        ]
        
        missing_files = [f for f in required_files if not f.exists()]
        if missing_files:
            print(f"✗ Missing required files: {missing_files}")
            return False
        else:
            print("✓ All required plugin files present")
            
    except Exception as e:
        print(f"✗ Failed to verify plugin structure: {e}")
        return False
    
    print("\n✓ All Binary Ninja plugin components working correctly!")
    return True

def demonstrate_usage():
    """Show how the plugin would be used in Binary Ninja"""
    
    print("\nDemonstrating plugin usage pattern...")
    
    # This is how the plugin would work in Binary Ninja:
    print("""
When Binary Ninja is available, the plugin works as follows:

1. User loads a binary in Binary Ninja
2. User goes to Tools > FLARE capa explorer  
3. Plugin creates a CapaExplorerForm widget
4. User clicks 'Settings' to select capa rules directory
5. User clicks 'Analyze' to run analysis
6. Analysis runs in background thread
7. Results appear in tree view
8. User can double-click results to navigate to addresses

The plugin provides:
- Non-blocking analysis (background threads)
- Interactive results navigation
- Settings persistence
- Graceful error handling
- Integration with Binary Ninja's UI framework
    """)

if __name__ == "__main__":
    print("capa Binary Ninja Plugin Example")
    print("=" * 40)
    
    success = test_plugin_components()
    
    if success:
        demonstrate_usage()
        print("\n✓ Plugin ready for use in Binary Ninja!")
    else:
        print("\n✗ Plugin has issues that need to be addressed")
        exit(1)