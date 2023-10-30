# Dream Affairs API Documentation

## Introduction
Welcome to the official Dream Affairs API documentation, the driving force behind our wedding website generator. Our API harness the power of Python, FastAPI, SQLAlchemy, PostgreSQL, and more to effortlessly create stunning wedding websites. In this documentation, you'll discover how to make the most of the API, explore endpoints and responses, learn how to contribute, and find acknowledgments for those who've been a part of this journey.

## Getting Started
Let's start this adventure with the setup:

### Prerequisites
Make sure you have these prerequisites installed on your system:

- Python (recommended version 3.6 or higher)
- pip (Python package manager)

### Installation and Usage
Follow these steps to set up and run the endpoint locally:

 1. **Clone this repository to your local machine.**

    ```bash
    git clone https://github.com/Dream-Affairs/Dream-Affairs-Backend
    cd Dream-Affairs-Backend
    ```

 2. **Setup Virtual Environment and Install Dependencies.**

    You can set up the environment using either `virtualenv`, `pipenv` or any other virtual environment management tool of your choice.
    Here are instructions for both:

    **Using `virtualenv`:**

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

    **Using `pipenv`:**

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

 3. **Configure Environment Variables:**
    Copy the env.sample file to .env and set values for each of the environment variables.
    ```bash
    cp env.sample .env
    ```

 4. **Run the App:**

    Now you have everything setup, you can run the app using python:
    ```bash
    python3 main.py
    ```

    or using unicorn:
    ```bash
    uvicorn main:app --port="8000"
    ```

    if you have `make` installed, to use the `Makefile` run:
    ```bash
    make run
    ```

 6. **Ta-da! Your endpoint is now accessible locally at http://localhost:8000/.**

## Deployment

The API has been deployed, and it's now globally accessible! You can access the swagger documentation to access detailed documentation of every endpoint, its request format and response model.
- [Production URL](#)
- [Development URL](#)

## Testing

To test your API, we've set up a flexible approach that allows you to seamlessly switch between local and remote testing with ease. Make sure you're in the `Dream-Affairs` directory.

 1. **Set up Environment Variable:**
    You can use an environment variable to specify the API URL you want to test. By default, it's set to the local development server.
    - For local testing:
      ```bash
      export API_URL='http://localhost:5000'
      ```
    - For remote testing:
      ```bash
      export API_URL='#'
      ```
 2. **Install pytest:**
    ```bash
    pip install pytest
    ```
 3. **Run Tests:**
    You can now run tests based on the environment variable you've set. For local testing, you don't need to set the environment variable as it defaults to the local server. Also ensure you hsve the API running locally. For remote testing, ensure you're connected to the internet.
    ```bash
    pytest app/tests/*
    ```

## Contributing:

Contributions are welcome from all Backend developers building the Dream Affairs application. You can:
- Submit a bug report or feature request
- Help us write documentation
- Fix a bug or implement a new feature
- Review code and help us improve

Ready to jump in? Take a look at our [CONTRIBUTION.md](CONTRIBUTION.md) to get started!

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
Appreciation and acknowledgments to contributors, libraries, or resources that helped in developing the API.
