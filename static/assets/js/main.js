// Mobile Navigation Toggle
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

if (hamburger && navMenu) {
    hamburger.addEventListener('click', () => {
        navMenu.classList.toggle('active');

        const spans = hamburger.querySelectorAll('span');
        if (navMenu.classList.contains('active')) {
            spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
            spans[1].style.opacity = '0';
            spans[2].style.transform = 'rotate(-45deg) translate(7px, -6px)';
        } else {
            spans[0].style.transform = 'none';
            spans[1].style.opacity = '1';
            spans[2].style.transform = 'none';
        }
    });
}

const navLinks = document.querySelectorAll('.nav-menu a');
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        if (navMenu) {
            navMenu.classList.remove('active');
        }
        if (hamburger) {
            const spans = hamburger.querySelectorAll('span');
            spans[0].style.transform = 'none';
            spans[1].style.opacity = '1';
            spans[2].style.transform = 'none';
        }
    });
});

const slides = document.querySelectorAll('.slide');
const prevBtn = document.querySelector('.prev-btn');
const nextBtn = document.querySelector('.next-btn');
let currentSlide = 0;
let slideInterval;

function showSlide(index) {
    slides.forEach((slide, i) => {
        slide.classList.remove('active');
        if (i === index) {
            slide.classList.add('active');
        }
    });
}

function nextSlide() {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
}

function prevSlide() {
    currentSlide = (currentSlide - 1 + slides.length) % slides.length;
    showSlide(currentSlide);
}

function startSlideShow() {
    slideInterval = setInterval(nextSlide, 5000);
}

function stopSlideShow() {
    clearInterval(slideInterval);
}

if (slides.length > 0) {
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            prevSlide();
            stopSlideShow();
            startSlideShow();
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            nextSlide();
            stopSlideShow();
            startSlideShow();
        });
    }

    startSlideShow();
}

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    });
});

const donationForm = document.getElementById('donationForm');
const contactForm = document.getElementById('contactForm');

if (donationForm) {
    donationForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(this);
        const data = Object.fromEntries(formData);

        if (!data.name || !data.email || !data.amount) {
            alert('Please fill in all required fields.');
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(data.email)) {
            alert('Please enter a valid email address.');
            return;
        }

        if (parseInt(data.amount) < 1) {
            alert('Please enter a valid donation amount.');
            return;
        }

        alert('Thank you for your donation! We will redirect you to the payment gateway.');
        console.log('Donation form submitted:', data);
        this.reset();
    });
}

if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(this);
        const data = Object.fromEntries(formData);

        if (!data.name || !data.email || !data.subject || !data.message) {
            alert('Please fill in all required fields.');
            return;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(data.email)) {
            alert('Please enter a valid email address.');
            return;
        }

        fetch('/contact', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert(result.message);
                    this.reset();
                } else {
                    alert('Error: ' + (result.error || 'Failed to send message'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while sending your message. Please try again.');
            });
    });
}

window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        if (window.scrollY > 50) {
            navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        }
    }
});

const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.querySelectorAll('.section, .program-card, .impact-item, .vision-card, .team-card, .value-item, .giving-card, .partnership-card, .transparency-item, .opportunity-item').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

const sections = document.querySelectorAll('section[id]');
const navItems = document.querySelectorAll('.nav-menu a');

window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (scrollY >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });

    navItems.forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('href') === `#${current}`) {
            item.classList.add('active');
        }
    });
});

if ('loading' in HTMLImageElement.prototype) {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.loading = 'lazy';
    });
} else {
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js';
    document.body.appendChild(script);
}

document.querySelectorAll('img').forEach(img => {
    img.addEventListener('error', function () {
        this.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect width="100" height="100" fill="%23f0f0f0"/%3E%3Ctext x="50" y="50" font-family="Arial" font-size="12" text-anchor="middle" fill="%23999"%3EImage not available%3C/text%3E%3C/svg%3E';
    });
});

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

const debouncedScroll = debounce(() => {
    // Any scroll-related operations that should be debounced
}, 100);

window.addEventListener('scroll', debouncedScroll);

console.log('%c Welcome to Banyan Bridge Foundation! ', 'background: #2e4669; color: white; padding: 10px; font-size: 16px; border-radius: 5px;');
console.log('%c Transforming education, empowering communities ', 'background: #4a7c59; color: white; padding: 10px; font-size: 14px; border-radius: 5px;');

