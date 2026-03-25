# Poisoning Attack Detection — Windows Setup Guide

> Complete installation and launch instructions for **Windows 10 / Windows 11 (64-bit)**

---

## Table of Contents

- [Setup Overview](#setup-overview)
- [Step 1 — Verify System Requirements](#step-1--verify-system-requirements)
- [Step 2 — Install Python 3.11](#step-2--install-python-311)
- [Step 3 — Install MySQL via XAMPP](#step-3--install-mysql-via-xampp)
- [Step 4 — Extract & Inspect the Project](#step-4--extract--inspect-the-project)
- [Step 5 — Set Up a Virtual Environment & Install Packages](#step-5--set-up-a-virtual-environment--install-packages)
- [Step 6 — Create the MySQL Database](#step-6--create-the-mysql-database)
- [Step 7 — Import the SQL Schema](#step-7--import-the-sql-schema)
- [Step 8 — Configure Database Credentials in main.py](#step-8--configure-database-credentials-in-mainpy)
- [Step 9 — Create Runtime Directories](#step-9--create-runtime-directories)
- [Step 10 — Initialise Blockchain State Files](#step-10--initialise-blockchain-state-files)
- [Step 11 — Pre-Launch Verification Checklist](#step-11--pre-launch-verification-checklist)
- [Step 12 — Launch & Smoke Test](#step-12--launch--smoke-test)
- [Common Errors & Fixes](#common-errors--fixes)

---

## Setup Overview

| Step | What You Do | Est. Time |
|------|-------------|-----------|
| 1 | Check system requirements | 2 min |
| 2 | Install Python 3.11 | 5 min |
| 3 | Install XAMPP (MySQL) | 5–10 min |
| 4 | Extract the project ZIP | 1 min |
| 5 | Create virtual environment & install packages | 10–15 min |
| 6 | Create the MySQL database | 2 min |
| 7 | Import the SQL schema | 1 min |
| 8 | Edit DB credentials in main.py | 1 min |
| 9 | Create runtime directories | 1 min |
| 10 | Initialise blockchain state files | 1 min |
| 11 | Run the pre-launch checklist | 2 min |
| 12 | Launch the app & run smoke test | 5 min |

**Total first-time setup: approximately 35–45 minutes**

---

## Step 1 — Verify System Requirements

### Hardware

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 4 GB | 8 GB+ |
| Free Disk Space | 600 MB | 1 GB+ |
| OS | Windows 10 (64-bit) | Windows 11 (64-bit) |

### Check for Existing Software

Open **Command Prompt** (`Win + R` → type `cmd` → press Enter) and run:

```cmd
python --version
pip --version
mysql --version
```

- If all three return version numbers, skip Steps 2 and 3 and jump to **Step 4**.
- If any command shows `'...' is not recognized`, install the missing software in the relevant step below.

---

## Step 2 — Install Python 3.11

> Skip this step if `python --version` already returned **3.8 or higher**.

1. Open your browser and go to: `https://www.python.org/downloads/`
2. Download **Python 3.11** (recommended for best TensorFlow compatibility).
3. Run the downloaded `.exe` installer.
4. ⚠️ **Critical:** On the very first screen, tick **"Add Python to PATH"** before clicking **Install Now**.

   ![Add Python to PATH checkbox must be ticked]

5. Click **Install Now** and wait for completion.
6. Open a **new** Command Prompt window and verify:

```cmd
python --version
pip --version
```

Expected output:
```
Python 3.11.x
pip 23.x.x from C:\Users\YourName\AppData\Local\Programs\Python\Python311\lib\site-packages\pip
```

> If `python` is still not found after installation, reboot your PC and try again — PATH changes sometimes require a restart.

---

## Step 3 — Install MySQL via XAMPP

> Skip this step if `mysql --version` already returned a version number.

XAMPP is the easiest option — it bundles MySQL and phpMyAdmin together in a single graphical installer.

1. Go to: `https://www.apachefriends.org/`
2. Click **Download** for Windows.
3. Run the installer and accept all defaults (install to `C:\xampp`).
4. Once installed, open the **XAMPP Control Panel** (it opens automatically, or find it via the Start menu).
5. Click **Start** next to **Apache**.
6. Click **Start** next to **MySQL**.
7. Both should turn green and show **Running**.
8. Verify by visiting `http://localhost/phpmyadmin` in your browser — the phpMyAdmin dashboard should load.

> **XAMPP default credentials:** Username = `root`, Password = *(blank — leave empty)*.
> You will use `passwd=""` in `main.py` later.

---

## Step 4 — Extract & Inspect the Project

### Extract the ZIP File

1. Right-click `poisoning_attack.zip`.
2. Select **Extract All...**.
3. Choose a destination, e.g., `C:\Projects\`.
4. Click **Extract**.

### Open the Project Folder in Command Prompt

```cmd
cd C:\Projects\poisoning_attack-main
```

> All commands from this point forward must be run from inside `poisoning_attack-main\`.

### Confirm the Required Files Are Present

```cmd
dir
```

You must see the following in the output:

```
main.py
test.py
user.txt
database\
templates\
sample\
```

If any of these are missing, re-extract the ZIP — it may have been extracted into a nested subfolder.

---

## Step 5 — Set Up a Virtual Environment & Install Packages

### 5A — Create the Virtual Environment

A virtual environment keeps this project's packages separate from other Python projects on your machine.

```cmd
python -m venv venv
```

### 5B — Activate the Virtual Environment

```cmd
venv\Scripts\activate
```

Your Command Prompt prompt will change to show `(venv)` at the start:
```
(venv) C:\Projects\poisoning_attack-main>
```

> ⚠️ You must run this activation command every time you open a new Command Prompt window before running the app.

### 5C — Install All Required Packages

```cmd
pip install flask mysql-connector-python pillow opencv-python pandas numpy matplotlib tensorflow scikit-learn werkzeug
```

This downloads approximately 400–600 MB. Wait for it to complete fully before continuing.

> **If TensorFlow fails to install**, try the CPU-only version instead:
> ```cmd
> pip install tensorflow-cpu
> ```

### 5D — Verify the Key Packages

Run each line individually and confirm there are no errors:

```cmd
python -c "import flask; print('Flask:', flask.__version__)"
python -c "import tensorflow as tf; print('TensorFlow:', tf.__version__)"
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import mysql.connector; print('MySQL Connector: OK')"
python -c "from sklearn.metrics.pairwise import cosine_similarity; print('scikit-learn: OK')"
```

All five lines must print successfully. If any shows `ModuleNotFoundError`, reinstall that specific package:

```cmd
pip install <package-name>
```

---

## Step 6 — Create the MySQL Database

1. Open your browser and go to `http://localhost/phpmyadmin`.
2. Click **New** in the left-hand sidebar.
3. In the **Database name** field, type:
   ```
   poisoning_attack
   ```
4. Set the collation to `utf8_general_ci`.
5. Click **Create**.
6. Confirm that `poisoning_attack` now appears in the left panel.

---

## Step 7 — Import the SQL Schema

This step creates all the required tables and inserts the default admin account (`admin / admin`).

1. In phpMyAdmin, click **`poisoning_attack`** in the left panel to select it.
2. Click the **Import** tab at the top.
3. Click **Choose File** and navigate to:
   ```
   C:\Projects\poisoning_attack-main\database\poisoning_attack.sql
   ```
4. Leave all other settings at their defaults.
5. Click **Go**.
6. A **green success banner** will appear confirming the import.
7. The left panel will now show 6 tables under `poisoning_attack`:

```
pa_admin
pa_data
pa_label
pa_model
pa_trainer
pa_user
```

### Verify the Admin Account Was Seeded

Click **`pa_admin`** in the left panel → click the **Browse** tab. You should see:

| username | password |
|----------|----------|
| admin    | admin    |

---

## Step 8 — Configure Database Credentials in main.py

1. Open `main.py` in any text editor (Notepad, VS Code, Notepad++, etc.).
2. Find the following block near the top of the file (around line 33):

```python
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  charset="utf8",
  database="poisoning_attack"
)
```

3. Update only the fields relevant to your setup:

| Parameter | What to Set |
|-----------|-------------|
| `host` | Leave as `"localhost"` (XAMPP runs on the same machine) |
| `user` | Leave as `"root"` |
| `passwd` | Leave as `""` for XAMPP (no password by default) |
| `database` | Do **not** change this |

4. **Save the file.**

---

## Step 9 — Create Runtime Directories

These folders must exist before the server starts. They are **not included in the ZIP**.

Open Command Prompt, navigate to the project folder, and run:

```cmd
mkdir static\dataset
mkdir static\upload
mkdir static\temp
mkdir static\test
mkdir static\web\assets\js
```

Or, if you prefer PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path static\dataset, static\upload, static\temp, static\test, static\web\assets\js
```

### What Each Directory Is For

| Directory | Purpose |
|-----------|---------|
| `static\dataset\` | Permanent storage for all uploaded training images |
| `static\upload\` | Serves files via the app's download route |
| `static\temp\` | Temporary holding area during SHA-256 hash checking |
| `static\test\` | Stores images uploaded by end users for prediction |
| `static\web\assets\js\` | Contains `d1.txt` — the raw blockchain ledger file |

---

## Step 10 — Initialise Blockchain State Files

5 files must exist with the correct starting content before the first blockchain event fires.

Run the following commands one by one in Command Prompt:

```cmd
echo 1    > static\key.txt
echo.     > static\prehash.txt
echo.     > static\web\assets\js\d1.txt
echo {}   > static\modelchain.json
echo.     > static\wrong.txt
```

> **Note for PowerShell users** — use these commands instead:
> ```powershell
> Set-Content static\key.txt "1"
> Set-Content static\prehash.txt ""
> Set-Content static\web\assets\js\d1.txt ""
> Set-Content static\modelchain.json "{}"
> Set-Content static\wrong.txt ""
> ```

### What Each File Does

| File | Starting Value | Purpose |
|------|---------------|---------|
| `static\key.txt` | `1` | Block ID counter — increments with every new blockchain event |
| `static\prehash.txt` | *(empty)* | Stores the MD5 hash of the last block to form the chain link |
| `static\web\assets\js\d1.txt` | *(empty)* | The raw blockchain ledger — all events are appended here |
| `static\modelchain.json` | `{}` | JSON mirror of the blockchain used by the visual explorer |
| `static\wrong.txt` | *(empty)* | Stores filenames of images flagged during an attack |

---

## Step 11 — Pre-Launch Verification Checklist

Go through every item below before starting the server. Any unchecked box is likely to cause a crash or error on startup.

```
══════════════════════════════════════════════════════════════
  PRE-LAUNCH CHECKLIST — WINDOWS
══════════════════════════════════════════════════════════════

  PYTHON ENVIRONMENT
  [ ] python --version returns 3.8 or higher
  [ ] Command prompt shows (venv) prefix  ← venv is active
  [ ] All 5 package verification commands passed (Step 5D)

  MYSQL / XAMPP
  [ ] XAMPP Control Panel is open
  [ ] Apache is showing green "Running" status
  [ ] MySQL is showing green "Running" status
  [ ] http://localhost/phpmyadmin loads in browser
  [ ] 'poisoning_attack' database is visible in left panel
  [ ] All 6 tables are visible under poisoning_attack
  [ ] pa_admin contains the row: admin | admin

  APPLICATION CONFIGURATION
  [ ] main.py — passwd="" (or your MySQL password if set)
  [ ] main.py — host="localhost"

  RUNTIME DIRECTORIES (must all exist under static\)
  [ ] static\dataset\
  [ ] static\upload\
  [ ] static\temp\
  [ ] static\test\
  [ ] static\web\assets\js\

  BLOCKCHAIN STATE FILES (must all exist)
  [ ] static\key.txt              → contains the number 1
  [ ] static\prehash.txt          → file exists (may be empty)
  [ ] static\web\assets\js\d1.txt → file exists (may be empty)
  [ ] static\modelchain.json      → contains {}
  [ ] static\wrong.txt            → file exists (may be empty)

══════════════════════════════════════════════════════════════
```

### Quick Verification Command (Command Prompt)

```cmd
type static\key.txt
type static\modelchain.json
dir static\dataset static\upload static\temp static\test static\web\assets\js
```

All five directories should appear in the listing with no errors.

---

## Step 12 — Launch & Smoke Test

### Start the Server

Make sure your virtual environment is active (prompt shows `(venv)`), then run:

```cmd
python main.py
```

### Expected Terminal Output

```
 * Serving Flask app 'main'
 * Debug mode: on
WARNING: This is a development server.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
```

Open **http://localhost:5000** in your browser.

> **If port 5000 is already in use** (this is common on some Windows setups), open `main.py`, find the very last line, and change the port number:
> ```python
> app.run(debug=True, host='0.0.0.0', port=8080)
> ```
> Then visit `http://localhost:8080` instead.

### 5 Smoke Tests

Run these checks in order to confirm the entire stack is working:

**Test 1 — Home page loads**
Visit `http://localhost:5000` → The landing page with three login options should appear. ✅

**Test 2 — Admin login (confirms database connection)**
Go to `/login` → enter `admin` / `admin` → you should be redirected to the Admin dashboard. ✅
- "logged in fail" → schema not imported correctly → redo Step 7
- HTTP 500 error → database connection failed → check `passwd=` in `main.py`

**Test 3 — Trainer registration**
Go to `/reg_trainer` → fill in the form → submit → a success message should appear. ✅

**Test 4 — Trainer login**
Go to `/login_trainer` → log in with the trainer account just created → you should reach the Trainer dashboard. ✅

**Test 5 — Blockchain writes**
Log in as admin → create a model at `/admin` → go to `/view_block?act=11` → at least one entry should be visible. ✅

All 5 tests passing confirms your full stack — Python, Flask, MySQL, and the blockchain logger — is operational.

> **To stop the server:** Press `Ctrl + C` in the Command Prompt window.

---

## Common Errors & Fixes

| Error Message | Cause | Fix |
|---------------|-------|-----|
| `'python' is not recognized` | Python not added to PATH | Reinstall Python and tick "Add Python to PATH" |
| `Access denied for user 'root'@'localhost'` | Wrong MySQL password in main.py | Set `passwd=""` in main.py (XAMPP default has no password) |
| `Unknown database 'poisoning_attack'` | Database not created | Redo Step 6 |
| `ModuleNotFoundError: No module named 'flask'` | Packages not installed or venv not active | Run `venv\Scripts\activate` then re-run pip install |
| `FileNotFoundError: static/key.txt` | Blockchain files not initialised | Redo Step 10 |
| `500 Internal Server Error` on image upload | `static\temp` or `static\dataset` folder missing | Redo Step 9 |
| `Address already in use: 5000` | Port 5000 is busy (another app using it) | Change port to `8080` in the last line of main.py |
| `Can't connect to MySQL server` | XAMPP MySQL is not running | Open XAMPP Control Panel → click Start next to MySQL |
| `TensorFlow install fails` | Python version incompatibility | Run `pip install tensorflow-cpu` instead |
| Trainer cannot log in | Account was eliminated (2+ violations) | Expected behaviour — create a new trainer account |
| Blockchain viewer is blank | d1.txt is missing or malformed | Re-run: `echo. > static\web\assets\js\d1.txt` and `echo 1 > static\key.txt` |
| Images not appearing after upload | `static\upload\` folder missing | Run `mkdir static\upload` |
