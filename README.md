# Online Coding Judge (Mini LeetCode)

A simplified coding judge built with Python (Flask). This repo contains backend APIs, a simple judge engine for Python, SQL schema, and sample data.

## Features
- User registration & (simple) login
- Create/list problems and test-cases
- Submit Python code and get evaluation (AC/Wrong/TimeLimit/RuntimeError)
- Store submissions & results in SQLite

## Tech Stack
- Python + Flask
- SQLAlchemy (SQLite by default)
- Passlib for password hashing

## Quickstart
1. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. Initialize DB & sample data
```bash
python db_init.py
```
3. Run the app
```bash
python app.py
```
4. Use HTTP client (Postman/curl) to interact with endpoints (/register, /login, /problems, /submit)

## Security Notes (IMPORTANT)
- The included judge runs untrusted code on the host: **this is not safe for production**.
- For production, run each submission inside an isolated container (Docker) or use system-level sandboxing (gVisor, Firecracker).
- Add authentication (JWT), input sanitization, rate limiting, and strict resource limits.

## Project Structure
```
online-coding-judge/
├─ app.py
├─ models.py
├─ judge.py
├─ db_init.py
├─ requirements.txt
├─ README.md
```

## Extending
- Add support for multiple languages using Docker-based runners.
- Move judge to a worker queue (Celery + Redis) for async execution.
- Add user profiles, badges, and improved leaderboard logic.

## License
MIT