let mediaRecorder;
let audioChunks = [];
let audioStream;
let startTime;
let recordingDuration = 0;
let lastAudioBlob = null;

const voiceBtn = document.getElementById('voiceBtn');
const voiceModal = document.getElementById('voiceModal');
const closeVoiceModal = document.getElementById('closeVoiceModal');
const startRecordBtn = document.getElementById('startRecordBtn');
const stopRecordBtn = document.getElementById('stopRecordBtn');
const playRecordBtn = document.getElementById('playRecordBtn');
const analyzeRecordBtn = document.getElementById('analyzeRecordBtn');
const recordingStatus = document.getElementById('recordingStatus');
const assessmentResults = document.getElementById('assessmentResults');
const submitAssessmentBtn = document.getElementById('submitAssessmentBtn');
const referenceTextInput = document.getElementById('referenceText');

// Handwriting Assessment Variables
const handwritingBtn = document.getElementById('handwritingBtn');
const handwritingModal = document.getElementById('handwritingModal');
const closeHandwritingModal = document.getElementById('closeHandwritingModal');
const startCameraBtn = document.getElementById('startCameraBtn');
const captureBtn = document.getElementById('captureBtn');
const retakeBtn = document.getElementById('retakeBtn');
const analyzeHandwritingBtn = document.getElementById('analyzeHandwritingBtn');
const submitHandwritingBtn = document.getElementById('submitHandwritingBtn');
const cameraPreview = document.getElementById('cameraPreview');
const cameraCanvas = document.getElementById('cameraCanvas');
const capturedImage = document.getElementById('capturedImage');
const handwritingStatus = document.getElementById('handwritingStatus');
const handwritingResults = document.getElementById('handwritingResults');

// Math Assessment Variables
const mathBtn = document.getElementById('mathBtn');
const mathModal = document.getElementById('mathModal');
const closeMathModal = document.getElementById('closeMathModal');
const startMathCameraBtn = document.getElementById('startMathCameraBtn');
const captureMathBtn = document.getElementById('captureMathBtn');
const retakeMathBtn = document.getElementById('retakeMathBtn');
const analyzeMathBtn = document.getElementById('analyzeMathBtn');
const mathCameraPreview = document.getElementById('mathCameraPreview');
const mathCameraCanvas = document.getElementById('mathCameraCanvas');
const mathCapturedImage = document.getElementById('mathCapturedImage');
const mathStatus = document.getElementById('mathStatus');
const mathResults = document.getElementById('mathResults');
const studentNameInput = document.getElementById('studentName');

let cameraStream = null;
let capturedImageData = null;
let mathCameraStream = null;
let mathCapturedImageData = null;

function resetAssessmentDisplay() {
    if (!assessmentResults) return;
    assessmentResults.style.display = 'none';

    const fields = [
        'razLevel', 'wcpm', 'phonicsErrors', 'skips', 'stumbles', 'struggles',
        'whatWentRight', 'whatWentWrong', 'razReason', 'phonicsDetail'
    ];

    fields.forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;

        if (id === 'razLevel' || id === 'wcpm') {
            el.textContent = '-';
        } else if (['phonicsErrors', 'skips', 'stumbles', 'struggles'].includes(id)) {
            el.textContent = '0';
        } else {
            el.textContent = '-';
        }
    });

    // Reset button states
    if (playRecordBtn) playRecordBtn.disabled = true;
    if (analyzeRecordBtn) analyzeRecordBtn.disabled = true;
    if (recordingStatus) recordingStatus.textContent = '';
}

if (voiceBtn) {
    voiceBtn.addEventListener('click', () => {
        if (voiceModal) {
            voiceModal.classList.add('show');
        }
        resetAssessmentDisplay();
    });
}

if (closeVoiceModal) {
    closeVoiceModal.addEventListener('click', () => {
        if (voiceModal) {
            voiceModal.classList.remove('show');
        }
        stopRecording();
    });
}

window.addEventListener('click', (e) => {
    if (voiceModal && e.target === voiceModal) {
        voiceModal.classList.remove('show');
        stopRecording();
    }
});

