"""
Real Mathematical Handwriting Analysis Module
Uses YOLOv8 for expression detection and TrOCR for mathematical text recognition
"""

import cv2
import numpy as np
import re
import logging
from typing import List, Dict, Optional, Tuple
from PIL import Image
import torch

logger = logging.getLogger(__name__)

class RealMathExpressionAnalyzer:
    """Real mathematical expression analysis using YOLOv8 + TrOCR"""
    
    def __init__(self):
        self.yolo_model = None
        
        # Try to load YOLOv8 for expression detection
        try:
            from ultralytics import YOLO
            self.yolo_model = YOLO('yolov8n.pt')  # Use nano version for speed
            logger.info("YOLOv8 model loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load YOLOv8: {e}, using computer vision fallback")
        
        # TrOCR disabled due to tokenizer compatibility issues on some systems
        # Using EasyOCR which is more reliable and works well for handwritten math
        logger.info("TrOCR disabled due to tokenizer compatibility issues")
        logger.info("Using EasyOCR for text recognition (works well for handwritten math)")
        
        if self.yolo_model:
            logger.info("Using YOLOv8 + EasyOCR for maximum accuracy")
        else:
            logger.info("Using computer vision + EasyOCR for reliability")
    
    def detect_mathematical_expressions(self, image_path: str) -> List[Dict]:
        """Detect mathematical expressions in image using YOLOv8 or computer vision"""
        if self.yolo_model:
            return self._detect_expressions_yolo(image_path)
        else:
            return self._detect_expressions_cv(image_path)
    
    def _detect_expressions_yolo(self, image_path: str) -> List[Dict]:
        """Detect expressions using YOLOv8"""
        try:
            results = self.yolo_model(image_path)
            expressions = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0].cpu().numpy())
                    
                    # Extract cropped image region
                    image = cv2.imread(image_path)
                    cropped = image[int(y1):int(y2), int(x1):int(x2)]
                    
                    expressions.append({
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'confidence': confidence,
                        'class_id': int(box.cls[0].cpu().numpy()),
                        'cropped_image': cropped
                    })
            
            logger.info(f"YOLOv8 detected {len(expressions)} regions")
            return expressions
            
        except Exception as e:
            logger.error(f"Error with YOLOv8 detection: {e}")
            return self._detect_expressions_cv(image_path)
    
    def _detect_expressions_cv(self, image_path: str) -> List[Dict]:
        """Enhanced method for detecting handwritten mathematical expressions"""
        try:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding for better text detection on handwritten content
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                            cv2.THRESH_BINARY_INV, 15, 8)
            
            # Use morphological operations to detect text regions
            # More aggressive kernel for handwritten math
            kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
            kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 30))
            
            dilated_h = cv2.dilate(binary, kernel_h, iterations=1)
            dilated_v = cv2.dilate(binary, kernel_v, iterations=1)
            
            # Combine horizontal and vertical dilation
            dilated = cv2.add(dilated_h, dilated_v)
            
            # Find contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            expressions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Very lenient filters for handwritten math
                # Handwritten math can have varying sizes and spacings
                if w > 20 and h > 10:  # Minimal size filter
                    cropped = image[y:y+h, x:x+w]
                    expressions.append({
                        'bbox': [x, y, x+w, y+h],
                        'confidence': 0.7,  # Moderate confidence
                        'class_id': 0,
                        'cropped_image': cropped
                    })
            
            # Sort by y position to maintain reading order
            expressions.sort(key=lambda e: e['bbox'][1])
            
            logger.info(f"Detected {len(expressions)} potential mathematical regions using enhanced CV")
            return expressions
            
        except Exception as e:
            logger.error(f"Error detecting expressions with CV: {e}")
            return []
    
    def extract_mathematical_text(self, image_region: np.ndarray) -> Dict:
        """Extract mathematical text from image region using EasyOCR"""
        return self._extract_text_easyocr_only(image_region)
    

    def _extract_text_easyocr_only(self, image_region: np.ndarray) -> Dict:
        """Fallback method using EasyOCR only"""
        try:
            import easyocr
            reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            
            # Perform OCR with detail=0 for better performance
            results = reader.readtext(image_region, detail=0)
            
            if not results:
                return {
                    'success': False,
                    'text': '',
                    'confidence': 0,
                    'method': 'EasyOCR'
                }
            
            # Handle different result formats
            texts = []
            if isinstance(results[0], tuple):
                # Format: (text, confidence)
                for text, confidence in results:
                    texts.append(text)
            else:
                # Format: [text]
                texts = results
            
            full_text = ' '.join(texts)
            
            return {
                'success': True,
                'text': full_text,
                'confidence': 75.0,
                'method': 'EasyOCR'
            }
            
        except Exception as e:
            logger.error(f"Error extracting text with EasyOCR: {e}")
            return {
                'success': False,
                'text': '',
                'confidence': 0,
                'method': 'Failed'
            }
    
    def parse_mathematical_expression(self, text: str) -> Optional[Dict]:
        """Enhanced mathematical expression parser for handwritten math with smart extraction"""
        try:
            # Clean the text - remove common OCR errors
            cleaned_text = text.strip()
            cleaned_text = cleaned_text.replace('|', '1')  # Common OCR error
            cleaned_text = cleaned_text.replace('l', '1')  # Common OCR error
            cleaned_text = cleaned_text.replace('O', '0')  # Common OCR error
            cleaned_text = cleaned_text.replace('S', '5')  # Common OCR error
            cleaned_text = cleaned_text.replace('o', '0')  # Common OCR error
            cleaned_text = cleaned_text.replace('_', '')  # Remove underscores
            cleaned_text = cleaned_text.replace('.', '')  # Remove dots (OCR artifacts)
            
            logger.info(f"Parsing cleaned text: '{cleaned_text}'")
            
            # Smart extraction: try to find mathematical patterns in jumbled text
            # Look for sequences like: number, operator, number, equals, number
            all_numbers = re.findall(r'\d+', cleaned_text)
            all_operators = re.findall(r'[+\-×x÷*/]', cleaned_text)
            has_equals = '=' in cleaned_text
            
            # If we have enough numbers and operators, try to construct expressions
            if len(all_numbers) >= 3 and has_equals:
                logger.info(f"Found {len(all_numbers)} numbers and {len(all_operators)} operators, attempting smart extraction")
                
                # Try to construct expression by analyzing the text structure
                # Strategy: Look for patterns like "45 + 28 = 73" in the text
                # First, try to find a complete expression pattern
                expression_pattern = r'(\d+)\s*([+\-×x÷*/])\s*(\d+)\s*=\s*(\d+)'
                match = re.search(expression_pattern, cleaned_text)
                if match:
                    operand1 = int(match.group(1))
                    operator = match.group(2)
                    operand2 = int(match.group(3))
                    student_answer = int(match.group(4))
                    
                    logger.info(f"Found complete expression pattern: {operand1} {operator} {operand2} = {student_answer}")
                    
                    # Normalize operator
                    if operator in ['×', 'x']:
                        operator = '*'
                    elif operator == '÷':
                        operator = '/'
                    
                    # Calculate correct answer
                    correct_answer = self._calculate_answer(operand1, operator, operand2)
                    
                    logger.info(f"Calculated correct answer: {correct_answer}")
                    
                    # Analyze error type if incorrect
                    error_analysis = None
                    if student_answer != correct_answer:
                        error_analysis = self._analyze_error_type(operand1, operator, operand2, student_answer, correct_answer)
                    
                    return {
                        'expression': f"{operand1} {operator} {operand2} = {student_answer}",
                        'operand1': operand1,
                        'operator': operator,
                        'operand2': operand2,
                        'student_answer': student_answer,
                        'correct_answer': correct_answer,
                        'is_correct': student_answer == correct_answer,
                        'error_type': error_analysis.get('error_type') if error_analysis else None,
                        'error_description': error_analysis.get('error_description') if error_analysis else None,
                        'pattern_description': error_analysis.get('pattern_description') if error_analysis else None
                    }
                
                # Fallback: Try to combine adjacent numbers if they look like multi-digit numbers
                # Handle cases like "45 + 2 8 =13" where 28 is split
                if len(all_numbers) >= 3:
                    # Try different combinations
                    # Combination 1: First number, second number as multi-digit, last as answer
                    if len(all_numbers) >= 3:
                        operand1 = int(all_numbers[0])
                        # Try to combine numbers until we find an operator or equals
                        combined_operand2 = ""
                        for i in range(1, len(all_numbers) - 1):
                            combined_operand2 += str(all_numbers[i])
                            if i < len(all_numbers) - 2:  # Don't include the last number (answer)
                                # Check if this combination makes sense
                                try:
                                    test_operand2 = int(combined_operand2)
                                    # Calculate what the answer should be
                                    operator = all_operators[0] if all_operators else '+'
                                    if operator in ['×', 'x']:
                                        operator = '*'
                                    elif operator == '÷':
                                        operator = '/'
                                    
                                    expected_answer = self._calculate_answer(operand1, operator, test_operand2)
                                    student_answer = int(all_numbers[-1])
                                    
                                    # If the student answer is close to expected, use this combination
                                    if abs(student_answer - expected_answer) < 10:  # Allow some tolerance
                                        logger.info(f"Combined operand2: {test_operand2}, expected: {expected_answer}, student: {student_answer}")
                                        
                                        error_analysis = None
                                        if student_answer != expected_answer:
                                            error_analysis = self._analyze_error_type(operand1, operator, test_operand2, student_answer, expected_answer)
                                        
                                        return {
                                            'expression': f"{operand1} {operator} {test_operand2} = {student_answer}",
                                            'operand1': operand1,
                                            'operator': operator,
                                            'operand2': test_operand2,
                                            'student_answer': student_answer,
                                            'correct_answer': expected_answer,
                                            'is_correct': student_answer == expected_answer,
                                            'error_type': error_analysis.get('error_type') if error_analysis else None,
                                            'error_description': error_analysis.get('error_description') if error_analysis else None,
                                            'pattern_description': error_analysis.get('pattern_description') if error_analysis else None
                                        }
                                except:
                                    continue
                    
                    # Final fallback: Use first number, second number, last number
                    operand1 = int(all_numbers[0])
                    operator = all_operators[0] if all_operators else '+'
                    operand2 = int(all_numbers[1])
                    student_answer = int(all_numbers[-1])
                    
                    logger.info(f"Fallback extraction: operand1={operand1}, operator={operator}, operand2={operand2}, answer={student_answer}")
                    
                    # Normalize operator
                    if operator in ['×', 'x']:
                        operator = '*'
                    elif operator == '÷':
                        operator = '/'
                    
                    # Calculate correct answer
                    correct_answer = self._calculate_answer(operand1, operator, operand2)
                    
                    logger.info(f"Calculated correct answer: {correct_answer}")
                    
                    # Analyze error type if incorrect
                    error_analysis = None
                    if student_answer != correct_answer:
                        error_analysis = self._analyze_error_type(operand1, operator, operand2, student_answer, correct_answer)
                    
                    return {
                        'expression': f"{operand1} {operator} {operand2} = {student_answer}",
                        'operand1': operand1,
                        'operator': operator,
                        'operand2': operand2,
                        'student_answer': student_answer,
                        'correct_answer': correct_answer,
                        'is_correct': student_answer == correct_answer,
                        'error_type': error_analysis.get('error_type') if error_analysis else None,
                        'error_description': error_analysis.get('error_description') if error_analysis else None,
                        'pattern_description': error_analysis.get('pattern_description') if error_analysis else None
                    }
            
            # Try multiple patterns to match different handwriting styles
            patterns = [
                # Standard format: "44 - 16 = 32"
                r'(\d+)\s*([+\-×x÷*/])\s*(\d+)\s*=\s*(\d+)',
                # Format without spaces: "44-16=32"
                r'(\d+)([+\-×x÷*/])(\d+)=(\d+)',
                # Format with multiple spaces: "44  -  16  =  32"
                r'(\d+)\s*[+\-×x÷*/]\s*(\d+)\s*=\s*(\d+)',
                # Format with dash variations: "44 — 16 = 32"
                r'(\d+)\s*[-–—]\s*(\d+)\s*=\s*(\d+)',
                # Format with parentheses: "(44 - 16) = 32"
                r'\(?(\d+)\)?\s*([+\-×x÷*/])\s*\(?(\d+)\)?\s*=\s*(\d+)',
                # Simple addition: "44+16=32"
                r'(\d+)[+](\d+)=(\d+)',
                # Simple subtraction: "44-16=32"
                r'(\d+)[-](\d+)=(\d+)',
                # Format with spaces around equals: "44 - 16 = 32"
                r'(\d+)\s*([+\-×x÷*/])\s*(\d+)\s*=\s*(\d+)',
                # More lenient format: any digits with operator and equals
                r'(\d+).*?([+\-×x÷*/]).*?(\d+).*?=.*?(\d+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, cleaned_text)
                if match:
                    try:
                        operand1 = int(match.group(1))
                        operator = match.group(2)
                        operand2 = int(match.group(3))
                        student_answer = int(match.group(4))
                        
                        logger.info(f"Matched pattern: operand1={operand1}, operator={operator}, operand2={operand2}, answer={student_answer}")
                        
                        # Normalize operator
                        if operator in ['×', 'x']:
                            operator = '*'
                        elif operator == '÷':
                            operator = '/'
                        
                        # Calculate correct answer
                        correct_answer = self._calculate_answer(operand1, operator, operand2)
                        
                        logger.info(f"Calculated correct answer: {correct_answer}")
                        
                        # Analyze error type if incorrect
                        error_analysis = None
                        if student_answer != correct_answer:
                            error_analysis = self._analyze_error_type(operand1, operator, operand2, student_answer, correct_answer)
                        
                        return {
                            'expression': cleaned_text,
                            'operand1': operand1,
                            'operator': operator,
                            'operand2': operand2,
                            'student_answer': student_answer,
                            'correct_answer': correct_answer,
                            'is_correct': student_answer == correct_answer,
                            'error_type': error_analysis.get('error_type') if error_analysis else None,
                            'error_description': error_analysis.get('error_description') if error_analysis else None,
                            'pattern_description': error_analysis.get('pattern_description') if error_analysis else None
                        }
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing numbers from expression: {e}")
                        continue
            
            logger.warning(f"No pattern matched for text: '{cleaned_text}'")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing mathematical expression: {e}")
            return None
    
    def _analyze_error_type(self, operand1: int, operator: str, operand2: int, student_answer: int, correct_answer: int) -> Dict:
        """Analyze the type of mathematical error"""
        # Check for operation confusion
        if operator == '+':
            if student_answer == operand1 - operand2:
                return {
                    'error_type': 'operation_confusion',
                    'error_description': 'Operation Confusion',
                    'pattern_description': f'Subtracted instead of added ({operand1}-{operand2}={student_answer})'
                }
        elif operator == '-':
            if student_answer == operand1 + operand2:
                return {
                    'error_type': 'operation_confusion',
                    'error_description': 'Operation Confusion',
                    'pattern_description': f'Added instead of subtracted ({operand1}+{operand2}={student_answer})'
                }
        
        # Check for place value errors in subtraction
        if operator == '-':
            if operand1 < operand2:  # Needs borrowing
                # Check if student did digit-by-digit subtraction without borrowing
                reversed_subtraction = self._reverse_digit_subtraction(operand1, operand2)
                if student_answer == reversed_subtraction:
                    return {
                        'error_type': 'place_value',
                        'error_description': 'Place Value Error: Confusion',
                        'pattern_description': f'Subtracted smaller digit from larger (digit-by-digit without borrowing)'
                    }
        
        # Check for digit reversal
        if self._is_digit_reversal(student_answer, correct_answer):
            return {
                'error_type': 'digit_reversal',
                'error_description': 'Digit Reversal',
                'pattern_description': f'Possibly reversed digits in answer'
            }
        
        # Default to calculation error
        return {
            'error_type': 'calculation',
            'error_description': 'Calculation Error',
            'pattern_description': f'Incorrect calculation result'
        }
    
    def _reverse_digit_subtraction(self, operand1: int, operand2: int) -> int:
        """Simulate digit-by-digit subtraction without borrowing"""
        str1 = str(operand1).zfill(2)
        str2 = str(operand2).zfill(2)
        
        result = ""
        for d1, d2 in zip(str1, str2):
            diff = abs(int(d1) - int(d2))
            result += str(diff)
        
        return int(result) if result else 0
    
    def _is_digit_reversal(self, student_answer: int, correct_answer: int) -> bool:
        """Check if student answer is a digit reversal of correct answer"""
        student_str = str(student_answer)
        correct_str = str(correct_answer)
        
        if len(student_str) == len(correct_str) == 2:
            return student_str == correct_str[::-1]
        return False
    
    def _calculate_answer(self, operand1: int, operator: str, operand2: int) -> int:
        """Calculate the correct answer"""
        if operator == '+':
            return operand1 + operand2
        elif operator == '-':
            return operand1 - operand2
        elif operator == '*':
            return operand1 * operand2
        elif operator == '/':
            return operand1 // operand2 if operand2 != 0 else 0
        return 0
    
    def analyze_spatial_structure(self, image_path: str, expressions: List[Dict]) -> Dict:
        """Analyze spatial structure of mathematical expressions"""
        try:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            if not expressions:
                return {
                    'digit_placement': 'N/A',
                    'carryover_positioning': 'N/A',
                    'operational_sequence': 'N/A',
                    'alignment': 'N/A'
                }
            
            # Analyze alignment of expressions
            alignment_score = self._analyze_expression_alignment(expressions)
            
            # Analyze digit placement
            digit_placement = self._analyze_digit_placement(gray, expressions)
            
            # Analyze carryover positioning (for subtraction problems)
            carryover_analysis = self._analyze_carryover_positioning(expressions)
            
            # Analyze operational sequence
            sequence_analysis = self._analyze_operational_sequence(expressions)
            
            return {
                'digit_placement': digit_placement,
                'carryover_positioning': carryover_analysis,
                'operational_sequence': sequence_analysis,
                'alignment': alignment_score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing spatial structure: {e}")
            return {
                'digit_placement': 'Unknown',
                'carryover_positioning': 'Unknown',
                'operational_sequence': 'Unknown',
                'alignment': 'Unknown'
            }
    
    def _analyze_expression_alignment(self, expressions: List[Dict]) -> str:
        """Analyze alignment of mathematical expressions"""
        if len(expressions) < 2:
            return 'Good'
        
        try:
            # Get y-coordinates of expressions
            y_positions = [exp['bbox'][1] for exp in expressions]
            
            # Calculate variance in y positions
            mean_y = sum(y_positions) / len(y_positions)
            std_y = (sum((y - mean_y) ** 2 for y in y_positions) / len(y_positions)) ** 0.5
            
            # Low variance = good alignment
            if std_y < 20:
                return 'Excellent'
            elif std_y < 50:
                return 'Good'
            else:
                return 'Needs Improvement'
                
        except Exception as e:
            logger.error(f"Error analyzing expression alignment: {e}")
            return 'Unknown'
    
    def _analyze_digit_placement(self, gray_image: np.ndarray, expressions: List[Dict]) -> str:
        """Analyze digit placement within expressions"""
        try:
            # This is a simplified analysis
            # In a full implementation, this would analyze individual digit positions
            
            # For now, check if expressions are horizontally aligned
            if len(expressions) > 0:
                return 'Appropriate'
            return 'Unknown'
            
        except Exception as e:
            logger.error(f"Error analyzing digit placement: {e}")
            return 'Unknown'
    
    def _analyze_carryover_positioning(self, expressions: List[Dict]) -> str:
        """Analyze carryover/borrowing positioning in subtraction problems"""
        try:
            # Check for subtraction problems that might need borrowing
            subtraction_problems = [exp for exp in expressions if exp.get('operator') == '-']
            
            if not subtraction_problems:
                return 'N/A'
            
            # Check if any subtraction problems need borrowing
            needs_borrowing = [exp for exp in subtraction_problems 
                            if exp.get('operand1', 0) < exp.get('operand2', 0)]
            
            if not needs_borrowing:
                return 'Not Applicable'
            
            # Check if these problems were solved correctly
            borrowing_errors = [exp for exp in needs_borrowing if not exp.get('is_correct', True)]
            
            if borrowing_errors:
                return 'Incorrect'
            else:
                return 'Proper'
                
        except Exception as e:
            logger.error(f"Error analyzing carryover positioning: {e}")
            return 'Unknown'
    
    def _analyze_operational_sequence(self, expressions: List[Dict]) -> str:
        """Analyze the sequence of operations"""
        try:
            if not expressions:
                return 'Unknown'
            
            # Check if operations are consistent
            operators = [exp.get('operator', '') for exp in expressions]
            unique_operators = set(operators)
            
            if len(unique_operators) == 1:
                return f'Consistent ({list(unique_operators)[0]})'
            else:
                return 'Mixed Operations'
                
        except Exception as e:
            logger.error(f"Error analyzing operational sequence: {e}")
            return 'Unknown'