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
### Add/Update Translation
Extract strings
```
docker-compose exec web pybabel extract -F babel.cfg -o messages.pot .
```
If Update Existing Translations
```
docker-compose exec web pybabel update -i messages.pot -d translations
```
If add new translations
```
docker-compose exec web pybabel init -i messages.pot -d translations -l <language_code>
```
Note language code has to match what flask babel normalize to

Compile Translations (After modifying .po files as needed)

```
docker-compose exec web pybabel compile -d translations
```
## License
This project is for learning purposes.
