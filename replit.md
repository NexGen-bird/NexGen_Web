# NEXGEN Study Centre Web Application

## Overview

NEXGEN Study Centre is a web-based student management system for a study centre that provides courses for various competitive exams (CA/CS, JEE, HSC, NEET, UPSC, etc.). The application manages student admissions, subscriptions, transactions, and provides business analytics through a comprehensive dashboard. It's designed to replace a mobile application with a responsive web interface while maintaining all core functionality.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Bootstrap 5 with custom CSS for responsive design
- **Template Engine**: Jinja2 templates with Flask
- **UI Components**: Card-based layout with gradient themes matching the NEXGEN brand
- **JavaScript**: Vanilla JavaScript for form validation, animations, and interactive features
- **Design System**: Custom gradient color scheme (teal, lime green, pink) with consistent branding

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Application Structure**: Modular design with separate files for routes, models, forms, and utilities
- **Session Management**: Flask sessions for user authentication
- **Form Handling**: WTForms for form validation and rendering
- **Business Logic**: Utility functions for calculations, WhatsApp integration, and data formatting

### Data Storage Architecture
- **Primary Database**: SQLAlchemy ORM with SQLite (configurable to PostgreSQL via DATABASE_URL)
- **Schema Design**: Four main entities:
  - Users (authentication)
  - Customers (student information)
  - Transactions (payments and subscriptions)
  - Investment (partner investment tracking)
- **Data Relationships**: One-to-many relationships between customers and transactions

### Authentication and Authorization
- **Authentication Method**: Simple email/password authentication
- **Session Management**: Server-side sessions with Flask's built-in session handling
- **Password Security**: Werkzeug password hashing for secure password storage
- **Access Control**: Session-based route protection (redirects to login if not authenticated)

### Key Features and Business Logic
- **Student Management**: Complete admission workflow with form validation
- **Subscription Management**: Multiple plan types (Monthly, Quarterly, Half Yearly, Yearly) with shift-based scheduling
- **Financial Tracking**: Transaction recording with discount calculations and payment method tracking
- **Business Analytics**: Dashboard with key metrics (active members, expired subscriptions, P&L)
- **Communication Integration**: WhatsApp URL generation for receipts and reminders
- **Receipt Generation**: Printable receipts with branded templates

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web application framework
- **SQLAlchemy**: Database ORM and toolkit
- **WTForms**: Form handling and validation library
- **Werkzeug**: Password hashing and security utilities

### Frontend Dependencies
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome 6**: Icon library for UI elements
- **Custom CSS**: Brand-specific styling with gradient themes

### Communication Services
- **WhatsApp Business API**: Direct messaging integration for receipts and reminders (via wa.me links)
- **URL Generation**: Custom utility functions for creating shareable WhatsApp messages

### Database Configuration
- **Default Database**: SQLite for development (nexgen.db)
- **Production Database**: Configurable via DATABASE_URL environment variable (supports PostgreSQL)
- **Connection Pooling**: SQLAlchemy engine options with pool recycling and pre-ping enabled

### Deployment Dependencies
- **Environment Variables**: 
  - `SESSION_SECRET`: Flask session security key
  - `DATABASE_URL`: Database connection string
- **Static Assets**: Logo, CSS, and JavaScript files served via Flask's static file handling
- **Template System**: Jinja2 templating with base template inheritance