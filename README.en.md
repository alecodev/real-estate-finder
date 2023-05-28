# Real Estate Finder

***Languages***
- **🇺🇸 - English**
- [🇪🇸 - Español](./README.md)
---

This project seeks to create a real estate search engine with the objective of providing users with an efficient and user-friendly tool to find real estate that fit their needs and preferences.

With this search engine, users will be able to perform customized searches based on different criteria, such as location, property type, price, size and more.


## Technologies Used
- **Python** will be the primary programming language to develop the backend microservices. Also, I will be using the following packages and libraries: `unittest` for writing and running tests, `mysql-connector-python` for connecting to MySQL database, `Pydantic` for data validation and `Uvicorn` as the ASGI web server.
- **Docker** to facilitate the creation and deployment of microservices in an isolated environment.


## Development Approach
In this project, I will follow a Test-Driven Development (TDD) methodology. This means that I will start by creating unit tests that cover different aspects of the microservices, from the database connection to the expected response of the endpoints. I will adhere to the PEP8 coding style guide to maintain clean and readable code.

Additionally, I will consider conditions and information that should not be exposed in the endpoints, ensuring that I implement the corresponding methods to handle these cases.