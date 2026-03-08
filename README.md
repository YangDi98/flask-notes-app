# Notes App (Flask)

A simple Flask-based application for creating and managing notes.  
Built as a practice project to explore backend development with Flask, including routing, templates, forms, and database integration.

---

## Getting Started
## Copy Environment File:
```
cp .env.sample .env
```
Edit `.env` and fill in your actual values
### Build and run project
```
docker-compose up --build
```
### Run migration
```
docker-compose exec web flask db upgrade
```

## Development
### Run tests
```
docker-compose exec web pytest
# Run specific test file
docker-compose exec web pytest tests/test_auth.py 
```
### Linting
We use flake8 and black for linting and formatting. Run:
```
./nt lint
```
if on windows
```
docker-compose exec web python notes-cli.py lint
```

### Add migration
1. Update models
```
docker-compose exec web flask db migrate -m "message"
```
```
docker-compose exec web flask db upgrade
```
### Add dependencies
```
docker-compose exec web poetry add <dependency>
```
## License
This project is for learning purposes.
