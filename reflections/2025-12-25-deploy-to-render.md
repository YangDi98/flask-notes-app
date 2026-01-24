## Summary
Deployed my app on render

## Take-away
- Use multi-stage dockerfile to satisfy requirements of different environments, for example, having dev dependencies locally but not on prod.
- Use gunicore, not flask run for prod.

## Future considerations
- Run migrations safely

- Test full CRUD routes locally


- Optional: Auto-migrations in Dockerfile

    For first deploy, you can temporarily add flask db upgrade && gunicorn …

    Then remove after tables exist

- Lock .env separation

    Keep local DB in .env.local

    Keep prod DB in .env.prod

    Never commit .env

- Check performance and logs on Render

    Access https://flask-notes-app-s8kt.onrender.com/

    Ensure requests succeed and logs show expected SQL queries- 