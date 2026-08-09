# Banyan Bridge Foundation - Educational Platform

A modern, responsive Flask web application for Banyan Bridge Foundation, an NGO dedicated to transforming education and empowering communities through innovative learning programs.

## Project Overview

This is a comprehensive educational platform built with Flask, Python, and modern web technologies. The platform provides role-based access for teachers, students, and administrators to manage educational content, assignments, and assessments.

## Project Overview

This is a complete static recreation of the original WordPress website, built with pure HTML, CSS, and JavaScript. The website showcases the foundation's mission, programs, impact, and provides ways for visitors to get involved through donations and volunteering.

## Features

### Public Website
- **Responsive Design**: Fully responsive layout that works on desktop, tablet, and mobile devices
- **Modern UI/UX**: Clean, professional design with smooth animations and transitions
- **Accessibility**: Semantic HTML and proper ARIA labels for screen readers
- **Interactive Elements**: Hero image slider, mobile navigation menu, smooth scrolling

### Educational Platform
- **User Authentication**: Secure login system with role-based access control
- **Teacher Dashboard**: Upload and manage PDF teaching materials
- **Student Dashboard**: Download materials, upload assignments, take exams
- **Admin Dashboard**: Create exams, manage users, view platform statistics
- **Exam System**: Multiple-choice questions with instant scoring and detailed feedback
- **File Management**: Secure PDF upload/download with size validation

## Project Structure

```
banyanbridge/
├── app.py                  # Flask application
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
│   ├── index.html          # Homepage
│   ├── about.html          # About Us page
│   ├── donate.html         # Donation page
│   ├── contact.html        # Contact page
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── admin/              # Admin dashboard templates
│   ├── teacher/            # Teacher dashboard templates
│   └── student/            # Student dashboard templates
├── static/                 # Static files
│   └── assets/             # CSS, JS, images
│       ├── css/
│       │   └── style.css   # Main stylesheet
│       ├── js/
│       │   └── main.js     # JavaScript functionality
│       └── images/         # All website images
├── uploads/                # File upload directory
└── README.md               # This file
```

## Pages

### Homepage (index.html)
- Hero section with image slider
- About the foundation
- Programs overview
- Impact showcase
- SDG alignment
- Call-to-action sections

### About Page (about.html)
- Mission and vision
- Organization story
- Team members
- Core values
- Partnership opportunities

### Donate Page (donate.html)
- Donation impact options
- Multiple donation methods
- Secure donation form
- Alternative ways to give
- Transparency information

### Contact Page (contact.html)
- Contact information
- Contact form
- Volunteer opportunities
- Partnership information
- FAQ section

## Technologies Used

### Backend
- **Flask**: Python web framework
- **Flask-SQLAlchemy**: Database ORM
- **Flask-Login**: User authentication
- **SQLite**: Database (can be upgraded to PostgreSQL for production)
- **Werkzeug**: Security and file handling

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS Grid and Flexbox
- **JavaScript (ES6+)**: Interactive functionality
- **Jinja2**: Template engine
- **Google Fonts**: Montserrat and Roboto typography

## Customization

### Colors
Main colors are defined as CSS variables in `style.css`:
```css
:root {
    --primary-color: #2e4669;
    --secondary-color: #4a7c59;
    --accent-color: #f4a261;
    --text-dark: #333333;
    --text-light: #666666;
    --bg-light: #f8f9fa;
}
```

### Images
All images are stored in the `assets/images/` directory. To update images:
1. Replace existing images with new ones
2. Maintain the same file names or update references in HTML files
3. Optimize images for web (recommended max 500KB per image)

### Content
Text content can be updated directly in the HTML files. Each page has clear section comments for easy navigation.

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/banyanbridge.git
   cd banyanbridge
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Access the application at `http://localhost:5000`

### Default Admin Credentials
- Username: `admin`
- Password: `admin123`

## Deployment

### Production Deployment
This Flask application can be deployed to various hosting services:
- **Heroku**: Easy Flask deployment with PostgreSQL
- **DigitalOcean**: VPS hosting with full control
- **AWS Elastic Beanstalk**: Scalable Flask deployment
- **PythonAnywhere**: Simple Python hosting

### Production Checklist
- Set `SECRET_KEY` environment variable
- Use PostgreSQL instead of SQLite
- Configure `SERVER_NAME` for your domain
- Use production WSGI server (Gunicorn)
- Set up SSL/HTTPS
- Configure file storage (AWS S3 for uploads)

## User Roles

### Admin
- Create and manage multiple-choice exams
- View all registered users
- Platform statistics and oversight
- Manage exam questions and settings

### Teacher
- Upload PDF teaching materials
- Organize materials by subject
- Manage course content
- Delete and update materials

### Student
- Browse and download teaching materials
- Upload assignment PDFs
- Take multiple-choice exams
- View exam results with detailed feedback
- Track assignment submission status

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Security Features

- Password hashing with Werkzeug
- Secure file upload validation
- Session management with Flask-Login
- CSRF protection
- Role-based access control
- File type and size validation

## Contact Information

For questions or updates about this platform:
- Email: info@banyanbridge.org
- Phone: +91 98765 43210
- Website: https://banyanbridge.org

## License

This platform is created for Banyan Bridge Foundation. All rights reserved.

## Credits

- Development: Flask educational platform
- Design: Modern responsive web design
- Images: Banyan Bridge Foundation
- Framework: Flask, SQLAlchemy, Flask-Login

---

**Note**: This is a comprehensive educational platform built with Flask. For production deployment, ensure proper security configurations and use a production database.