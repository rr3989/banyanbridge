"""Test script for mathematical expression detection with user's image"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from real_math_analysis import RealMathAnalyzer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_math_detection():
    """Test mathematical expression detection"""
    # Use a local test image - user should provide their image
    test_image = "test_math.png"
    
    if not os.path.exists(test_image):
        logger.error(f"Test image not found: {test_image}")
        logger.info("Please place your test image with handwritten math as 'test_math.png' in the project directory")
        logger.info("Expected expressions like: 44 - 16 = 32, 2 + 3 = 5, 12 + 15 = 22")
        return
    
    logger.info(f"Testing with image: {test_image}")
    
    analyzer = RealMathAnalyzer()
    
    # Test expression detection
    logger.info("Testing mathematical expression detection...")
    expressions = analyzer.detect_mathematical_expressions(test_image)
    logger.info(f"Detected {len(expressions)} mathematical regions")
    
    # Test text extraction from full image
    logger.info("Testing text extraction from full image...")
    from real_handwriting_analysis import RealHandwritingAnalyzer
    handwriting_analyzer = RealHandwritingAnalyzer()
    ocr_result = handwriting_analyzer.extract_text(test_image)
    logger.info(f"OCR Result: {ocr_result}")
    
    # Test expression parsing
    if ocr_result.get('success'):
        logger.info(f"Extracted text: {ocr_result['text']}")
        logger.info("Testing expression parsing...")
        
        # Try parsing from full text
        lines = ocr_result['text'].split('\n')
        for line in lines:
            if line.strip():
                parsed = analyzer.parse_mathematical_expression(line)
                if parsed:
                    logger.info(f"Parsed expression: {parsed}")
                else:
                    logger.info(f"Could not parse: {line}")
    
    # Test with detected regions
    for i, expr in enumerate(expressions):
        logger.info(f"\nTesting region {i+1}:")
        text_result = analyzer.extract_mathematical_text(expr['cropped_image'])
        logger.info(f"Text result: {text_result}")
        
        if text_result.get('success'):
            parsed = analyzer.parse_mathematical_expression(text_result['text'])
            logger.info(f"Parsed: {parsed}")

if __name__ == "__main__":
    test_math_detection()
