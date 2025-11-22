## Summary
Migrated to postgres db and use docker-compose for my project.

## Take-away
- Do not put secrets directly in docker-compose yaml, or exclude from .dockerignore, should use 
```
env_file:
      - .env  # Loaded at runtime, not built into image
```
- Can use init-db.sql for initial script for db, for example create test.db
- Connection in postgresql must be made to a db, there is no connection to server.

## Future Considerations
- Currently all my files are bind mounted to volume (including .env) which means anyone has the container can access those secrets. This is fine as long as this is for local development and I do not push .env to github. For future dev and prod environment, revisit this. 