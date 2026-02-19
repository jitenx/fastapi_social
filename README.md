
```markdown
# 🚀 Social

> A full-stack social platform built with FastAPI and Streamlit, supporting JWT authentication and flexible database configuration (SQLite & PostgreSQL).

---

## 📌 Overview

**Social** is a modern full-stack web application built using:

- ⚡ FastAPI (Backend API)
- 🎨 Streamlit (Frontend UI)
- 🗄 SQLite / PostgreSQL (Database)
- 🔐 JWT Authentication
- 🔄 Alembic (Database Migrations)
- 🚀 Render (Deployment)
- 📦 uv (Dependency & Runtime Manager)

The project demonstrates clean architecture, environment-based configuration, authentication, and full-stack integration.

---

## 🌍 Live Deployment

🔗 **Production URL:**  
https://jitenxmedia.onrender.com

---

## 🛠 Tech Stack

| Layer        | Technology |
|-------------|------------|
| Backend     | FastAPI |
| Frontend    | Streamlit |
| Database    | SQLite / PostgreSQL |
| Auth        | JWT (HS256) |
| Migrations  | Alembic |
| Deployment  | Render |
| Runtime     | uv |

---

## 🏗 Architecture

```

Streamlit (Frontend)
↓
FastAPI (REST API)
↓
Database (SQLite / PostgreSQL)

```

- Streamlit handles UI & user interactions
- FastAPI handles authentication & API logic
- Database stores users & posts
- JWT secures protected endpoints

---

## 📂 Project Structure

```

.
├── app/
│   ├── app.py                # FastAPI main app
│   ├── models.py             # Database models
│   ├── schemas.py            # Pydantic schemas
│   ├── database.py           # Database connection
│   ├── configsettings.py     # Pydantic settings / environment
│   └── routes/               # API route modules
│
├── streamlit_app/
│   └── app.py                # Streamlit frontend
│
├── alembic/                  # Database migration files
├── requirements.txt          # Python dependencies
├── Makefile                  # Commands to run backend/frontend
└── README.md                 # Project documentation

```

---

## ⚙️ Environment Configuration

The application uses **Pydantic Settings** for environment management.

Create a `.env` file for local development:

```

DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=social
DATABASE_USERNAME=jitu
DATABASE_PASSWORD=jitu
ALGORITHM=HS256
SECRET_KEY=hgsfdhfjh455gdjhjgjsd
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_COM=sqlite
API_BASE_URL=[http://127.0.0.1:8000](http://127.0.0.1:8000)

```

### Production (Render)

Set the same variables inside:

```

Render Dashboard → Environment → Environment Variables

```

---

## 🗄 Database Support

The project supports two database modes:

### 🟢 SQLite (Local Development)

```

DATABASE_COM=sqlite

```

### 🔵 PostgreSQL (Production Recommended)

```

DATABASE_COM=postgresql

````

Database switching is controlled via environment variables.

---

## 🔐 Authentication System

- JWT-based authentication
- Algorithm: **HS256**
- Configurable token expiration
- Protected routes require Bearer Token
- Token stored and reused by frontend

---

## 🚀 Running the Project Locally

This project uses a **Makefile** for easier development.

---

### 1️⃣ Install Dependencies & Run Migrations

```bash
make migrate
````

---

### 2️⃣ Run Full Application (Backend + Frontend)

```bash
make run
```

After running:

* 🔹 FastAPI → [http://0.0.0.0:8000](http://0.0.0.0:8000)
* 🔹 Streamlit → [http://localhost:8501](http://localhost:8501)

---

## 🔥 Available Make Commands

| Command          | Description                                    |
| ---------------- | ---------------------------------------------- |
| `make run`       | Run both FastAPI + Streamlit                   |
| `make fastapi`   | Run only FastAPI                               |
| `make streamlit` | Run only Streamlit                             |
| `make stop`      | Stop all running services                      |
| `make migrate`   | Install dependencies & run database migrations |

---

## 📜 Makefile

```makefile
.PHONY: run fastapi streamlit stop migrate

FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
STREAMLIT_PORT=8501

migrate:
	@echo "Installing depenecies from requirements.txt"
	@uv add -r requirements.txt
	@echo "🗄️  Running database migrations..."
	@uv run alembic upgrade head

run: migrate
	@echo "🚀 Starting FastAPI..."
	@uv run uvicorn app.app:app --host $(FASTAPI_HOST) --port $(FASTAPI_PORT) --reload & \
	echo $$! > .fastapi.pid
	@echo "🌟 Starting Streamlit..."
	@uv run streamlit run streamlit_app/app.py --server.port $(STREAMLIT_PORT) & \
	echo $$! > .streamlit.pid
	@echo ""
	@echo "✅ Services started!"
	@echo "FastAPI: http://$(FASTAPI_HOST):$(FASTAPI_PORT)"
	@echo "Streamlit: http://localhost:$(STREAMLIT_PORT)"
	@echo ""
	@echo "ℹ️  Use 'make stop' to stop both services."
	@echo ""
	@wait

fastapi: migrate
	@echo "🚀 Starting FastAPI only..."
	@uv run uvicorn app.app:app --host $(FASTAPI_HOST) --port $(FASTAPI_PORT) --reload

streamlit:
	@echo "🌟 Starting Streamlit only..."
	@uv run streamlit run streamlit_app/app.py --server.port $(STREAMLIT_PORT)

stop:
	@echo "🛑 Stopping FastAPI..."
	@kill $$(cat .fastapi.pid) 2>/dev/null || true
	@echo "🛑 Stopping Streamlit..."
	@kill $$(cat .streamlit.pid) 2>/dev/null || true
	@pkill -f "streamlit.web.cli" || true
	@rm -f .fastapi.pid .streamlit.pid
	@echo "✅ All services stopped."
```

---

## 🧪 API Endpoints (Example)

| Method | Endpoint  | Description             |
| ------ | --------- | ----------------------- |
| POST   | /login    | User login              |
| POST   | /register | User registration       |
| GET    | /users    | Get users (Protected)   |
| POST   | /posts    | Create post (Protected) |

---

## 🧠 Key Features

* ✅ Clean architecture
* ✅ Environment-based configuration
* ✅ JWT authentication
* ✅ SQLite & PostgreSQL support
* ✅ Alembic migrations
* ✅ Full-stack integration
* ✅ Makefile-based development workflow
* ✅ Production deployment on Render

---

## 📈 Future Improvements

* Like & comment system
* User profile management
* Role-based access control
* Docker containerization
* CI/CD integration
* Android / Flutter mobile client

---

## 👨‍💻 Author

**Jiten**

---

## ⭐ If You Like This Project

Give it a ⭐ on GitHub and feel free to fork or contribute.

```
