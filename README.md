# Cloud Security System 🔒
live link: https://cloud-security-system.onrender.com/ <br>

A dynamic, real-time cloud security and threat detection system designed for monitoring, logging, and alerting on potential security breaches. This system currently demonstrates **Brute Force Attack Detection** with a high-performance web dashboard that receives alerts instantaneously via WebSockets.

## 🚀 Features

- **Real-time Threat Dashboard**: A responsive, live-updating frontend built with Bootstrap and Socket.IO.
- **Brute Force Detection Intelligence**: The backend maintains in-memory tracking of failed authentication events. If An IP address fails login 5 times within 5 minutes, a HIGH severity alert is generated.
- **WebSocket Alerting System**: Instead of relying on slow, resource-heavy polling, the backend pushes alerts directly to connected admin clients using seamless bidirectional communication (`Flask-SocketIO`).
- **Incident Management**: View all historical security events, filter alerts by severity, and mark active alerts as `RESOLVED`.
- **Infrastructure as Code (IaC)**: Includes a `render.yaml` and `Dockerfile` for instantaneous 1-click cloud deployment.
- **Self-Healing SQLite Database**: Database tables and required directories (`data/`, `logs/`) execute automatically on startup, making it perfect for containerized and ephemeral environments.

---

## 🏗️ Architecture

The application operates fundamentally split into two components:

1. **Backend (Python / Flask)**
   - Exposes RESTful API endpoints for interaction (`/api/login`, `/api/alerts`, `/api/events`, `/api/health`).
   - Integrates `Flask-SocketIO` for low-latency live pushes to connected frontends.
   - Stores logs and records in an `SQLite` database (`data/security.db`), tracking all login attempts and triggered alerts.
   - Uses `gunicorn` with an `eventlet` worker as its production-grade Web Server Gateway Interface (WSGI).
   
2. **Frontend (HTML5 / Vanilla JS / Bootstrap 5)**
   - Contains a pure uncompiled frontend served statically by the Flask application.
   - Leverages native `fetch` requests for performing manual tests and loading historical data.
   - Instantiates a Socket.IO client that listens for `new_alert` emissions to dynamically update the DOM array without refreshing the page.

---

## 💻 Running the Application Locally

### Method 1: Docker Compose (Recommended)

Because the project includes a `docker-compose.yml`, spinning up the whole environment is trivial:

```bash
# Start the container stack in detached mode
docker-compose up -d --build
```

The web dashboard securely runs at `http://localhost:5000`. Stop the environment with `docker-compose down`.

### Method 2: Python Virtual Environment

If you prefer to run it without Docker:

```bash
# 1. Navigate into the backend directory
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the application using development server
python app.py
```

---

## 🧪 Testing the Security Engine 

To ensure the security engine is operating correctly, we've provided multiple ways to simulate an attack against the application's login pathways.

**Option A: Automated Attack Script**
There is a provided script `test_attack.py` inside the root directory. Run it while the local server is operating:
```bash
python test_attack.py
```
This script acts as an adversary. It will sequentially fire 8 incorrect passwords directly at the API. Once the detection engine notices the threshold is passed, the CLI script will print a generated alert payload.

**Option B: Dashboard Test Suite**
Navigate to the web dashboard (`http://localhost:5000`) and select the **🧪 Test Attack** tab.
- Click **"Start Brute Force Simulation"** to automate rapid failed logins natively in the browser.
- Watch the **Live Alerts** tab simultaneously update without page reloads.

---

## ☁️ Deploying to Render (Cloud Hosting)

The project is already perfectly optimized for production deployment on Render.

We have included a Blueprint configuration file (`render.yaml`).

### Deployment Steps:
1. Ensure this entire project codebase is pushed to your GitHub or GitLab repository.
2. Sign in to your [Render Dashboard](https://dashboard.render.com/).
3. Click the **"New +"** button and select **"Blueprint"**.
4. Grant Render access to your repository. 
5. Render will automatically read the `render.yaml` file, provision a free web service, attach your `Dockerfile`, build the container, inject randomized Secure keys, and run it using Gunicorn.

**Note on Free Tier Ephemeral Data:** 
If you host this using Render's *Free Tier*, note that Render spins down inactive instances, and the local disk is wiped. Upon waking back up, the system's `init_db()` dynamically resets the SQLite structure. All old alerts are cleared to save space. For production scenarios, consider upgrading to a paid instance or utilizing a managed PostgreSQL database.