if (startRecordBtn) {
    startRecordBtn.addEventListener('click', async () => {
        try {
            if (!navigator.mediaDevices || !window.MediaRecorder) {
                recordingStatus.textContent = '❌ Your browser does not support microphone recording.';
                return;
            }

            resetAssessmentDisplay();
            audioChunks = [];
            lastAudioBlob = null;
            audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(audioStream, { mimeType: 'audio/webm' });

            mediaRecorder.ondataavailable = (event) => {
                if (event.data && event.data.size > 0) {
                    audioChunks.push(event.data);
                }
            };

            mediaRecorder.onstop = () => {
                lastAudioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType || 'audio/webm' });
                recordingDuration = (Date.now() - startTime) / 1000;
                
                console.log('Recording stopped. Blob size:', lastAudioBlob.size, 'bytes');
                console.log('Recording duration:', recordingDuration, 'seconds');
                
                if (playRecordBtn) {
                    playRecordBtn.disabled = false;
                    playRecordBtn.audioBlob = lastAudioBlob;
                }

                if (analyzeRecordBtn) {
                    analyzeRecordBtn.disabled = false;
                }

                if (lastAudioBlob && lastAudioBlob.size > 0) {
                    recordingStatus.textContent = '✅ Recording complete. Click "Analyze Recording" to process your voice.';
                    assessmentResults.style.display = 'block';
                } else {
                    recordingStatus.textContent = '❌ No audio was captured. Please record again.';
                }
            };

            mediaRecorder.start();
            startTime = Date.now();

            startRecordBtn.disabled = true;
            stopRecordBtn.disabled = false;
            recordingStatus.textContent = '🎙️ Recording in progress...';
            recordingStatus.classList.add('recording');
        } catch (error) {
            recordingStatus.textContent = '❌ Error accessing microphone: ' + (error.message || 'Unknown microphone error');
            console.error('Error accessing microphone:', error);
        }
    });
}

if (stopRecordBtn) {
    stopRecordBtn.addEventListener('click', () => {
        stopRecording();
    });
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        if (audioStream) {
            audioStream.getTracks().forEach(track => track.stop());
        }

        if (startRecordBtn) startRecordBtn.disabled = false;
        if (stopRecordBtn) stopRecordBtn.disabled = true;
        if (analyzeRecordBtn) analyzeRecordBtn.disabled = true;
        if (recordingStatus) {
            recordingStatus.textContent = '✅ Recording stopped. Duration: ' + Number(recordingDuration || 0).toFixed(2) + 's';
            recordingStatus.classList.remove('recording');
        }
    }
}

if (playRecordBtn) {
    playRecordBtn.addEventListener('click', () => {
        if (playRecordBtn.audioBlob) {
            const audioUrl = URL.createObjectURL(playRecordBtn.audioBlob);
            const audio = new Audio(audioUrl);
            audio.play();
        }
    });
}

if (analyzeRecordBtn) {
    analyzeRecordBtn.addEventListener('click', () => {
        analyzeRecording();
    });
}

async function analyzeRecording() {
    if (!lastAudioBlob || lastAudioBlob.size === 0) {
        recordingStatus.textContent = '❌ No audio was captured. Please record again.';
        return;
    }

    // Check if the audio blob is too small (less than 1KB)
    if (lastAudioBlob.size < 1000) {
        recordingStatus.textContent = '❌ The recording is too short. Please record again and speak clearly.';
        return;
    }

    const referenceText = referenceTextInput ? referenceTextInput.value.trim() : '';
    if (!referenceText) {
        recordingStatus.textContent = '❌ Please enter the reading text before submitting the recording.';
        return;
    }

    assessmentResults.style.display = 'block';
    recordingStatus.textContent = '🔄 Transcribing audio locally with Whisper...';
    recordingStatus.classList.add('recording');

    try {
        const formData = new FormData();
        formData.append('audio', lastAudioBlob, 'recording.webm');
        formData.append('reference_text', referenceText);
        formData.append('duration_seconds', String(recordingDuration || 0));

        console.log('Sending voice analysis request...');
        console.log('Audio blob size:', lastAudioBlob.size);
        console.log('Reference text:', referenceText);
        console.log('Duration:', recordingDuration);

        const response = await fetch('/api/voice/analyze', {
            method: 'POST',
            body: formData,
        });

        console.log('Response status:', response.status);
        
        const data = await response.json();
        console.log('Response data:', data);

        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Speech analysis failed.');
        }

        document.getElementById('razLevel').textContent = data.raz_level || 'N/A';
        document.getElementById('wcpm').textContent = Number(data.wpm || 0).toFixed(1) + ' WPM';
        document.getElementById('phonicsErrors').textContent = Number(data.phonics_errors || 0);
        document.getElementById('skips').textContent = Number(data.skips || 0);
        document.getElementById('stumbles').textContent = Number(data.stumbles || 0);
        document.getElementById('struggles').textContent = Number(data.struggles || 0);

        const strengths = Array.isArray(data.strengths) && data.strengths.length ? data.strengths.join(' ') : 'No major strengths detected.';
        const issues = Array.isArray(data.issues) && data.issues.length ? data.issues.join(' ') : 'No major issues were detected.';
        document.getElementById('whatWentRight').textContent = strengths;
        document.getElementById('whatWentWrong').textContent = issues;
        document.getElementById('razReason').textContent = data.raz_reason || 'RAZ level was assigned based on pace and phonics errors.';
        document.getElementById('phonicsDetail').textContent = data.phonics_error_detail || 'No phonics mismatches were recorded.';

        recordingStatus.textContent = data.transcript
            ? '✅ Transcript captured: ' + data.transcript.slice(0, 120)
            : '✅ Assessment complete.';
        recordingStatus.classList.remove('recording');
    } catch (error) {
        recordingStatus.textContent = '❌ ' + (error.message || 'Unable to analyze the audio right now.');
        recordingStatus.classList.remove('recording');
        console.error('Voice analysis failed:', error);
    }
}

