#!/usr/bin/env python
"""Test script to debug mathematical handwriting assessment API"""

import requests
import io
from PIL import Image, ImageDraw, ImageFont

def create_test_math_image():
    """Create a test image with mathematical expressions"""
    # Create a blank white image
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw mathematical expressions from the screenshot (Rahul Kumar example)
    expressions = [
        "53 - 27 = 34",  # Place value error, should be 26
        "45 + 28 = 73",  # Correct
        "82 - 37 = 55"   # Place value error, should be 45
    ]
    
    y_pos = 50
    for expr in expressions:
        draw.text((50, y_pos), expr, fill='black')
        y_pos += 100
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

def test_math_api():
    """Test the mathematical assessment API"""
    try:
        # Test both examples from the screenshot
        test_cases = [
            {
                'name': 'Rahul Kumar',
                'expressions': [
                    "53 - 27 = 34",  # Place value error, should be 26
                    "45 + 28 = 73",  # Correct
                    "82 - 37 = 55"   # Place value error, should be 45
                ],
                'expected_error': 'Place Value Error: Confusion'
            },
            {
                'name': 'Priya Singh',
                'expressions': [
                    "12 x 3 = 36",  # Correct
                    "15 + 8 = 7",   # Operation confusion, should be 23
                    "24 / 6 = 4"    # Correct
                ],
                'expected_error': 'Operation: Confusion'
            }
        ]
        
        for test_case in test_cases:
            print(f"\n{'='*50}")
            print(f"Testing: {test_case['name']}")
            print(f"{'='*50}")
            
            # Create test image
            image_data = create_test_math_image()
            
            # Create a file-like object
            image_file = io.BytesIO(image_data.getvalue())
            image_file.name = 'test_math.jpg'
            
            # Test the API
            response = requests.post(
                'http://127.0.0.1:5000/api/math/analyze',
                files={'image': image_file},
                data={'student_name': test_case['name']}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("API call successful")
                data = response.json()
                if data.get('success'):
                    print("Mathematical analysis successful")
                    print(f"Student: {data.get('student_name')}")
                    print(f"Problems analyzed: {data.get('problems_analyzed')}")
                    print(f"Correct answers: {data.get('correct_answers')}")
                    print(f"Accuracy: {data.get('accuracy_percentage')}%")
                    print(f"Primary error: {data.get('primary_error')}")
                    print(f"Expected error: {test_case['expected_error']}")
                    print(f"AI Insight: {data.get('ai_insight')}")
                else:
                    print(f"Mathematical analysis failed: {data.get('error')}")
            else:
                print(f"API call failed with status {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_math_api()