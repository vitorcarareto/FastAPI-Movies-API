# Movie Rental

## API documentation

https://vitor-movie-api.herokuapp.com/docs

## Postman Collection

[![Run in Postman](https://run.pstmn.io/button.svg)](https://app.getpostman.com/run-collection/45b45472fe0c33a1c333?action=collection%2Fimport)

# Instructions for running locally

## Starting PostgreSQL database

SQL scripts (create tables and initial inserts) are executed automatically on container startup for the first time, from the `database_scripts/` directory.

```sh
docker compose up -d db
```

## Starting the app

```sh
docker compose up app
```
