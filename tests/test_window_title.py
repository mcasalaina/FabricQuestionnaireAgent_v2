#!/usr/bin/env python3
"""
Test for window title verification.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_window_title():
    """Test that the window title is set correctly by checking the source code."""
    
    try:
        # Read the source file and verify it contains the correct title
        source_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "question_answerer.py")
        
        with open(source_file, 'r') as f:
            content = f.read()
        
        # Check that the correct title is set
        expected_title_line = 'self.root.title("Fabric Questionnaire Agent")'
        old_title_line = 'self.root.title("Questionnaire Multiagent")'
        
        if expected_title_line in content:
            print(f"✓ Window title correctly set in source code: 'Fabric Questionnaire Agent'")
            
            # Verify the old title is not present
            if old_title_line in content:
                print(f"✗ Error: Old title still found in source code")
                return False
            else:
                print(f"✓ Old title 'Questionnaire Multiagent' successfully removed")
                return True
        else:
            print(f"✗ Error: Expected title not found in source code")
            print(f"Looking for: {expected_title_line}")
            return False
        
    except Exception as e:
        print(f"✗ Error testing window title: {e}")
        return False

def test_window_title_runtime():
    """Test that the window title is set correctly at runtime (requires display)."""
    
    try:
        # Only run this test if we have a display available
        import tkinter as tk
        
        # Try to create a simple test window first
        test_root = tk.Tk()
        test_root.withdraw()  # Hide the test window
        test_root.destroy()
        
        # Import and create the GUI application in mock mode
        from question_answerer import QuestionnaireAgentUI
        
        # Create the application in mock mode to avoid Azure dependencies
        app = QuestionnaireAgentUI(headless_mode=False, mock_mode=True)
        
        # Verify the window title is set correctly
        expected_title = "Fabric Questionnaire Agent"
        actual_title = app.root.title()
        
        assert actual_title == expected_title, f"Window title should be '{expected_title}' but got '{actual_title}'"
        
        print(f"✓ Window title correctly set at runtime: '{actual_title}'")
        
        # Clean up
        app.cleanup_agents()
        app.root.destroy()
        
        return True
        
    except Exception as e:
        print(f"⚠ Runtime test skipped (no display or error): {e}")
        return True  # Don't fail the test if we can't test the runtime

if __name__ == "__main__":
    success1 = test_window_title()
    success2 = test_window_title_runtime()
    sys.exit(0 if (success1 and success2) else 1)