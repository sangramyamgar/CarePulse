# CarePulse — macOS + VS Code Setup Guide

Complete step-by-step guide to get CarePulse running on your Mac.

---

## Prerequisites (What You Need Installed)

### 1. Homebrew (macOS package manager)
```bash
# Check if installed
brew --version

# If not installed:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Python 3.10+
```bash
# Check version
python3 --version

# If not installed or too old:
brew install python@3.12
```

### 3. PostgreSQL 14+
```bash
# Install
brew install postgresql@14

# Start the service
brew services start postgresql@14

# Verify it's running
pg_isready
# Should show: "accepting connections"

# Create your user (if needed — Homebrew usually creates one matching your macOS username)
createuser -s postgres 2>/dev/null || true
```

### 4. Git
```bash
# Check
git --version

# If not installed:
brew install git
```

### 5. VS Code
Download from: https://code.visualstudio.com/

---

## VS Code Extensions to Install

Open VS Code → Extensions panel (Cmd+Shift+X) → Search and install:

| Extension | Why |
|-----------|-----|
| **Python** (Microsoft) | Syntax highlighting, IntelliSense, debugging |
| **Pylance** (Microsoft) | Fast Python language server |
| **SQLTools** | Browse and query your PostgreSQL database |
| **SQLTools PostgreSQL** | PostgreSQL driver for SQLTools |
| **GitLens** | See git history and blame inline |
| **Markdown Preview Enhanced** | Better markdown rendering |
| **GitHub Copilot** | AI code completion (if you have access) |

### Optional but helpful
| Extension | Why |
|-----------|-----|
| **Thunder Client** | Test API calls (if you ever add an API) |
| **indent-rainbow** | Visualize indentation (helpful for Python) |

---

## Step-by-Step: First-Time Setup

### Step 1: Open the project in VS Code
```bash
cd ~/Desktop/Projects/Kaiser
code .
```

### Step 2: Create and activate virtual environment
```bash
# Create
python3 -m venv .venv

# Activate
source .venv/bin/activate

# You should see (.venv) in your terminal prompt
```

### Step 3: Install Python dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set up environment file
```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials. Default works for most Homebrew installs:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=carepulse
DB_USER=postgres
DB_PASSWORD=postgres
```

**If you use your macOS username instead of "postgres":**
```
DB_USER=yourusername
DB_PASSWORD=
```

### Step 5: Create the database
```bash
createdb carepulse
```

If it says the database already exists, that's fine.

### Step 6: Run the ETL pipeline
```bash
python run_etl.py
```

You should see output like:
```
============================================================
  CarePulse — Full ETL Pipeline
============================================================

--- Creating Database Schema ---
  ✓ All tables created

[1/7] Generating 8 organizations...
       → 8 organizations saved
...
  ✓ Readmissions table: X rows, Y 30-day readmissions (Z%)

============================================================
  ✓ ETL Pipeline Complete!
============================================================
```

### Step 7: Run the tests
```bash
pytest tests/ -v
```

All tests should pass.

### Step 8: Launch the dashboard
```bash
streamlit run app/Home.py
```

Your browser should open to `http://localhost:8501`.

---

## Common Errors on macOS and Fixes

### Error: `psycopg2` fails to install
```
Error: pg_config executable not found
```
**Fix:**
```bash
brew install libpq
export PATH="/opt/homebrew/opt/libpq/bin:$PATH"
pip install psycopg2-binary
```

### Error: `connection refused` when running ETL
```
sqlalchemy.exc.OperationalError: could not connect to server
```
**Fix:** PostgreSQL isn't running.
```bash
brew services start postgresql@14
pg_isready  # Should say "accepting connections"
```

### Error: `FATAL: role "postgres" does not exist`
**Fix:** Create the role:
```bash
createuser -s postgres
```

Or edit `.env` to use your macOS username:
```
DB_USER=yourusername
DB_PASSWORD=
```

### Error: `FATAL: database "carepulse" does not exist`
**Fix:**
```bash
createdb carepulse
```

### Error: `ModuleNotFoundError: No module named 'src'`
**Fix:** You're in the wrong directory or venv isn't activated.
```bash
cd ~/Desktop/Projects/Kaiser
source .venv/bin/activate
```

### Error: `password authentication failed for user "postgres"`
**Fix:** Set a password for the postgres user:
```bash
psql -U $(whoami) -d postgres -c "ALTER USER postgres PASSWORD 'postgres';"
```

Or change your `.env` to match your actual credentials.

### Error: Streamlit page shows import errors
**Fix:** Make sure you run Streamlit from the project root:
```bash
cd ~/Desktop/Projects/Kaiser
streamlit run app/Home.py
```

### Error: `port 5432 already in use`
**Fix:** Another PostgreSQL instance is running:
```bash
brew services stop postgresql@14
brew services start postgresql@14
```

### Error: macOS asks about developer tools
**Fix:** Click "Install" when prompted. This installs Xcode command-line tools.

---

## How to Use Copilot/Claude in VS Code

### GitHub Copilot
1. Install the **GitHub Copilot** extension
2. Sign in with your GitHub account
3. Copilot will auto-suggest code as you type
4. Press **Tab** to accept a suggestion
5. Press **Esc** to dismiss

### Tips for using Copilot with this project
- Open a file you want to modify → Copilot understands context from the open file
- Write a comment describing what you want → Copilot generates the code
- Example: type `# Function to get average cost by payer` and Copilot writes it

### Copilot Chat / Claude
- Open the chat panel (Cmd+Shift+I for Copilot Chat)
- Ask questions like:
  - "Explain the readmission logic in transform.py"
  - "How does the LEAD window function work in readmission_flag.sql?"
  - "Add a new chart showing cost by payer to the Executive Overview page"
  - "Why is my database connection failing?"

### Best practices
- Always review AI-generated code before using it
- If the suggestion is wrong, give more context in your prompt
- Use it to learn, not just to copy — ask "why" after getting an answer

---

## Daily Workflow

When you sit down to work on the project:

```bash
# 1. Open terminal
cd ~/Desktop/Projects/Kaiser

# 2. Activate environment
source .venv/bin/activate

# 3. Make sure Postgres is running
pg_isready

# 4. Open VS Code
code .

# 5. If you changed data or ETL:
python run_etl.py

# 6. Run tests
pytest tests/ -v

# 7. Launch dashboard
streamlit run app/Home.py
```

### Stopping everything
```bash
# Stop Streamlit: Ctrl+C in the terminal
# Stop PostgreSQL (optional):
brew services stop postgresql@14

# Deactivate virtual environment:
deactivate
```

---

## Verifying Everything Works

Run this checklist:

- [ ] `python3 --version` → 3.10 or higher
- [ ] `pg_isready` → "accepting connections"
- [ ] `source .venv/bin/activate` → (.venv) appears in prompt
- [ ] `python -c "import pandas; print(pandas.__version__)"` → no error
- [ ] `python run_etl.py` → completes successfully
- [ ] `pytest tests/ -v` → all tests pass
- [ ] `streamlit run app/Home.py` → browser opens dashboard
