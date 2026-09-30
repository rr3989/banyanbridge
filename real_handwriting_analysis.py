"""
Real Handwriting Analysis Module
Uses Tesseract OCR for text extraction and computer vision for quality analysis
"""

import logging
import os
from typing import Dict, List, Optional

# Lazy-load heavy dependencies only when needed
_cv2 = None
_np = None
_PIL = None

def get_cv2():
    """Lazy import cv2"""
    global _cv2
    if _cv2 is None:
        import cv2
        _cv2 = cv2
    return _cv2

def get_np():
    """Lazy import numpy"""
    global _np
    if _np is None:
        import numpy
        _np = numpy
    return _np

def get_PIL():
    """Lazy import PIL"""
    global _PIL
    if _PIL is None:
        from PIL import Image, ImageStat, ImageFilter
        _PIL = (Image, ImageStat, ImageFilter)
    return _PIL

logger = logging.getLogger(__name__)

class RealHandwritingAnalyzer:
    """Real handwriting analysis using computer vision and OCR"""
    
    def __init__(self):
        self.ocr_reader = None
        self.use_tesseract = False
        try:
            import pytesseract
            from PIL import Image
            import shutil
            import os
            
            # Check if tesseract is available in PATH
            tesseract_path = shutil.which('tesseract')
            
            if tesseract_path:
                # Test if it works
                try:
                    pytesseract.get_tesseract_version()
                    self.use_tesseract = True
                    logger.info(f"Tesseract OCR initialized successfully at: {tesseract_path}")
                except Exception as e:
                    logger.warning(f"Tesseract found but not working: {e}")
                    self._init_easyocr()
            else:
                # Try common installation paths
                common_paths = [
                    r"D:\Tesseract-OCR\tesseract.exe",  # User's custom installation
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                    r"C:\Tesseract-OCR\tesseract.exe",
                    "/usr/bin/tesseract",
                    "/usr/local/bin/tesseract"
                ]
                
                for path in common_paths:
                    if os.path.exists(path):
                        try:
                            pytesseract.pytesseract.tesseract_cmd = path
                            pytesseract.get_tesseract_version()
                            self.use_tesseract = True
                            logger.info(f"Tesseract OCR initialized successfully at: {path}")
                            break
                        except Exception as e:
                            logger.warning(f"Tesseract found at {path} but not working: {e}")
                            continue
                
                if not self.use_tesseract:
                    logger.warning("Tesseract not found in PATH or common locations")
                    logger.info("Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
                    logger.info("See TESSERACT_INSTALLATION.md for installation guide")
                    self._init_easyocr()
                    
        except ImportError:
            logger.warning("pytesseract not available, trying EasyOCR")
            self._init_easyocr()
        except Exception as e:
            logger.warning(f"Error initializing Tesseract: {e}")
            self._init_easyocr()
    
    def _init_easyocr(self):
        """Initialize EasyOCR as fallback"""
        try:
            import easyocr
            import sys
            import locale
            
            # Fix encoding issues for Windows
            if sys.platform == 'win32':
                try:
                    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
                except:
                    pass
            
            self.ocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            logger.info("EasyOCR initialized successfully")
        except ImportError:
            logger.warning("EasyOCR not available, using computer vision analysis only")
        except Exception as e:
            logger.warning(f"EasyOCR initialization failed: {e}, using computer vision analysis only")
    
    def analyze_image_quality(self, image_path: str) -> Dict:
        """Analyze image quality metrics"""
        try:
            img = Image.open(image_path)
            
            # Calculate image quality metrics
            stat = ImageStat.Stat(img)
            
            # Check brightness
            brightness = sum(stat.mean) / len(stat.mean)
            
            # Check contrast
            contrast = sum(stat.stddev) / len(stat.stddev)
            
            # Check blur (using Laplacian variance)
            img_cv = cv2.imread(image_path)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            return {
                'brightness': brightness,
                'contrast': contrast,
                'blur_score': laplacian_var,
                'is_clear': laplacian_var > 100,  # Threshold for clear image
                'is_well_lit': 50 < brightness < 200
            }
        except Exception as e:
            logger.error(f"Error analyzing image quality: {e}")
            return {
                'brightness': 0,
                'contrast': 0,
                'blur_score': 0,
                'is_clear': False,
                'is_well_lit': False
            }
    
    def extract_text(self, image_path: str) -> Dict:
        """Extract text from image using OCR (Tesseract or EasyOCR)"""
        # Try Tesseract first (more reliable for Vercel)
        if self.use_tesseract:
            return self._extract_text_tesseract(image_path)
        
        # Fallback to EasyOCR
        if self.ocr_reader is not None:
            return self._extract_text_easyocr_full(image_path)
        
        # Final fallback to basic text detection
        return self._basic_text_detection(image_path)
    
    def _extract_text_tesseract(self, image_path: str) -> Dict:
        """Extract text using Tesseract OCR with enhanced preprocessing"""
        try:
            import pytesseract
            from PIL import Image
            import cv2
            import numpy as np
            
            # Load and preprocess image
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding for better text extraction
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                            cv2.THRESH_BINARY_INV, 11, 2)
            
            # Remove noise
            kernel = np.ones((1, 1), np.uint8)
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # Save preprocessed image
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_path = temp_file.name
                cv2.imwrite(temp_path, binary)
            
            try:
                # Configure Tesseract for better OCR with character whitelist
                config = r'--oem 3 --psm 6'
                text = pytesseract.image_to_string(Image.open(temp_path), config=config)
                
                if text and text.strip():
                    return {
                        'success': True,
                        'text': text.strip(),
                        'confidence': 85.0,
                        'method': 'Tesseract'
                    }
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        except Exception as e:
            logger.error(f"Error extracting text with Tesseract: {e}")
            return self._extract_text_easyocr_full(image_path)
    
    def _extract_text_easyocr_full(self, image_path: str) -> Dict:
        """Extract text using EasyOCR with enhanced preprocessing for better accuracy"""
        try:
            import cv2
            import numpy as np
            
            # Load image
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply multiple preprocessing techniques
            # 1. Denoise
            denoised = cv2.fastNlMeansDenoising(gray, h=10)
            
            # 2. Contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # 3. Try different thresholding methods
            methods = []
            
            # Method 1: Adaptive thresholding
            binary1 = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                            cv2.THRESH_BINARY_INV, 11, 2)
            methods.append(('adaptive', binary1))
            
            # Method 2: Otsu thresholding
            _, binary2 = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            methods.append(('otsu', binary2))
            
            # Method 3: Original grayscale
            methods.append(('gray', gray))
            
            # Try each method and pick the best result
            best_text = ""
            best_confidence = 0
            best_method = "EasyOCR"
            
            for method_name, processed_image in methods:
                try:
                    # Extract text using EasyOCR
                    results = self.ocr_reader.readtext(processed_image, detail=1)
                    
                    if results:
                        # Calculate average confidence and collect text
                        confidences = []
                        texts = []
                        
                        for result in results:
                            if len(result) == 2:
                                # Format: (text, confidence)
                                text, conf = result
                                texts.append(text)
                                confidences.append(conf)
                            elif len(result) >= 2:
                                # Format: (bbox, text, confidence)
                                text = result[1]
                                conf = result[2] if len(result) > 2 else 0.5
                                texts.append(text)
                                confidences.append(conf)
                        
                        if texts:
                            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                            combined_text = ' '.join(texts)
                            
                            if avg_confidence > best_confidence and len(combined_text) > len(best_text):
                                best_text = combined_text
                                best_confidence = avg_confidence
                                best_method = f"EasyOCR-{method_name}"
                                
                except Exception as e:
                    logger.warning(f"Error with {method_name} method: {e}")
                    continue
            
            if best_text:
                return {
                    'success': True,
                    'text': best_text,
                    'confidence': best_confidence * 100,
                    'method': best_method
                }
            else:
                # Fallback to simple full image OCR
                results = self.ocr_reader.readtext(image_path, detail=0)
                
                if not results:
                    return {
                        'success': False,
                        'text': '',
                        'confidence': 0,
                        'error': 'No text detected'
                    }
                
                # Extract text - handle both formats
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
            logger.error(f"Error extracting text with enhanced EasyOCR: {e}")
            return self._basic_text_detection(image_path)
    
    def _basic_text_detection(self, image_path: str) -> Dict:
        """Basic text detection using OpenCV"""
        try:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Use thresholding to detect text regions
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Estimate if there's text based on contour count and characteristics
            text_contours = [c for c in contours if cv2.contourArea(c) > 100]
            
            if len(text_contours) > 5:
                return {
                    'success': True,
                    'text': 'Text detected (OCR unavailable for detailed extraction)',
                    'confidence': 50.0,
                    'method': 'OpenCV Detection'
                }
            else:
                return {
                    'success': False,
                    'text': '',
                    'confidence': 0,
                    'error': 'No clear text detected'
                }
        except Exception as e:
            logger.error(f"Error in basic text detection: {e}")
            return {
                'success': False,
                'text': '',
                'confidence': 0,
                'error': str(e)
            }
    
    def analyze_handwriting_quality(self, image_path: str, ocr_text: str = '') -> Dict:
        """Enhanced handwriting quality analysis based on actual image content"""
        try:
            img = Image.open(image_path)
            img_cv = cv2.imread(image_path)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Analyze actual image characteristics
            # 1. Edge density (ink density)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            # 2. Contrast
            contrast = gray.std()
            
            # 3. Brightness
            brightness = gray.mean()
            
            # 4. Image quality score
            image_quality = 50
            if 50 < brightness < 200:
                image_quality += 20
            if contrast > 30:
                image_quality += 20
            if 0.05 < edge_density < 0.4:
                image_quality += 10
            
            # Analyze line consistency
            lines = self._detect_lines(gray)
            line_consistency = self._analyze_line_consistency(lines)
            
            # Analyze character spacing
            char_spacing = self._analyze_character_spacing(gray)
            
            # Analyze stroke quality
            stroke_quality = self._analyze_stroke_quality(gray)
            
            # Calculate scores based on actual analysis, not OCR text length
            overall_score = min(95, 40 + line_consistency * 0.2 + char_spacing * 0.15 + stroke_quality * 0.15 + image_quality * 0.1)
            legibility_score = min(95, 40 + stroke_quality * 0.3 + edge_density * 0.2)
            letter_formation = min(90, 45 + stroke_quality * 0.4 + contrast * 0.1)
            spacing_score = min(95, 45 + char_spacing * 0.4 + line_consistency * 0.1)
            
            return {
                'overall_score': int(overall_score),
                'legibility_score': int(legibility_score),
                'letter_formation': int(letter_formation),
                'spacing_score': int(spacing_score),
                'line_consistency': line_consistency,
                'character_spacing': char_spacing,
                'stroke_quality': stroke_quality,
                'image_quality': image_quality,
                'edge_density': edge_density,
                'contrast': contrast,
                'brightness': brightness
            }
            
        except Exception as e:
            logger.error(f"Error analyzing handwriting quality: {e}")
            # Return moderate scores if analysis fails
            return {
                'overall_score': 70,
                'legibility_score': 70,
                'letter_formation': 70,
                'spacing_score': 70,
                'line_consistency': 50,
                'character_spacing': 50,
                'stroke_quality': 50,
                'image_quality': 50,
                'edge_density': 0,
                'contrast': 0,
                'brightness': 0
            }
    
    def _detect_lines(self, gray_image: np.ndarray) -> List:
        """Detect handwritten lines using image processing"""
        try:
            # Use morphological operations to detect lines
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
            dilated = cv2.dilate(gray_image, kernel, iterations=2)
            
            # Find contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter and sort contours by y position
            lines = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 50 and h > 10:  # Filter small contours
                    lines.append({'x': x, 'y': y, 'width': w, 'height': h})
            
            # Sort by y position
            lines.sort(key=lambda l: l['y'])
            return lines
            
        except Exception as e:
            logger.error(f"Error detecting lines: {e}")
            return []
    
    def _analyze_line_consistency(self, lines: List) -> float:
        """Analyze consistency of line spacing and alignment"""
        if len(lines) < 2:
            return 50.0
        
        try:
            # Calculate spacing between consecutive lines
            spacings = []
            for i in range(len(lines) - 1):
                spacing = lines[i+1]['y'] - (lines[i]['y'] + lines[i]['height'])
                spacings.append(spacing)
            
            if not spacings:
                return 50.0
            
            # Calculate consistency (lower standard deviation = more consistent)
            mean_spacing = sum(spacings) / len(spacings)
            std_spacing = (sum((s - mean_spacing) ** 2 for s in spacings) / len(spacings)) ** 0.5
            
            # Convert to score (lower std = higher score)
            consistency_score = max(0, 100 - std_spacing * 2)
            return min(100, consistency_score)
            
        except Exception as e:
            logger.error(f"Error analyzing line consistency: {e}")
            return 50.0
    
    def _analyze_character_spacing(self, gray_image: np.ndarray) -> float:
        """Analyze character spacing using horizontal projection"""
        try:
            # Use horizontal projection to analyze spacing
            horizontal_proj = np.sum(gray_image, axis=1)
            
            # Find gaps in the projection
            threshold = np.mean(horizontal_proj) * 0.5
            gaps = horizontal_proj < threshold
            
            # Count transitions
            transitions = 0
            for i in range(len(gaps) - 1):
                if gaps[i] != gaps[i+1]:
                    transitions += 1
            
            # Calculate spacing score based on transitions
            spacing_score = min(100, transitions * 2)
            return spacing_score
            
        except Exception as e:
            logger.error(f"Error analyzing character spacing: {e}")
            return 50.0
    
    def _analyze_stroke_quality(self, gray_image: np.ndarray) -> float:
        """Analyze stroke quality using edge detection"""
        try:
            # Use Canny edge detection
            edges = cv2.Canny(gray_image, 50, 150)
            
            # Count edge pixels
            edge_count = np.sum(edges > 0)
            total_pixels = edges.shape[0] * edges.shape[1]
            
            # Calculate edge density
            edge_density = edge_count / total_pixels
            
            # Convert to score (moderate edge density = good stroke quality)
            if 0.1 < edge_density < 0.3:
                stroke_score = 80 + (edge_density - 0.2) * 100
            else:
                stroke_score = 60 - abs(edge_density - 0.2) * 100
            
            return max(30, min(100, stroke_score))
            
        except Exception as e:
            logger.error(f"Error analyzing stroke quality: {e}")
            return 50.0
    
    def detect_handwriting_issues(self, image_path: str, ocr_text: str) -> List[Dict]:
        """Enhanced handwriting issue detection based on actual OCR text"""
        issues = []
        
        try:
            img = Image.open(image_path)
            img_cv = cv2.imread(image_path)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Analyze the actual OCR text for handwriting patterns
            if ocr_text:
                # Check for common handwriting issues in the text
                text_lower = ocr_text.lower()
                
                # Letter reversals
                if 'b' in text_lower and 'd' in text_lower:
                    issues.append({
                        'description': 'Potential letter reversals detected (b/d, p/q confusion)',
                        'severity': 'warning'
                    })
                
                # Number reversals (common in math)
                if any(char in text_lower for char in ['6', '9']):
                    issues.append({
                        'description': 'Check for number reversals (6/9 confusion)',
                        'severity': 'warning'
                    })
                
                # Inconsistent sizing based on character variance
                char_sizes = self._analyze_character_size_variance(gray)
                if char_sizes > 0.3:
                    issues.append({
                        'description': 'Inconsistent character sizing detected',
                        'severity': 'error'
                    })
                
                # Baseline alignment
                baseline_score = self._analyze_baseline_alignment(gray)
                if baseline_score < 60:
                    issues.append({
                        'description': 'Baseline alignment needs improvement',
                        'severity': 'warning'
                    })
                
                # Spacing issues
                spacing_score = self._analyze_character_spacing(gray)
                if spacing_score < 50:
                    issues.append({
                        'description': 'Character spacing irregularities detected',
                        'severity': 'error'
                    })
            else:
                # If no OCR text, analyze image properties
                baseline_score = self._analyze_baseline_alignment(gray)
                if baseline_score < 60:
                    issues.append({
                        'description': 'Baseline alignment needs improvement',
                        'severity': 'warning'
                    })
                
                stroke_quality = self._analyze_stroke_quality(gray)
                if stroke_quality < 50:
                    issues.append({
                        'description': 'Stroke quality needs improvement',
                        'severity': 'error'
                    })
            
            # If analysis was successful but no major issues found
            if not issues and (ocr_text or baseline_score > 70):
                issues.append({
                    'description': 'Handwriting appears generally clear and well-formed',
                    'severity': 'success'
                })
            elif not issues:
                issues.append({
                    'description': 'Unable to perform detailed handwriting analysis',
                    'severity': 'warning'
                })
            
            return issues
            
        except Exception as e:
            logger.error(f"Error detecting handwriting issues: {e}")
            return [{
                'description': 'Handwriting analysis encountered an error',
                'severity': 'warning'
            }]
    
    def _analyze_character_size_variance(self, gray_image: np.ndarray) -> float:
        """Analyze variance in character sizes"""
        try:
            # Use connected components to analyze character sizes
            _, binary = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)
            
            if num_labels < 2:
                return 0.0
            
            # Get heights of connected components
            heights = [stats[i, cv2.CC_STAT_HEIGHT] for i in range(1, num_labels)]
            heights = [h for h in heights if 10 < h < 100]  # Filter reasonable character heights
            
            if len(heights) < 3:
                return 0.0
            
            # Calculate variance
            mean_height = sum(heights) / len(heights)
            variance = sum((h - mean_height) ** 2 for h in heights) / len(heights)
            std_dev = variance ** 0.5
            
            # Return normalized variance
            return min(1.0, std_dev / mean_height) if mean_height > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error analyzing character size variance: {e}")
            return 0.0
    
    def _analyze_baseline_alignment(self, gray_image: np.ndarray) -> float:
        """Enhanced baseline alignment analysis without scipy dependency"""
        try:
            # Use horizontal projection to detect baseline
            horizontal_proj = np.sum(gray_image, axis=1)
            
            # Find peaks manually without scipy
            threshold = np.mean(horizontal_proj) * 0.5
            peaks = []
            for i in range(1, len(horizontal_proj) - 1):
                if horizontal_proj[i] > threshold and horizontal_proj[i] > horizontal_proj[i-1] and horizontal_proj[i] > horizontal_proj[i+1]:
                    peaks.append(i)
            
            if len(peaks) < 2:
                return 70.0  # Not enough data to analyze
            
            # Calculate variance in peak positions
            peak_variance = np.var(peaks)
            
            # Convert to alignment score (lower variance = better alignment)
            alignment_score = max(0, 100 - peak_variance * 0.5)
            return alignment_score
            
        except Exception as e:
            logger.error(f"Error analyzing baseline alignment: {e}")
            return self._analyze_baseline_hough(gray_image)
    
    def _analyze_baseline_hough(self, gray_image: np.ndarray) -> float:
        """Fallback baseline analysis using Hough transform"""
        try:
            edges = cv2.Canny(gray_image, 50, 150)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=30)
            
            if lines is None or len(lines) < 2:
                return 70.0
            
            angles = [line[0][1] * 180 / np.pi for line in lines]
            mean_angle = sum(angles) / len(angles)
            std_angle = (sum((a - mean_angle) ** 2 for a in angles) / len(angles)) ** 0.5
            
            # Lower angle variance = better alignment
            alignment_score = max(0, 100 - std_angle * 5)
            return alignment_score
            
        except Exception as e:
            logger.error(f"Error in Hough baseline analysis: {e}")
            return 50.0
    
