#!/usr/bin/env python3
"""
Test Installation Script for ComfyUI Random LoRA Chooser
Run this script to verify that the nodes are properly installed and functional
"""

import sys
import os

def test_imports():
    """Test if the nodes can be imported properly"""
    print("🧪 Testing imports...")
    
    try:
        from nodes.random_lora_chooser import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
        print("✅ Successfully imported node classes")
        
        # Check if nodes are properly defined
        expected_nodes = ["DynamicRandomLoraChooser", "SimpleRandomLoraChooser"]
        for node_name in expected_nodes:
            if node_name in NODE_CLASS_MAPPINGS:
                print(f"✅ Found node: {node_name}")
            else:
                print(f"❌ Missing node: {node_name}")
                return False
                
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_node_structure():
    """Test if nodes have proper structure"""
    print("\n🧪 Testing node structure...")
    
    try:
        from nodes.random_lora_chooser import DynamicRandomLoraChooser, SimpleRandomLoraChooser
        
        # Test DynamicRandomLoraChooser
        node = DynamicRandomLoraChooser()
        input_types = node.INPUT_TYPES()
        
        required_keys = ["required", "optional"]
        for key in required_keys:
            if key in input_types:
                print(f"✅ DynamicRandomLoraChooser has {key} inputs")
            else:
                print(f"❌ DynamicRandomLoraChooser missing {key} inputs")
                return False
        
        # Check for num_loras parameter
        if "num_loras" in input_types["required"]:
            print("✅ DynamicRandomLoraChooser has num_loras parameter")
        else:
            print("❌ DynamicRandomLoraChooser missing num_loras parameter")
            return False
            
        # Test SimpleRandomLoraChooser
        simple_node = SimpleRandomLoraChooser()
        simple_input_types = simple_node.INPUT_TYPES()
        
        if "num_loras" in simple_input_types["required"]:
            print("✅ SimpleRandomLoraChooser has num_loras parameter")
        else:
            print("❌ SimpleRandomLoraChooser missing num_loras parameter")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Structure test error: {e}")
        return False

def test_javascript_files():
    """Test if JavaScript files exist"""
    print("\n🧪 Testing JavaScript files...")
    
    js_file = "web/js/dynamic_lora_chooser.js"
    if os.path.exists(js_file):
        print(f"✅ Found JavaScript file: {js_file}")
        
        # Check if the file contains key functionality
        try:
            with open(js_file, 'r') as f:
                content = f.read()
                
            key_features = [
                "app.registerExtension",
                "DynamicRandomLoraChooser",
                "SimpleRandomLoraChooser",
                "updateNodeInputsVisibility"
            ]
            
            for feature in key_features:
                if feature in content:
                    print(f"✅ JavaScript contains: {feature}")
                else:
                    print(f"❌ JavaScript missing: {feature}")
                    return False
                    
            return True
        except Exception as e:
            print(f"❌ Error reading JavaScript file: {e}")
            return False
    else:
        print(f"❌ Missing JavaScript file: {js_file}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\n🧪 Testing file structure...")
    
    required_files = [
        "__init__.py",
        "nodes/random_lora_chooser.py",
        "web/js/dynamic_lora_chooser.js",
        "README.md"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_exist = False
            
    return all_exist

def main():
    """Run all tests"""
    print("🎯 ComfyUI Random LoRA Chooser - Installation Test")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Node Imports", test_imports),
        ("Node Structure", test_node_structure),
        ("JavaScript Files", test_javascript_files)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        print()  # Add spacing between tests
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Installation appears to be correct.")
        print("💡 Restart ComfyUI and look for the nodes under 'loaders/lora' category")
        return True
    else:
        print("❌ Some tests failed. Please check the installation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)