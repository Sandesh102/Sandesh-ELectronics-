# E-commerce Website

A modern e-commerce platform built with Django, featuring user authentication, product management, and shopping cart functionality.

## Features

- User Authentication
  - Registration and Login
  - Password Reset
  - User Profile Management
- Product Management
  - Product Listing
  - Product Details
  - Product Categories
- Shopping Cart
  - Add/Remove Items
  - Update Quantities
  - Checkout Process
- Responsive Design
  - Mobile-friendly interface
  - Bootstrap 5 styling

## Tech Stack

- **Backend**: Django 5.2
- **Frontend**: 
  - HTML5
  - CSS3
  - Bootstrap 5
  - JavaScript
- **Database**: SQLite
- **Authentication**: Django's built-in authentication system
- **Image Handling**: Pillow

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ecommerce-website.git
cd ecommerce-website
```

2. Create and activate a virtual environment:
```bash
python -m venv myenv
# On Windows
myenv\Scripts\activate
# On macOS/Linux
source myenv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Create a superuser (admin):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Access the website at `http://127.0.0.1:8000/`

## Project Structure

```
ecommerce-website/
├── ecommerce/              # Main project settings
├── products/              # Products app
├── users/                 # Users app
├── media/                 # User uploaded files
├── static/                # Static files
├── templates/             # Base templates
├── manage.py             # Django management script
└── requirements.txt      # Project dependencies
```

## Configuration

1. Email Settings (for password reset):
   Add the following to your `settings.py`:
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'your-smtp-server'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = 'your-email@example.com'
   EMAIL_HOST_PASSWORD = 'your-email-password'
   ```

2. Media Files:
   - Create a `media` directory in your project root
   - Configure `MEDIA_ROOT` and `MEDIA_URL` in settings.py

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Django Documentation
- Bootstrap 5
- Font Awesome Icons

## Support

For support, email your-email@example.com or open an issue in the repository.
