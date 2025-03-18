# Test-Driven Development with FastAPI

This project is designed to practice Test-Driven Development. It uses Docker Compose to launch the whole backend stack, so please make sure that [Docker](https://www.docker.com/) is installed.

## Goals

- [x] Develop an asynchronous RESTful API with FastAPI and async ORM
- [x] Use Makefile for task automation and environment management
- [x] Implement Test-Driven Development (TDD) practice
- [x] Test the FastAPI application with Pytest
- [x] Run unit and integration tests with code coverage tracking
- [x] Use Ruff and Pre-commit hooks for code linting and formatting checks
- [x] Automate testing with Tox
- [x] Use Poetry to manage python packages
- [x] Handle database migrations with Alembic
- [x] Dockerize FastAPI, PostgreSQL and Redis for containerized deployment
- [x] Design the email service with the Strategy Pattern for scalable email generation and delivery

## Deployment

### Setup

Refer to the `.env.example` file for the required variables. It is recommended to use [direnv](https://github.com/direnv/direnv) for managing environment variables.

### Running the Backend Service

To start the whole stack, run:
	
```
$ make up
```

To take down the stack, run:

```
$ make down
```

To view logs for a specific service, use `logs-{service}`. You can also customize the number of log lines to display with the `log_lines` argument:
	
```
$ make logs-api log_lines=50
```

Swagger UI is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). You can use it to test the API endpoints and explore the API documentation.

## Running Tests

To run the tests:

```
$ make test
```
