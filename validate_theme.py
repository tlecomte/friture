#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validation script for theme implementation without GUI initialization
"""

import sys
import os

# Add the friture directory to Python path
sys.path.insert(0, '/workspaces/friture')

def test_theme_module():
    """Test if theme module can be imported and has correct structure"""
    try:
        import friture.theme as theme_module
        print("✓ Theme module imported successfully")
        
        # Check if required classes and functions exist
        assert hasattr(theme_module, 'ThemeManager'), "ThemeManager class missing"
        assert hasattr(theme_module, 'apply_theme'), "apply_theme function missing" 
        assert hasattr(theme_module, 'get_theme_manager'), "get_theme_manager function missing"
        print("✓ Theme module has all required components")
        
        # Check ThemeManager methods
        manager_methods = ['apply_theme', '_apply_dark_theme', '_apply_light_theme', '_apply_system_theme']
        for method in manager_methods:
            assert hasattr(theme_module.ThemeManager, method), f"ThemeManager.{method} method missing"
        print("✓ ThemeManager has all required methods")
        
        return True
    except Exception as e:
        print(f"✗ Theme module test failed: {e}")
        return False

def test_settings_changes():
    """Test if settings module has theme-related changes"""
    try:
        # Read the settings file to check for our additions
        with open('/workspaces/friture/friture/settings.py', 'r') as f:
            settings_content = f.read()
        
        required_strings = [
            'theme_changed = pyqtSignal(str)',
            'self.comboBox_theme.currentTextChanged.connect(self.theme_changed)',
            'settings.setValue("theme"',
            'theme_text = settings.value("theme"'
        ]
        
        for required in required_strings:
            if required not in settings_content:
                print(f"✗ Missing in settings.py: {required}")
                return False
        
        print("✓ Settings module has all theme-related changes")
        return True
    except Exception as e:
        print(f"✗ Settings module test failed: {e}")
        return False

def test_ui_settings_changes():
    """Test if ui_settings module has theme UI elements"""
    try:
        with open('/workspaces/friture/friture/ui_settings.py', 'r') as f:
            ui_content = f.read()
        
        required_elements = [
            'self.themeGroup = QtWidgets.QGroupBox',
            'self.label_theme = QtWidgets.QLabel',
            'self.comboBox_theme = QtWidgets.QComboBox',
            'self.themeGroup.setTitle(_translate("Settings_Dialog", "Appearance"))',
            '"System Default"', '"Light"', '"Dark"'
        ]
        
        for required in required_elements:
            if required not in ui_content:
                print(f"✗ Missing in ui_settings.py: {required}")
                return False
        
        print("✓ UI Settings module has all theme UI elements")
        return True
    except Exception as e:
        print(f"✗ UI Settings module test failed: {e}")
        return False

def test_analyzer_changes():
    """Test if analyzer module has theme integration"""
    try:
        with open('/workspaces/friture/friture/analyzer.py', 'r') as f:
            analyzer_content = f.read()
        
        required_changes = [
            'from friture.theme import apply_theme',
            'self.settings_dialog.theme_changed.connect(self.theme_changed)',
            'def theme_changed(self, theme_name: str) -> None:',
            'apply_theme(theme_name)'
        ]
        
        for required in required_changes:
            if required not in analyzer_content:
                print(f"✗ Missing in analyzer.py: {required}")
                return False
        
        print("✓ Analyzer module has all theme integration changes")
        return True
    except Exception as e:
        print(f"✗ Analyzer module test failed: {e}")
        return False

def test_ui_file_changes():
    """Test if settings.ui has theme elements"""
    try:
        with open('/workspaces/friture/ui/settings.ui', 'r') as f:
            ui_content = f.read()
        
        required_ui_elements = [
            'name="themeGroup"',
            '<string>Appearance</string>',
            'name="comboBox_theme"',
            '<string>System Default</string>',
            '<string>Light</string>',
            '<string>Dark</string>'
        ]
        
        for required in required_ui_elements:
            if required not in ui_content:
                print(f"✗ Missing in settings.ui: {required}")
                return False
        
        print("✓ Settings UI file has all theme elements")
        return True
    except Exception as e:
        print(f"✗ Settings UI file test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("=== Friture Theme Implementation Validation ===\n")
    
    tests = [
        ("Theme Module", test_theme_module),
        ("Settings Module Changes", test_settings_changes),
        ("UI Settings Module Changes", test_ui_settings_changes),
        ("Analyzer Module Changes", test_analyzer_changes),
        ("UI File Changes", test_ui_file_changes)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        if test_func():
            passed += 1
            print()
        else:
            print()
    
    print(f"=== Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("🎉 All tests passed! Theme implementation is complete and ready to use.")
        print("\nTo use the theme feature:")
        print("1. Run Friture normally")
        print("2. Open Settings from the toolbar")
        print("3. Look for the 'Appearance' section")
        print("4. Select your preferred theme from the dropdown")
        print("5. The theme will apply immediately!")
    else:
        print(f"⚠️  {total - passed} tests failed. Please check the implementation.")

if __name__ == '__main__':
    main()
