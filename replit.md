# DAO Governance Explorer

## Overview

DAO Governance Explorer is a Flask-based web application that helps users discover and understand DAO (Decentralized Autonomous Organization) governance proposals from Snapshot.org. The application fetches proposal data via GraphQL API and generates plain-English summaries using OpenAI's GPT models to make complex governance proposals more accessible to users.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Flask with Jinja2 templating engine
- **Styling**: Bootstrap 5 with dark theme optimized for Replit
- **Icons**: Feather Icons for consistent iconography
- **Layout**: Responsive design with base template inheritance
- **JavaScript**: Vanilla JavaScript for client-side interactions including timestamp formatting, copy functionality, and smooth scrolling

### Backend Architecture
- **Web Framework**: Flask application with modular structure
- **Request Handling**: Form-based POST requests for DAO searches
- **Data Processing**: Proposal data fetching and AI summary generation pipeline
- **Error Handling**: Comprehensive logging and graceful error recovery with fallback messages
- **Session Management**: Flask sessions with configurable secret key

### Data Integration
- **External API**: Snapshot.org GraphQL API for fetching DAO proposals
- **Query Structure**: GraphQL queries to retrieve proposal metadata including title, body, voting data, and timestamps
- **Data Processing**: Real-time proposal data fetching with configurable limits

### AI Integration
- **Model**: OpenAI GPT-5 for proposal summarization
- **Processing**: Automatic generation of 2-3 sentence plain-English summaries
- **Fallback Strategy**: Graceful degradation when AI service is unavailable
- **Prompt Engineering**: Specialized prompts designed for DAO governance content

## External Dependencies

### Third-Party APIs
- **Snapshot.org GraphQL API**: Primary data source for DAO governance proposals
- **OpenAI API**: GPT-5 model for generating proposal summaries

### Libraries and Frameworks
- **Flask**: Web application framework
- **OpenAI Python SDK**: API client for OpenAI services
- **Requests**: HTTP library for external API calls
- **Bootstrap 5**: Frontend styling framework
- **Feather Icons**: Icon library for UI elements

### Environment Configuration
- **OPENAI_API_KEY**: Required for AI summary generation
- **SESSION_SECRET**: Flask session security (defaults to development key)

### Development Tools
- **Python Logging**: Comprehensive logging system for debugging and monitoring
- **Flask Debug Mode**: Development server with hot reloading