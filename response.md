# Response
> The Current content is an **example template**; please edit it to fit your style and content.
## A. Required Information
### A.1. Requirement Completion Rate
- [o] List all pharmacies open at a specific time and on a day of the week if requested.
  - Implemented at `GET /pharmacies/open?day={Mon|Tue|...|Sun}&time=HH:mm` API.
- [o] List all masks sold by a given pharmacy, sorted by mask name or price.
  - Implemented at `GET /pharmacies/{pharmacy_name}/masks?sort_by={name|price}&order={asc|desc}` API.
- [o] List all pharmacies with more or less than x mask products within a price range.
  - Implemented at `GET /pharmacies/mask_count?min_price={float}&max_price={float}&count={int}&op={gt|lt}` API.
- [o] The top x users by total transaction amount of masks within a date range.
  - Implemented at `GET /users/top_users?top={int}&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` API.
- [o] The total number of masks and dollar value of transactions within a date range.
  - Implemented at `GET /transactions/summary?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` API.
- [o] Search for pharmacies or masks by name, ranked by relevance to the search term.
  - Implemented at `GET /search?keyword={str}` API.
- [o] Process a user purchases a mask from a pharmacy, and handle all relevant data changes in an atomic transaction.
  - Implemented at `POST /purchase` API.
### A.2. API Document
Please read the API documentation [here](api-document.md)

### A.3. Commands
Please run these commands.

```bash
# Create and activate a virtual environment
$ python3 -m venv venv
$ source venv/bin/activate # Linux/macOS

# Windows：
# venv\Scripts\activate

# Install required packages
$ pip install -r requirements.txt

# Import data into the database（ETL）
$ python3 -m app.etl

# Run the FastAPI application
$ uvicorn app.main:app --reload

```

## B. Bonus Information

>  If you completed the bonus requirements, please fill in your task below.
### B.1. Test Coverage Report
Make sure the database is initialized before running tests.
You can run the test script and check the test coverage report by using the command below:

```bash
$ coverage run --source=app -m pytest
$ coverage report 
$ coverage html                  # Output htmlcov visualization page
$ open htmlcov/index.html 
```

### B.2. Dockerized
Please check my [Dockerfile](Dockerfile) / [docker-compose.yml](docker-compose.yml).

On the local machine, please follow the commands below to build it.

```bash
$ docker-compose up --build
```

### B.3. Demo Site Url

The demo site is ready on [my demo site](https://phantom-mask-vpnk.onrender.com); you can try any APIs on this demo site.

## C. Other Information

### C.1. ERD

[My ERD](ERD.md).

### C.2. Technical Document
Please read the API documentation [here](api-document.md)

- --
