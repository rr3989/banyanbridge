# Tesseract OCR Installation Instructions

## Why Install Tesseract?
Tesseract OCR is the industry standard for text recognition and will significantly improve handwriting accuracy from the current ~10% (EasyOCR) to ~80-90%.

## Installation Steps for Windows

### Option 1: Manual Download (Recommended)

1. **Download Tesseract**:
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Click on "Tesseract at UB-Mannheim"
   - Download: `tesseract-ocr-w64-setup-v5.3.3.exe` (64-bit Windows)

2. **Install Tesseract**:
   - Run the downloaded installer
   - Choose installation path: `C:\Program Files\Tesseract-OCR`
   - Select "Additional language data" and download English language pack
   - Complete the installation

3. **Add to PATH**:
   - Right-click "This PC" → Properties → Advanced system settings
   - Click "Environment Variables"
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add: `C:\Program Files\Tesseract-OCR`
   - Click OK on all dialogs

4. **Verify Installation**:
   - Open new PowerShell window
   - Run: `tesseract --version`
   - You should see version information

### Option 2: Using pip (Python wrapper)

The Python wrapper is already installed (`pytesseract==0.3.13`), but you still need the Tesseract binary from Option 1.

## Configuration for Banyan Bridge App

Once Tesseract is installed:

1. **Restart the Flask app** (it will automatically detect Tesseract)
2. **Test handwriting assessment** - accuracy should improve dramatically

## Verification

After installation, the app logs should show:
```
INFO:real_handwriting_analysis:Tesseract initialized successfully
INFO:real_handwriting_analysis:Using Tesseract for text recognition
```

Instead of:
```
WARNING:real_handwriting_analysis:Tesseract not found, trying EasyOCR
```

## Expected Results

- **Current OCR**: "7h 5 1 L L TAA" (poor)
- **With Tesseract**: "This is Customer Support" (good to excellent)

## Troubleshooting

If Tesseract is not detected:
1. Make sure you added it to PATH
2. Restart your computer
3. Try running `tesseract --version` in PowerShell
4. Check that the installation path is correct

## Alternative: Cloud OCR

If installation is too complex, consider using Google Cloud Vision API for production deployment.