if (submitAssessmentBtn) {
    submitAssessmentBtn.addEventListener('click', () => {
        if (voiceModal) {
            voiceModal.classList.remove('show');
        }
        if (recordingStatus) {
            recordingStatus.textContent = 'Assessment submitted successfully.';
        }
        if (assessmentResults) {
            assessmentResults.style.display = 'none';
        }
    });
}

// Handwriting Assessment Functionality
if (handwritingBtn) {
    handwritingBtn.addEventListener('click', () => {
        if (handwritingModal) {
            handwritingModal.classList.add('show');
        }
        resetHandwritingAssessment();
    });
}

if (closeHandwritingModal) {
    closeHandwritingModal.addEventListener('click', () => {
        if (handwritingModal) {
            handwritingModal.classList.remove('show');
        }
        stopCamera();
    });
}

window.addEventListener('click', (e) => {
    if (handwritingModal && e.target === handwritingModal) {
        handwritingModal.classList.remove('show');
        stopCamera();
    }
});

function resetHandwritingAssessment() {
    if (handwritingResults) {
        handwritingResults.style.display = 'none';
    }
    
    if (handwritingStatus) {
        handwritingStatus.textContent = '';
    }
    
    if (capturedImage) {
        capturedImage.style.display = 'none';
        capturedImage.src = '';
    }
    
    if (cameraPreview) {
        cameraPreview.style.display = 'block';
    }
    
    if (captureBtn) {
        captureBtn.disabled = true;
    }
    
    if (analyzeHandwritingBtn) {
        analyzeHandwritingBtn.disabled = true;
    }
    
    if (retakeBtn) {
        retakeBtn.style.display = 'none';
    }
    
    capturedImageData = null;
    stopCamera();
}

if (startCameraBtn) {
    startCameraBtn.addEventListener('click', async () => {
        try {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                handwritingStatus.textContent = '❌ Your browser does not support camera access.';
                return;
            }

            cameraStream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    facingMode: 'environment',
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                } 
            });

            if (cameraPreview) {
                cameraPreview.srcObject = cameraStream;
                cameraPreview.style.display = 'block';
            }

            if (capturedImage) {
                capturedImage.style.display = 'none';
            }

            if (captureBtn) {
                captureBtn.disabled = false;
            }

            if (startCameraBtn) {
                startCameraBtn.disabled = true;
            }

            if (handwritingStatus) {
                handwritingStatus.textContent = '📷 Camera started. Position the paper and click Capture.';
            }

        } catch (error) {
            handwritingStatus.textContent = '❌ Error accessing camera: ' + (error.message || 'Unknown camera error');
            console.error('Error accessing camera:', error);
        }
    });
}

