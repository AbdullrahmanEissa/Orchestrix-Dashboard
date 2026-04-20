# Orchestrix Dashboard

Orchestrix Dashboard is a lightweight server orchestration monitoring app with three components:

- `agent`: collects Linux host metrics, system logs, and Docker container logs.
- `backend`: FastAPI service that stores metrics in PostgreSQL and pushes live updates over WebSocket.
- `frontend`: React + Vite dashboard for real-time visualization.

## Suggested app name

I suggest naming this project **Orchestrix Dashboard**.

## Stack

- Frontend: React, Recharts, Vite
- Backend: FastAPI, SQLAlchemy
- Database: PostgreSQL
- Cache/Message layer: Redis
- Runtime: Docker Compose

## Project structure

```text
.
├── agent/
│   └── agent.py
├── backend/
│   ├── Dockerfile
│   ├── database.py
│   ├── main.py
│   └── models.py
├── frontend/
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   └── src/
│       ├── App.css
│       ├── App.jsx
│       └── main.jsx
└── docker-compose.yml
```

## Run with Docker

From the project root:

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:3000`
- Backend docs: `http://localhost:3000/docs`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## Notes

- `GET /` on backend returns `404` by default, which is expected.
- Frontend dashboard may show no cards until data arrives from the agent.
- In `agent/agent.py`, set `BACKEND_URL` to your backend endpoint when running agent on another host.

## Useful commands

```bash
docker compose ps
docker compose logs -f backend frontend
docker compose down
```

## License

This project is licensed under the GNU General Public License v3.0. See `LICENSE`.
