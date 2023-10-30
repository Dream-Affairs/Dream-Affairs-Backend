# Dream Affairs API Documentation

Welcome to the official Dream Affairs API documentation, the driving force behind our wedding website generator. Our API harness the power of Python, FastAPI, SQLAlchemy, PostgreSQL, and more to effortlessly create stunning wedding websites. In this documentation, you'll discover how to make the most of the API, explore endpoints and responses, learn how to contribute, and find acknowledgments for those who've been a part of this journey.

## Table of Contents

- [1. Introduction](#introduction)
- [2. Features](#features)
- [3. Technologies Used](#technologies-used)
- [4. Getting Started](#getting-started)
  - [4.1 Prerequisites](#prerequisites)
     - [4.1.1 Clone The Repository](#clone-the-repository)
     - [4.1.2 Install Dependencies](#install-the-dependencies)
     - [4.1.3 Configure Environment Variables](#configure-environment-variables)
  - [4.2 Usage](#usage)
- [5. API Endpoints](#5-api-endpoints)
  - [5.1 Shop](#51-shop)
  - [5.2 Product](#52-product)
  - [5.3 Health](#53-health)
  - [5.4 Test](#54-test)
  - [5.5 Logs](#55-logs)
  - [5.6 Notifications](#56-notifications)
- [6. Database Schema](#database-schema)
- [7. Authentication](#authentication)
- [8. Error Handling](#error-handling)
- [9. Testing](#testing)
- [10. Deployment](#deployment)
- [11. Contributing](#contributing)
   -[11.1 Commit Convention](#commit-convention)
- [12. License](#license)
- [13. Acknowledgments](#acknowledgments)


## 1. Getting Started

### Prerequisites
Before getting started, ensure you have Python and the necessary dependencies installed on your system. You can find a list of required dependencies in the 'Requirements' section.

#### 1.1 Clone The Repository

To get started with the local development environment, clone the repository:

```bash
$ git clone https://github.com/hngx-org/spitfire-super-admin-one.git
$ cd super_admin_1
```

#### 1.2 Setup Virtual Environment and Install Dependencies

You can set up the environment using either `virtualenv`, `pipenv` or any other virtual environment management tool of your choice.
Here are instructions for both:

Using `virtualenv`:

```bash
# Install virtualenv
pip install virtualenv

# Create virtual environment
virtualenv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies in requirement.txt
pip install -r requirements.txt
```

Using `pipenv`:

```bash
# Install pipenv
pip install pipenv

# Create virtual environment
pipenv --python 3.10

# Activate the virtual environment
pipenv shell

# Install dependencies in requirements.txt or pipfile
pipenv install
```

#### 1.3 Configure Environment Variables

Make sure to set the following environment variables:

    SECRET_KEY: [Your Secret Key]
    SQLALCHEMY_DATABASE_URI: [Your Database URI]

### 1.2 Usage

Now you have everything setup, you can run the app using the command:
```bash
python3 main.py
```
if you have `make` installed, to use the `Makefile` run:
```bash
make run
```

## 2. API Endpoints



## Testing

**Note:** ensure you are connected to the internet before running tests and are in `spitfire-events` directory

```bash
# install test suite and HTTP requests library
$ pip install requests pytest

cd super_admin_1
$ pytest tests\* -v
```

## Contributing


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Appreciation and acknowledgments to contributors, libraries, or resources that helped in developing the API.