if (captureBtn) {
    captureBtn.addEventListener('click', () => {
        if (!cameraStream || !cameraPreview) {
            handwritingStatus.textContent = '❌ Camera not available.';
            return;
        }

        const canvas = cameraCanvas;
        const video = cameraPreview;
        
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        capturedImageData = canvas.toDataURL('image/jpeg', 0.8);
        
        if (capturedImage) {
            capturedImage.src = capturedImageData;
            capturedImage.style.display = 'block';
        }
        
        if (cameraPreview) {
            cameraPreview.style.display = 'none';
        }
        
        if (captureBtn) {
            captureBtn.disabled = true;
        }
        
        if (analyzeHandwritingBtn) {
            analyzeHandwritingBtn.disabled = false;
        }
        
        if (retakeBtn) {
            retakeBtn.style.display = 'inline-block';
        }
        
        if (handwritingStatus) {
            handwritingStatus.textContent = '✅ Image captured. Click "Analyze Handwriting" to process.';
        }
    });
}

if (retakeBtn) {
    retakeBtn.addEventListener('click', () => {
        if (capturedImage) {
            capturedImage.style.display = 'none';
            capturedImage.src = '';
        }
        
        if (cameraPreview) {
            cameraPreview.style.display = 'block';
        }
        
        if (captureBtn) {
            captureBtn.disabled = false;
        }
        
        if (analyzeHandwritingBtn) {
            analyzeHandwritingBtn.disabled = true;
        }
        
        if (retakeBtn) {
            retakeBtn.style.display = 'none';
        }
        
        capturedImageData = null;
        
        if (handwritingStatus) {
            handwritingStatus.textContent = '📷 Ready to capture again.';
        }
    });
}

function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }
    
    if (startCameraBtn) {
        startCameraBtn.disabled = false;
    }
}

if (analyzeHandwritingBtn) {
    analyzeHandwritingBtn.addEventListener('click', () => {
        analyzeHandwriting();
    });
}

async function analyzeHandwriting() {
    if (!capturedImageData) {
        handwritingStatus.textContent = '❌ No image captured. Please capture an image first.';
        return;
    }

    handwritingStatus.textContent = '🔄 Analyzing handwriting...';
    handwritingResults.style.display = 'block';

    try {
        // Convert base64 to blob
        const response = await fetch(capturedImageData);
        const blob = await response.blob();
        
        const formData = new FormData();
        formData.append('image', blob, 'handwriting.jpg');

        console.log('Sending handwriting analysis request...');
        console.log('Image blob size:', blob.size);

        const apiResponse = await fetch('/api/handwriting/analyze', {
            method: 'POST',
            body: formData,
        });

        console.log('Response status:', apiResponse.status);
        
        const data = await apiResponse.json();
        console.log('Response data:', data);

        if (!apiResponse.ok || !data.success) {
            throw new Error(data.error || 'Handwriting analysis failed.');
        }

        // Display results
        document.getElementById('overallScore').textContent = data.overall_score || '-';
        document.getElementById('legibilityScore').textContent = data.legibility_score || '-';
        document.getElementById('letterFormation').textContent = data.letter_formation || '-';
        document.getElementById('spacingScore').textContent = data.spacing_score || '-';

        // Display misconceptions
        const misconceptionList = document.getElementById('misconceptionList');
        if (data.misconceptions && data.misconceptions.length > 0) {
            misconceptionList.innerHTML = data.misconceptions.map(m => 
                `<li class="${m.severity}-type">${m.description}</li>`
            ).join('');
        } else {
            misconceptionList.innerHTML = '<p>No misconceptions detected.</p>';
        }

        // Display errors
        const errorList = document.getElementById('errorList');
        if (data.errors && data.errors.length > 0) {
            errorList.innerHTML = data.errors.map(e => 
                `<li class="${e.severity}-type">${e.description}</li>`
            ).join('');
        } else {
            errorList.innerHTML = '<p>No errors detected.</p>';
        }

        // Display recommendations
        const recommendationList = document.getElementById('recommendationList');
        if (data.recommendations && data.recommendations.length > 0) {
            recommendationList.innerHTML = data.recommendations.map(r => 
                `<li>${r}</li>`
            ).join('');
        } else {
            recommendationList.innerHTML = '<p>No specific recommendations.</p>';
        }

        handwritingStatus.textContent = '✅ Handwriting analysis complete.';
    } catch (error) {
        handwritingStatus.textContent = '❌ ' + (error.message || 'Unable to analyze handwriting right now.');
        console.error('Handwriting analysis failed:', error);
    }
}

