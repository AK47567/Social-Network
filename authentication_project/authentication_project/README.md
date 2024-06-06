# Django Social Network API

This project is a Django-based REST API for managing user signups, logins, friend requests, and searching users. It uses JWT for authentication.

## Features

- User Signup
- User Login
- JWT Authentication
- Sending Friend Requests
- Accepting Friend Requests
- Rejecting Friend Requests
- Searching Users
- Listing Friends

## Requirements

- Python 3.x
- Django 4.x
- djangorestframework
- djangorestframework-jwt
- Postgresql

## Setup

### 1. Clone the Repository


git clone https://github.com/AK47567/Social-Network.git
cd django-friends-management

### 2. Set up the Virtual Environment

python -m venv venv
.\venv\Scripts\activate

### 3. Install the dependencies

pip install -r requirements.txt

### 4. Run the Migrations

python manage.py makemigrations
python manage.py migrate

### 5. Create a superuser

python manage.py createsuperuser

### 4. Run the server

python manage.py runserver