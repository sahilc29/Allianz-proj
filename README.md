# Introduction
The `docker-compose.yml` file provides access to `Feddit` which is a fake reddit API built to complete the Allianz challenge. 

# How-to-run
1. Please make sure you have docker installed.
2. To run `Feddit` API locally in the terminal, replace `<path-to-docker-compose.yml>` by the actual path of the given `docker-compose.yml` file in `docker compose -f <path-to-docker-compose.yml> up -d`. It should be available in [http://0.0.0.0:8080](http://0.0.0.0:8080). 
3. To stop `Feddit` API in the terminal,  replace `<path-to-docker-compose.yml>` by the actual path of the given `docker-compose.yml` file in `docker compose -f <path-to-docker-compose.yml> down`.

# API Specification
Please visit either [http://0.0.0.0:8080/docs](http://0.0.0.0:8080/docs) or [http://0.0.0.0:8080/redoc](http://0.0.0.0:8080/redoc) for the documentation of available endpoints and examples of the responses.
There are 3 subfeddits available. For each subfeddit there are more than 20,000 comments, that is why we use pagination in the JSON response with the following parameters:

+ `skip` which is the number of comments to be skipped for each query
+ `limit` which is the max returned number of comments in a JSON response.

# Overview :
The API is a microservice designed to manage comments on different subfeddits (analogous to Reddit's subreddits) and provide sentiment analysis on these comments. Users can retrieve recent comments from specific subfeddits, along with sentiment analysis to determine if the comments are positive or negative.

# Key Features :
1. Retrieve Recent Comments:
+ Endpoint: /subfeddit/{subfeddit_name}/comments
+ Function: Returns the most recent comments for a specific subfeddit.
+ Parameters:
    + subfeddit_name (required): The name of the subfeddit.
    + limit (optional, default: 25): The maximum number of comments to return.
    + start_time and end_time (optional): Filters comments by a specific time range. (The time range available to filter results is from 01-05-2024 00:00:00 to 31-05-2024 23:59:59)
    + sort_by_polarity (optional, default: False): Sorts comments by polarity score if true.

2. Sentiment Analysis:
Each comment includes a polarity score and a classification (positive or negative) based on the sentiment analysis.
3. Subfeddit Listing:
+ Endpoint: /subfeddits/
+ Function: Lists all available subfeddits.
4. Health Check:
+ Endpoints: /api/v1/version, /db-conn
+ Function: Provides the current status of the API and checks the database connection.

# Technical Details :
Backend: FastAPI, a modern web framework for building APIs with Python 3.7+.Database: PostgreSQL is used to store the comments and subfeddits data.ORM: SQLAlchemy for database interactions.

# Sentiment Analysis: 
VADER SentimentIntensityAnalyzer, which is effective for analyzing social media text.Testing: Pytest for unit and integration tests to ensure the reliability of the API.

# GitHub Workflow :
The GitHub workflow is configured to run linting checks and tests automatically whenever changes are pushed to the repository. This ensures code quality and functionality are maintained consistently.

# Data Schemas
## Comment

+ **id**: unique identifier of the comment.
+ **username**: user who made/wrote the comment.
+ **text**: content of the comment in free text format.
+ **created_at**: timestamp in unix epoch time indicating when the comment was made/wrote.
+ **subfeddit_id**

## Subfeddit
+ **id**: unique identifier of the subfeddit
+ **username**: user who started the subfeddit.
+ **title**: topic of the subfeddit.
+ **description**: short description of the subfeddit.
+ **comments**: comments under the subfeddit.