if (submitHandwritingBtn) {
    submitHandwritingBtn.addEventListener('click', () => {
        if (handwritingModal) {
            handwritingModal.classList.remove('show');
        }
        if (handwritingStatus) {
            handwritingStatus.textContent = 'Assessment submitted successfully.';
        }
        if (handwritingResults) {
            handwritingResults.style.display = 'none';
        }
        stopCamera();
    });
}

// Math Assessment Functionality
if (mathBtn) {
    mathBtn.addEventListener('click', () => {
        if (mathModal) {
            mathModal.classList.add('show');
        }
        resetMathAssessment();
    });
}

if (closeMathModal) {
    closeMathModal.addEventListener('click', () => {
        if (mathModal) {
            mathModal.classList.remove('show');
        }
        stopMathCamera();
    });
}

window.addEventListener('click', (e) => {
    if (mathModal && e.target === mathModal) {
        mathModal.classList.remove('show');
        stopMathCamera();
    }
});

function resetMathAssessment() {
    if (mathResults) {
        mathResults.style.display = 'none';
        mathResults.innerHTML = '';
    }
    
    if (mathStatus) {
        mathStatus.textContent = '';
    }
    
    if (mathCapturedImage) {
        mathCapturedImage.style.display = 'none';
        mathCapturedImage.src = '';
    }
    
    if (mathCameraPreview) {
        mathCameraPreview.style.display = 'block';
    }
    
    if (captureMathBtn) {
        captureMathBtn.disabled = true;
    }
    
    if (analyzeMathBtn) {
        analyzeMathBtn.disabled = true;
    }
    
    if (retakeMathBtn) {
        retakeMathBtn.style.display = 'none';
    }
    
    if (studentNameInput) {
        studentNameInput.value = '';
    }
    
    mathCapturedImageData = null;
    stopMathCamera();
}

if (startMathCameraBtn) {
    startMathCameraBtn.addEventListener('click', async () => {
        try {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                mathStatus.textContent = '❌ Your browser does not support camera access.';
                return;
            }

            mathCameraStream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    facingMode: 'environment',
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                } 
            });

            if (mathCameraPreview) {
                mathCameraPreview.srcObject = mathCameraStream;
                mathCameraPreview.style.display = 'block';
            }

            if (mathCapturedImage) {
                mathCapturedImage.style.display = 'none';
            }

            if (captureMathBtn) {
                captureMathBtn.disabled = false;
            }

            if (startMathCameraBtn) {
                startMathCameraBtn.disabled = true;
            }

            if (mathStatus) {
                mathStatus.textContent = '📷 Camera started. Position the math work and click Capture.';
            }

        } catch (error) {
            mathStatus.textContent = '❌ Error accessing camera: ' + (error.message || 'Unknown camera error');
            console.error('Error accessing camera:', error);
        }
    });
}

if (captureMathBtn) {
    captureMathBtn.addEventListener('click', () => {
        if (!mathCameraStream || !mathCameraPreview) {
            mathStatus.textContent = '❌ Camera not available.';
            return;
        }

        const canvas = mathCameraCanvas;
        const video = mathCameraPreview;
        
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        mathCapturedImageData = canvas.toDataURL('image/jpeg', 0.8);
        
        if (mathCapturedImage) {
            mathCapturedImage.src = mathCapturedImageData;
            mathCapturedImage.style.display = 'block';
        }
        
        if (mathCameraPreview) {
            mathCameraPreview.style.display = 'none';
        }
        
        if (captureMathBtn) {
            captureMathBtn.disabled = true;
        }
        
        if (analyzeMathBtn) {
            analyzeMathBtn.disabled = false;
        }
        
        if (retakeMathBtn) {
            retakeMathBtn.style.display = 'inline-block';
        }
        
        if (mathStatus) {
            mathStatus.textContent = '✅ Image captured. Click "Analyze Math" to process.';
        }
    });
}

if (retakeMathBtn) {
    retakeMathBtn.addEventListener('click', () => {
        if (mathCapturedImage) {
            mathCapturedImage.style.display = 'none';
            mathCapturedImage.src = '';
        }
        
        if (mathCameraPreview) {
            mathCameraPreview.style.display = 'block';
        }
        
        if (captureMathBtn) {
            captureMathBtn.disabled = false;
        }
        
        if (analyzeMathBtn) {
            analyzeMathBtn.disabled = true;
        }
        
        if (retakeMathBtn) {
            retakeMathBtn.style.display = 'none';
        }
        
        mathCapturedImageData = null;
        
        if (mathStatus) {
            mathStatus.textContent = '📷 Ready to capture again.';
        }
    });
}

