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
const recordingStatus = document.getElementById('recordingStatus');
const assessmentResults = document.getElementById('assessmentResults');
const submitAssessmentBtn = document.getElementById('submitAssessmentBtn');
const referenceTextInput = document.getElementById('referenceText');

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
                if (playRecordBtn) {
                    playRecordBtn.disabled = false;
                    playRecordBtn.audioBlob = lastAudioBlob;
                }

                if (lastAudioBlob && lastAudioBlob.size > 0) {
                    assessmentResults.style.display = 'block';
                    analyzeRecording();
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

async function analyzeRecording() {
    if (!lastAudioBlob || lastAudioBlob.size === 0) {
        recordingStatus.textContent = '❌ No audio was captured. Please record again.';
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

        const response = await fetch('/api/voice/analyze', {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();

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