# TLB Kitchen API

> Custom Python Flask API for the TLB Kitchen bakery website, providing robust endpoints for product management, search functionality, and custom order processing.

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/mongodb-atlas-brightgreen.svg)](https://www.mongodb.com/cloud/atlas)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Features

- 🍰 Custom orders and pastries catalog management
- 🔍 Advanced search with MongoDB aggregation
- 📁 Category filtering and organization
- 📄 Pagination support
- 🔐 Secure MongoDB connection with environment variables
- 🌐 CORS-enabled for frontend integration
- ⚡ Optimized with lazy database connections
- 🚀 Ready for deployment on Render

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/tlb-kitchen-api.git

# Navigate to API directory
cd tlb-kitchen-api/api

# Install dependencies
pip install -r requirements.txt

# Create .env file with your MongoDB credentials
cp .env.example .env

# Run the API
python app.py