function stopMathCamera() {
    if (mathCameraStream) {
        mathCameraStream.getTracks().forEach(track => track.stop());
        mathCameraStream = null;
    }
    
    if (startMathCameraBtn) {
        startMathCameraBtn.disabled = false;
    }
}

if (analyzeMathBtn) {
    analyzeMathBtn.addEventListener('click', () => {
        analyzeMathWork();
    });
}

async function analyzeMathWork() {
    if (!mathCapturedImageData) {
        mathStatus.textContent = '❌ No image captured. Please capture an image first.';
        return;
    }

    const studentName = studentNameInput ? studentNameInput.value.trim() : 'Student';
    if (!studentName) {
        mathStatus.textContent = '❌ Please enter the student name.';
        return;
    }

    mathStatus.textContent = '🔄 Analyzing mathematical handwriting using YOLOv8 + TrOCR...';
    mathResults.style.display = 'block';
    mathResults.innerHTML = '<div class="loading-spinner">Processing...</div>';

    try {
        // Convert base64 to blob
        const response = await fetch(mathCapturedImageData);
        const blob = await response.blob();
        
        const formData = new FormData();
        formData.append('image', blob, 'math_work.jpg');
        formData.append('student_name', studentName);

        console.log('Sending mathematical analysis request...');
        console.log('Image blob size:', blob.size);
        console.log('Student name:', studentName);

        const apiResponse = await fetch('/api/math/analyze', {
            method: 'POST',
            body: formData,
        });

        console.log('Response status:', apiResponse.status);
        
        const data = await apiResponse.json();
        console.log('Response data:', data);

        if (!apiResponse.ok || !data.success) {
            throw new Error(data.error || 'Mathematical analysis failed.');
        }

        // Generate assessment card
        generateMathAssessmentCard(data);
        
        mathStatus.textContent = '✅ Mathematical analysis complete.';
    } catch (error) {
        mathStatus.textContent = '❌ ' + (error.message || 'Unable to analyze mathematical handwriting right now.');
        console.error('Mathematical analysis failed:', error);
        mathResults.innerHTML = '';
    }
}

function generateMathAssessmentCard(data) {
    const cardHTML = `
        <div class="assessment-card">
            <div class="assessment-card-header">
                <h3>Mathematical Assessment Results</h3>
                <div class="student-info">
                    <span><strong>Student:</strong> ${data.student_name}</span>
                    <span><strong>Date:</strong> ${data.timestamp}</span>
                </div>
            </div>
            <div class="assessment-card-body">
                <div class="math-problems-grid">
                    ${data.expressions.map(exp => `
                        <div class="math-problem ${exp.is_correct ? 'correct' : 'incorrect'}">
                            <div class="expression">${exp.expression}</div>
                            <div class="status-icon">${exp.is_correct ? '✓' : '✗'}</div>
                        </div>
                    `).join('')}
                </div>
                
                <div class="ai-analysis-section">
                    <h4>AI Analysis Results</h4>
                    
                    <div class="analysis-stats">
                        <div class="stat-item">
                            <div class="stat-label">OCR Confidence</div>
                            <div class="stat-value">${data.ocr_confidence}%</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Problems Analyzed</div>
                            <div class="stat-value">${data.problems_analyzed}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Correct Answers</div>
                            <div class="stat-value">${data.correct_answers}/${data.problems_analyzed}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Accuracy</div>
                            <div class="stat-value">${data.accuracy_percentage}%</div>
                        </div>
                    </div>
                    
                    <div class="primary-error">
                        <div class="error-label">Primary Error:</div>
                        <div>${data.primary_error}</div>
                    </div>
                    
                    ${data.error_breakdown.length > 0 ? `
                    <div class="error-breakdown">
                        <h5>Error Breakdown:</h5>
                        ${data.error_breakdown.map(error => `
                            <div class="error-item">
                                <div class="expression">${error.expression}</div>
                                <div class="pattern">${error.pattern_description}</div>
                            </div>
                        `).join('')}
                    </div>
                    ` : ''}
                    
                    <div class="ai-insight">
                        <h5>AI Insight:</h5>
                        <p>${data.ai_insight}</p>
                    </div>
                    
                    <div class="recommendations">
                        <h5>Recommendations:</h5>
                        <ul>
                            ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    mathResults.innerHTML = cardHTML;
}