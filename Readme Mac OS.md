# Poisoning Attack Detection in Federated Learning
### A Blockchain-Secured Web Application for Detecting Label-Flipping Attacks

---

## Table of Contents

- [What Is This Project?](#what-is-this-project)
- [The Problem It Solves](#the-problem-it-solves)
- [How the System Works — Big Picture](#how-the-system-works--big-picture)
- [Key Concepts Explained](#key-concepts-explained)
- [Project Structure](#project-structure)
- [User Roles & What Each Can Do](#user-roles--what-each-can-do)
- [Database Design](#database-design)
- [Technology Stack](#technology-stack)
- [Overall Setup Process](#overall-setup-process)
  - [Setup at a Glance](#setup-at-a-glance)
  - [Phase 1 — System Requirements Check](#phase-1--system-requirements-check)
  - [Phase 2 — Extract & Inspect the Project](#phase-2--extract--inspect-the-project)
  - [Phase 3 — Python Environment Setup](#phase-3--python-environment-setup)
  - [Phase 4 — MySQL Database Setup](#phase-4--mysql-database-setup)
  - [Phase 5 — Configure the Application](#phase-5--configure-the-application)
  - [Phase 6 — Create Runtime Directories](#phase-6--create-runtime-directories)
  - [Phase 7 — Initialise Blockchain State Files](#phase-7--initialise-blockchain-state-files)
  - [Phase 8 — Verify Everything Before Launch](#phase-8--verify-everything-before-launch)
  - [Phase 9 — Launch the Application](#phase-9--launch-the-application)
  - [Phase 10 — First-Run Smoke Test](#phase-10--first-run-smoke-test)
- [Navigating the Application](#navigating-the-application)
- [Complete Workflow Walkthrough](#complete-workflow-walkthrough)
- [Attack Detection — Deep Dive](#attack-detection--deep-dive)
- [SPFL Algorithm — Deep Dive](#spfl-algorithm--deep-dive)
- [Blockchain Logging — Deep Dive](#blockchain-logging--deep-dive)
- [Sample Datasets Included](#sample-datasets-included)
- [Default Credentials](#default-credentials)
- [Common Issues & Fixes](#common-issues--fixes)

---

## What Is This Project?

This is a **research-grade, full-stack web application** built with Python and Flask that demonstrates two things simultaneously:

1. **How a poisoning attack works** — specifically a *label-flipping attack*, where a malicious participant in a machine learning pipeline deliberately mislabels training data to corrupt a model.
2. **How to detect and stop it** — using image hash integrity checking, a cosine-similarity-based filtering algorithm (called SPFL), and a blockchain-backed audit trail that records every single action taken in the system.

The application is designed to mimic a real-world **Federated Learning** environment where multiple independent trainers contribute data to train a shared AI model — but some of those trainers may be adversaries.

---

## The Problem It Solves

### What is Federated Learning?
Federated Learning is a machine learning approach where a global model is trained across many participants (called "clients" or "trainers") without sharing raw data. Each trainer trains locally on their own data and sends only model updates to a central server, which aggregates them.

### What is a Poisoning Attack?
Because the central server cannot directly inspect each trainer's data, a malicious trainer can **poison** the model by:
- Uploading images with **deliberately wrong labels** (e.g., labelling a crow as a sparrow)
- This is known as a **Label-Flipping Attack**
- Over time, this corrupts the global model so it makes wrong predictions

### Why Is This Hard to Detect?
The poisoned data *looks* legitimate — it's real images with real labels. There's no obvious signature of malice, which is why special detection algorithms are needed.

### What This Project Does About It
This system uses **three layers of defense**:
1. **SHA-256 Hash Checking** — Every image is fingerprinted. If the same image appears under a different label, it's instantly flagged.
2. **SPFL Cosine Similarity Filtering** — Model weight updates from trainers are compared mathematically. Outliers (likely attackers) are excluded from the global model.
3. **Blockchain Immutable Logging** — Every event — including attacks — is permanently recorded with a hash chain, making it impossible to tamper with the history.

---

## How the System Works — Big Picture

```
                        ┌─────────────────────────────────────────────────────┐
                        │              FLASK WEB APPLICATION                  │
                        │                                                     │
  ┌──────────┐          │  ┌───────────────┐    ┌────────────────────────┐   │
  │  ADMIN   │──────────┼─►│ Model Manager │    │  Blockchain Logger     │   │
  └──────────┘  Creates │  │ • Create model│    │  • MD5 hash chain      │   │
                models  │  │ • Add labels  │    │  • Records all events  │   │
                        │  │ • Upload data │    │  • Tamper-evident log  │   │
  ┌──────────┐          │  └───────┬───────┘    └────────────────────────┘   │
  │ TRAINER  │──────────┼─►        │                                         │
  └──────────┘  Uploads │  ┌───────▼───────────────────────────────────┐    │
                images  │  │         ATTACK DETECTION ENGINE            │    │
                        │  │                                            │    │
                        │  │  Step 1: SHA-256 hash the uploaded image   │    │
                        │  │  Step 2: Look up hash in database          │    │
                        │  │  Step 3a: Hash found, same label → OK ✓   │    │
                        │  │  Step 3b: Hash found, diff label → ATTACK  │    │
                        │  │  Step 4: Log attack to blockchain          │    │
                        │  │  Step 5: Penalise / eliminate trainer      │    │
                        │  └───────────────────────┬───────────────────┘    │
  ┌──────────┐          │                          │                         │
  │   USER   │──────────┼─►  Hash lookup of test   │                         │
  └──────────┘  Queries │   image → predicted label│                         │
                model   │                          ▼                         │
                        │              ┌───────────────────┐                 │
                        │              │   MySQL Database   │                 │
                        │              └───────────────────┘                 │
                        └─────────────────────────────────────────────────────┘
```

---

## Key Concepts Explained

### SHA-256 Image Hashing
Every image uploaded into the system is run through the **SHA-256 cryptographic hash function**, which produces a unique 64-character fingerprint of that file's contents. Even a single pixel change produces a completely different hash. This means:
- Two identical images will always produce the same hash
- If the same image is uploaded under a different label, the system recognises the duplicate and flags it as a label-flipping attack

### Label-Flipping Attack
A trainer uploads `crow.jpg` (hash: `abc123`) under the label `sparrow`. The system checks the database — `abc123` already exists under label `crow` in model `BirdsNet`. This is an attack. The system logs it, displays the wrong image to the trainer, and increments their violation score.

### SPFL — Self-Purified Federated Learning
When the global model is being assembled from trainer contributions, SPFL acts as a filter:
- It trains a small local model for each client
- Extracts the model's weight vector
- Computes the **cosine similarity** between each trainer's weight vector and the group average
- Trainers whose updates deviate significantly (similarity < 0.85) are considered malicious
- Only "benign" updates are averaged into the global model

### Blockchain Audit Trail
Every significant event is recorded as a "block" containing:
- A sequential ID
- The event data (who did what, when, with which file)
- An MD5 hash of the event data
- The hash of the previous block (creating the "chain")

This means if anyone tries to edit a past record, all subsequent hashes become invalid — tampering is immediately detectable.

---

## Project Structure

```
poisoning_attack-main/
│
├── main.py                      # ← The entire backend: all Flask routes, ML logic,
│                                #   blockchain functions, attack detection
│
├── test.py                      # ← Standalone utility: reads images from a folder
│                                #   and saves them as a .pkl file for model use
│
├── user.txt                     # ← Simple text file that stores the currently
│                                #   logged-in trainer's username (session bridge)
│
├── database/
│   └── poisoning_attack.sql     # ← MySQL schema: creates all 5 tables and inserts
│                                #   the default admin account (admin/admin)
│
├── templates/
│   │
│   ├── index.html               # ← Public landing page with links to all login types
│   ├── login.html               # ← Admin login form
│   ├── login_trainer.html       # ← Trainer login form
│   ├── login_user.html          # ← User login form
│   ├── register.html            # ← New user self-registration form
│   ├── reg_trainer.html         # ← New trainer self-registration form
│   │
│   └── web/                     # ← Authenticated pages (require login)
│       ├── admin.html           # ← Admin dashboard: create models, upload base data
│       ├── admin2.html          # ← Admin: add class labels to an existing model
│       ├── admin3.html          # ← Admin: upload training images per label
│       ├── tr_home.html         # ← Trainer: main upload page (attack detection here)
│       ├── tr_home2.html        # ← Trainer: browse their own uploaded data
│       ├── tr_home3.html        # ← Trainer: review and submit data for training
│       ├── tr_home4.html        # ← Trainer: view flagged images after attack detected
│       ├── userhome.html        # ← User: upload image, receive predicted label
│       └── view_block.html      # ← Blockchain viewer: full audit log with colour coding
│
└── sample/
    ├── BirdsNet.pkl             # ← Pre-trained pickle model: bird species classification
    ├── WildNet.pkl              # ← Pre-trained pickle model: wildlife classification
    ├── CrimeNet.pkl             # ← Pre-trained pickle model: crime/face recognition
    │
    ├── BirdsNet/                # ← Sample training images for the Birds model
    │   ├── Crow/                #   4 crow images
    │   ├── king fisher/         #   4 kingfisher images
    │   ├── peacock/             #   4 peacock images
    │   └── sparrow/             #   5 sparrow images
    │
    ├── WildNet/                 # ← Sample training images for the Wildlife model
    │   ├── beer/                #   6 images
    │   ├── cow/                 #   8 images
    │   ├── elephant/            #   7 images
    │   └── horse/               #   5 images
    │
    └── c1.jpg, c2.jpg, c3.jpg  # ← Generic test images for user prediction
```

> **Note on `static/` directory:** The application also requires a `static/` folder (not included in the zip) that holds runtime files — uploaded datasets, temporary files, blockchain text files, and the JSON audit log. You must create this manually before running. See Installation Step 5.

---

## User Roles & What Each Can Do

### Admin
The admin is the system owner and controls the model registry.

| Task | Route | Description |
|------|-------|-------------|
| Login | `/login` | Authenticate with username/password |
| Create Model | `/admin` | Register a new ML model name and upload a base dataset ZIP |
| Add Labels | `/admin2?mid=X` | Define the class labels (categories) for a model |
| Upload Images | `/admin3?mid=X&bid=Y` | Upload training images for a specific label |
| View Blockchain | `/view_block?act=11` | See the full colour-coded audit trail |

### Model Trainer
Trainers contribute labelled training images to grow the dataset.

| Task | Route | Description |
|------|-------|-------------|
| Register | `/reg_trainer` | Create an account |
| Login | `/login_trainer` | Authenticate |
| Upload Images | `/tr_home` | Select a model, enter a label, upload images (attack detection runs here) |
| View My Data | `/tr_home2` | Browse images previously uploaded, grouped by model and label |
| Submit for Training | `/tr_home3` | Review pending data and mark it as ready for training |
| View Warnings | `/tr_home4` | See which images were flagged and what penalty was applied |
| Logout | `/logout` | End session |

**Trainer Penalty System:**
- **First offence** (`dstatus = 1`): Warning shown, flagged images listed
- **Second offence** (`dstatus = 2`): Trainer is permanently **eliminated** — they can no longer log in. An elimination event is logged to the blockchain.

### End User
Users interact with the trained model to get predictions.

| Task | Route | Description |
|------|-------|-------------|
| Register | `/register` | Create a user account |
| Login | `/login_user` | Authenticate |
| Predict | `/userhome` | Upload an image — system computes hash and looks up the label |
| Logout | `/logout` | End session |

> The prediction system currently works by **hash-based lookup** rather than neural network inference — meaning it matches the uploaded image to a known training image and returns its label. This is by design, as the focus of the project is data integrity and attack detection rather than model inference.

---

## Database Design

The MySQL database `poisoning_attack` contains 5 tables:

### `pa_admin`
Stores admin login credentials.

| Column | Type | Description |
|--------|------|-------------|
| username | VARCHAR(20) | Admin username |
| password | VARCHAR(20) | Admin password (plaintext) |

### `pa_trainer`
Stores registered model trainer accounts.

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| name | VARCHAR | Full name |
| mobile | BIGINT | Phone number |
| email | VARCHAR | Email address |
| location | VARCHAR | Geographic location |
| uname | VARCHAR | Login username |
| pass | VARCHAR | Password |
| create_date | VARCHAR | Registration date |
| status | INT | Account status |
| dstatus | INT | **Violation count** (0=clean, 1=warned, 2+=eliminated) |

### `pa_user`
Stores registered end-user accounts (same structure as trainer, without `dstatus`).

### `pa_model`
Stores ML model records created by the admin.

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| model | VARCHAR | Model name (e.g., BirdsNet) |
| model_file | VARCHAR | Uploaded model file name |

### `pa_label`
Stores the class labels defined for each model.

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| mid | INT | Foreign key to pa_model |
| label_name | VARCHAR | Label/class name (e.g., Crow) |
| uname | VARCHAR | Who created this label |

### `pa_data`
The central table — stores every uploaded training image with its integrity hash.

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| mid | INT | Foreign key to pa_model |
| bid | INT | Foreign key to pa_label |
| image_file | VARCHAR | Saved filename |
| model | VARCHAR | Model name (denormalised for quick lookup) |
| label_name | VARCHAR | Label name (denormalised) |
| hash1 | VARCHAR(100) | **SHA-256 hash of the image file** |
| uname | VARCHAR | Uploader's username |
| status | INT | Training status (0=pending, 1=submitted) |

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Web Framework | **Flask** (Python) | Routing, sessions, form handling, template rendering |
| Database | **MySQL** + `mysql-connector-python` | Persistent storage of all users, models, images, labels |
| Image Processing | **OpenCV** (`cv2`), **Pillow** | Reading, resizing, and handling image files |
| Deep Learning | **TensorFlow / Keras** | Building and training the federated model (Sequential Dense layers) |
| ML Utilities | **scikit-learn** | Cosine similarity computation for SPFL filtering |
| Data Science | **NumPy**, **Pandas**, **Matplotlib** | Array operations, data handling, optional visualisation |
| Integrity Hashing | **hashlib** (SHA-256) | Image fingerprinting for label-flip detection |
| Blockchain Hashing | **hashlib** (MD5) | Block content hashing for the audit chain |
| Template Engine | **Jinja2** | Dynamic HTML generation |
| File Handling | **Werkzeug** `secure_filename` | Safe upload filename sanitisation |
| Model Serialisation | **Pickle** | Saving and loading pre-trained models |

---

## Overall Setup Process

This section is your complete, end-to-end guide to getting the project running from a fresh machine. Follow every phase in order — skipping any single phase is the most common cause of startup failures.

---

### Setup at a Glance

```
┌──────────────────────────────────────────────────────────────────────┐
│                     COMPLETE SETUP FLOW                              │
├─────────┬───────────────────────────────────────┬────────────────────┤
│  Phase  │  What You Do                          │  Estimated Time    │
├─────────┼───────────────────────────────────────┼────────────────────┤
│    1    │  Verify system requirements           │  2 min             │
│    2    │  Install Python                       │  5 min             │
│    3    │  Install MySQL / XAMPP                │  5–10 min          │
│    4    │  Extract & inspect the project        │  1 min             │
│    5    │  Install Python packages              │  5–15 min          │
│    6    │  Create MySQL database                │  2 min             │
│    7    │  Import the SQL schema                │  1 min             │
│    8    │  Configure DB credentials in main.py  │  1 min             │
│    9    │  Create runtime directories           │  1 min             │
│   10    │  Initialise blockchain state files    │  1 min             │
│   11    │  Pre-launch verification checklist    │  2 min             │
│   12    │  Launch the app & smoke test          │  5 min             │
└─────────┴───────────────────────────────────────┴────────────────────┘

Total first-time setup: approximately 30–40 minutes
```

---

### Phase 1 — Verify System Requirements

Before installing anything, confirm your machine meets the minimum requirements.

**Hardware:**

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 4 GB | 8 GB+ (TensorFlow needs headroom) |
| Disk space | 600 MB free | 1 GB+ |
| OS | Windows 10, macOS 11, Ubuntu 20.04 | Any 64-bit OS |

**Software — check if already installed:**

```bash
python --version        # Need 3.8 or higher
pip --version           # Should be bundled with Python
mysql --version         # Need 5.7 or 8.x
```

If any of these commands fail with "not found", proceed to Phase 2 or 3 to install them. If all three succeed, skip to Phase 4.

---

### Phase 2 — Install Python

Skip this phase if `python --version` already returned 3.8 or higher.

#### Windows

1. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download **Python 3.11** (recommended — best TensorFlow compatibility)
3. Run the installer
4. ⚠️ **On the very first installer screen**, tick **"Add Python to PATH"** before clicking Install Now
5. After install, open **Command Prompt** and verify:

```cmd
python --version
pip --version
```

Expected:
```
Python 3.11.x
pip 23.x.x from C:\Users\...\Scripts\pip
```

#### Linux (Ubuntu / Debian)

```bash
sudo apt update
sudo apt install python3.11 python3-pip python3.11-venv -y
python3 --version
```

#### macOS

```bash
# Using Homebrew (https://brew.sh)
brew install python@3.11
python3 --version
```

> Avoid Python 3.12+ unless you substitute `tensorflow-cpu` for `tensorflow` during package installation.

---

### Phase 3 — Install MySQL

Skip this phase if `mysql --version` already returned a version number.

**XAMPP is strongly recommended for beginners** — it bundles MySQL + phpMyAdmin in a single installer with a graphical control panel.

#### Option A — XAMPP (Easiest, Recommended for Beginners)

1. Download XAMPP from [https://www.apachefriends.org/](https://www.apachefriends.org/) — choose your OS
2. Install it (accept all defaults)
3. Open the **XAMPP Control Panel**
4. Click **Start** next to both **Apache** and **MySQL**
5. Both should show green "Running" status
6. Visit `http://localhost/phpmyadmin` to confirm phpMyAdmin loads

> **XAMPP default credentials:** username `root`, password is **blank**. Leave `passwd=""` in `main.py`.

#### Option B — Standalone MySQL Server

**Windows:**
1. Download from [https://dev.mysql.com/downloads/installer/](https://dev.mysql.com/downloads/installer/)
2. Choose **Developer Default** setup
3. Set a root password during the wizard — note it down
4. Verify: `mysql -u root -p` → you should see the `mysql>` prompt

**Linux:**
```bash
sudo apt install mysql-server -y
sudo systemctl start mysql
sudo systemctl enable mysql
sudo mysql_secure_installation    # Set root password here
```

**macOS:**
```bash
brew install mysql
brew services start mysql
mysql_secure_installation
```

---

### Phase 4 — Extract & Inspect the Project

#### Extract the ZIP

**Windows:** Right-click `poisoning_attack.zip` → **Extract All** → choose a destination (e.g., `C:\Projects\`)

**Linux / macOS:**
```bash
unzip poisoning_attack.zip
```

#### Navigate Into the Project Folder

**Windows:**
```cmd
cd C:\Projects\poisoning_attack-main
```

**Linux / macOS:**
```bash
cd poisoning_attack-main
```

> All commands from this point must be run from inside `poisoning_attack-main/`.

#### Confirm the Expected Files Are Present

```bash
# Linux / macOS
ls

# Windows
dir
```

You must see: `main.py`, `test.py`, `user.txt`, `database/`, `templates/`, `sample/`

---

### Phase 5 — Install Python Packages

#### Step 5A — (Recommended) Create a Virtual Environment

A virtual environment isolates this project's packages, preventing conflicts with other Python projects.

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Your prompt will show `(venv)` at the start, confirming the environment is active.

> ⚠️ If you use a virtual environment, run the activate command every time you open a new terminal before running `python main.py`.

#### Step 5B — Install All Required Packages

```bash
pip install flask \
            mysql-connector-python \
            pillow \
            opencv-python \
            pandas \
            numpy \
            matplotlib \
            tensorflow \
            scikit-learn \
            werkzeug
```

This downloads approximately 400–600 MB. Wait for full completion.

**Platform-specific alternatives:**

```bash
# Python 3.12+ (TensorFlow may fail):
pip install tensorflow-cpu

# Apple Silicon Mac (M1/M2/M3):
pip install tensorflow-macos tensorflow-metal

# Linux permission error:
pip install --user flask mysql-connector-python ...
```

#### Step 5C — Verify Key Packages

```bash
python -c "import flask; print('Flask:', flask.__version__)"
python -c "import tensorflow as tf; print('TensorFlow:', tf.__version__)"
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import mysql.connector; print('MySQL Connector: OK')"
python -c "from sklearn.metrics.pairwise import cosine_similarity; print('scikit-learn: OK')"
```

All five should print without errors. If any shows `ModuleNotFoundError`, re-install that package: `pip install <package-name>`.

---

### Phase 6 — Create the MySQL Database

#### Using phpMyAdmin (XAMPP users)

1. Go to `http://localhost/phpmyadmin`
2. Click **New** in the left sidebar
3. Database name: `poisoning_attack`, collation: `utf8_general_ci`
4. Click **Create**
5. Confirm `poisoning_attack` appears in the left panel

#### Using MySQL Command Line

```bash
mysql -u root -p
```

```sql
CREATE DATABASE poisoning_attack CHARACTER SET utf8 COLLATE utf8_general_ci;
SHOW DATABASES;    -- confirm it appears
EXIT;
```

---

### Phase 7 — Import the SQL Schema

This creates all 6 tables and seeds the admin account (`admin / admin`).

#### Using phpMyAdmin

1. Click **`poisoning_attack`** in the left panel
2. Click the **Import** tab → **Choose File** → select `database/poisoning_attack.sql`
3. Leave defaults → click **Go**
4. ✅ Green success banner confirms completion
5. All 6 tables now appear in the left panel: `pa_admin`, `pa_data`, `pa_label`, `pa_model`, `pa_trainer`, `pa_user`

#### Using MySQL Command Line

```bash
mysql -u root -p poisoning_attack < database/poisoning_attack.sql
```

Verify:
```bash
mysql -u root -p -e "USE poisoning_attack; SHOW TABLES; SELECT * FROM pa_admin;"
```

Expected:
```
+-----------------------------+
| Tables_in_poisoning_attack  |
+-----------------------------+
| pa_admin                    |
| pa_data                     |
| pa_label                    |
| pa_model                    |
| pa_trainer                  |
| pa_user                     |
+-----------------------------+

+----------+----------+
| username | password |
+----------+----------+
| admin    | admin    |
+----------+----------+
```

---

### Phase 8 — Configure the Application

Open `main.py` in any text editor. Find this block near the top (around line 33):

```python
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  charset="utf8",
  database="poisoning_attack"
)
```

Update only what's needed for your setup:

| Parameter | What to Change |
|-----------|---------------|
| `host` | Leave as `"localhost"` unless MySQL is on a different machine |
| `user` | Leave as `"root"` unless you created a different MySQL user |
| `passwd` | **Set to your MySQL root password. Leave as `""` for XAMPP default.** |
| `database` | Do not change |

Examples:
```python
# XAMPP default (no password):
passwd=""

# MySQL with password:
passwd="yourpassword123"

# MySQL on another machine:
host="192.168.1.50"
passwd="yourpassword123"
```

Save the file.

---

### Phase 9 — Create Runtime Directories

These subdirectories under `static/` must exist before the server starts. They are **not in the zip**.

#### Linux / macOS

```bash
mkdir -p static/dataset static/upload static/temp static/test static/web/assets/js
```

#### Windows (Command Prompt)

```cmd
mkdir static\dataset
mkdir static\upload
mkdir static\temp
mkdir static\test
mkdir static\web\assets\js
```

#### Windows (PowerShell)

```powershell
New-Item -ItemType Directory -Force -Path static\dataset, static\upload, static\temp, static\test, static\web\assets\js
```

**What each directory is for:**

| Directory | Purpose |
|-----------|---------|
| `static/dataset/` | Permanent storage of all training images, organised as `static/dataset/<ModelName>/<file>` |
| `static/upload/` | Serves files via the `/down` download route |
| `static/temp/` | Trainer images are saved here first while SHA-256 hash check runs, then moved to `dataset/` or deleted |
| `static/test/` | Images uploaded by end users for prediction |
| `static/web/assets/js/` | Contains `d1.txt` — the raw blockchain ledger |

---

### Phase 10 — Initialise Blockchain State Files

5 files must exist with the correct starting content before the first blockchain event fires.

#### Linux / macOS

```bash
echo "1"  > static/key.txt
echo ""   > static/prehash.txt
echo ""   > static/web/assets/js/d1.txt
echo "{}" > static/modelchain.json
echo ""   > static/wrong.txt
```

#### Windows (Command Prompt)

```cmd
echo 1    > static\key.txt
echo.     > static\prehash.txt
echo.     > static\web\assets\js\d1.txt
echo {}   > static\modelchain.json
echo.     > static\wrong.txt
```

#### Windows (PowerShell)

```powershell
Set-Content static\key.txt "1"
Set-Content static\prehash.txt ""
Set-Content static\web\assets\js\d1.txt ""
Set-Content static\modelchain.json "{}"
Set-Content static\wrong.txt ""
```

**What each file does:**

| File | Initial Value | Role |
|------|--------------|------|
| `static/key.txt` | `1` | Counter for the next block ID — increments with every blockchain event |
| `static/prehash.txt` | *(empty)* | Stores the MD5 hash of the last written block, used as `previous_hash` in the next block to form the chain |
| `static/web/assets/js/d1.txt` | *(empty)* | The raw blockchain ledger. Events appended as `<id>##<md5>##<data>##<timestamp>`, blocks separated by `#|`. Read by the `/view_block` page |
| `static/modelchain.json` | `{}` | JSON mirror of the blockchain — used by the visual blockchain explorer in the admin UI |
| `static/wrong.txt` | *(empty)* | When an attack is detected, flagged image filenames are written here so the trainer warning page (`/tr_home4`) can display them |

---

### Phase 11 — Pre-Launch Verification Checklist

Run through every item below before starting the server. Any unchecked box is a potential crash.

```
══════════════════════════════════════════════════════════════
  PRE-LAUNCH CHECKLIST
══════════════════════════════════════════════════════════════

  ENVIRONMENT
  [ ] python --version returns 3.8 or higher
  [ ] All 5 package verification commands passed (Phase 5C)
  [ ] If using venv: prompt shows (venv) prefix

  DATABASE
  [ ] MySQL is running
        XAMPP → green "Running" next to MySQL
        Linux → sudo systemctl status mysql → active (running)
        Windows → net start MySQL80
  [ ] 'poisoning_attack' database exists
  [ ] All 6 tables present in the database
  [ ] pa_admin contains: admin | admin

  APPLICATION CONFIG
  [ ] main.py passwd= matches your MySQL password
  [ ] main.py host= is correct

  RUNTIME DIRECTORIES (must all exist)
  [ ] static/dataset/
  [ ] static/upload/
  [ ] static/temp/
  [ ] static/test/
  [ ] static/web/assets/js/

  BLOCKCHAIN FILES (must all exist)
  [ ] static/key.txt              → contains "1"
  [ ] static/prehash.txt          → file exists
  [ ] static/web/assets/js/d1.txt → file exists
  [ ] static/modelchain.json      → contains "{}"
  [ ] static/wrong.txt            → file exists

══════════════════════════════════════════════════════════════
```

Quick shell verification of the directory and file structure:

```bash
# Linux / macOS — verify all at once
echo "=== key.txt ===" && cat static/key.txt
echo "=== modelchain.json ===" && cat static/modelchain.json
echo "=== Directories ===" && ls -d static/dataset static/upload static/temp static/test static/web/assets/js
echo "=== Blockchain files ===" && ls static/prehash.txt static/wrong.txt static/web/assets/js/d1.txt
```

---

### Phase 12 — Launch the Application & Smoke Test

#### Start the Server

```bash
# Activate venv if you created one:
# Windows:   venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

python main.py
```

**Expected terminal output:**
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

> **Port 5000 in use?** (common on macOS Monterey+ due to AirPlay)
> Edit the last line of `main.py`: `app.run(debug=True, host='0.0.0.0', port=8080)`
> Then visit `http://localhost:8080`

**Startup error reference:**

| Error Message | Cause | Fix |
|---------------|-------|-----|
| `Access denied for user 'root'@'localhost'` | Wrong MySQL password | Update `passwd=` in `main.py` |
| `Unknown database 'poisoning_attack'` | DB not created | Re-run Phase 6 |
| `FileNotFoundError: static/key.txt` | Blockchain files missing | Re-run Phase 10 |
| `Address already in use: 5000` | Port 5000 is busy | Change port to 8080 in `main.py` |
| `ModuleNotFoundError: No module named 'flask'` | Packages not installed or venv not active | Install packages or activate venv |
| `Can't connect to MySQL server` | MySQL service not running | Start XAMPP MySQL or `sudo systemctl start mysql` |

#### First-Run Smoke Test (5 checks)

**Test 1 — Home page loads**
→ Visit `http://localhost:5000` → landing page with three login options appears ✅

**Test 2 — Admin login (confirms DB connection)**
→ Visit `/login` → enter `admin / admin` → redirected to Admin dashboard ✅
If it says "logged in fail": schema not imported → re-run Phase 7
If 500 error: DB connection failed → check `passwd=` in `main.py`

**Test 3 — Trainer registration**
→ Visit `/reg_trainer` → fill in form → submit → success message appears ✅

**Test 4 — Trainer login**
→ Visit `/login_trainer` → log in with trainer just registered → redirected to Trainer dashboard ✅

**Test 5 — Blockchain writes**
→ Logged in as admin → create a model at `/admin` → visit `/view_block?act=11` → at least one entry appears ✅

All 5 passing means your full stack is operational. Proceed to the [Complete Workflow Walkthrough](#complete-workflow-walkthrough) to test all features.

> **To stop the server:** Press `Ctrl + C` in the terminal.

---

## Navigating the Application

```
http://localhost:5000/               → Home / Landing page
http://localhost:5000/login          → Admin Login
http://localhost:5000/login_trainer  → Trainer Login
http://localhost:5000/login_user     → User Login
http://localhost:5000/register       → New User Registration
http://localhost:5000/reg_trainer    → New Trainer Registration
```

---

## Complete Workflow Walkthrough

Here is the recommended sequence to test all features end-to-end:

### Phase 1 — Admin Setup

1. Go to `/login` and log in as `admin / admin`
2. On the Admin dashboard (`/admin`), create a new model:
   - Enter a model name, e.g., `BirdsNet`
   - Upload any placeholder file as the model file
3. Click the model → go to `/admin2` to add labels:
   - Enter `4` as the number of labels
   - Type: `Crow`, `Sparrow`, `Kingfisher`, `Peacock`
4. For each label, go to `/admin3` and upload images from the `sample/BirdsNet/` folder

### Phase 2 — Trainer Registration & Normal Upload

1. Go to `/reg_trainer` and register a new trainer (e.g., `trainer1`)
2. Log in as `trainer1` at `/login_trainer`
3. Select the `BirdsNet` model, enter label `Crow`, upload a crow image → should show **success**
4. The upload is recorded in the blockchain

### Phase 3 — Simulating a Label-Flipping Attack

1. Still logged in as `trainer1`
2. Select model `BirdsNet`, enter label `Sparrow`
3. Upload an image that was **already uploaded as a Crow image**
4. The system detects the hash collision with a different label
5. The screen shows the flagged image and a **warning message**
6. The trainer's `dstatus` is incremented to `1`
7. The attack is logged to the blockchain as type `Attack`

### Phase 4 — Viewing the Blockchain Audit Log

1. Log back in as admin → go to `/view_block?act=11`
2. You will see colour-coded blockchain entries:
   - **Green rows** — normal events (registrations, legitimate uploads)
   - **Red rows** — attack events and trainer eliminations
3. Each row shows: Block ID, Hash, Event Data, Timestamp

### Phase 5 — User Prediction

1. Register a user at `/register`, log in at `/login_user`
2. Go to `/userhome` and upload an image that was previously used as training data
3. The system returns the **predicted label** based on the hash match
4. The prediction query is also logged to the blockchain

---

## Attack Detection — Deep Dive

The core attack detection logic lives inside the `/tr_home` route in `main.py`. Here is exactly what happens when a trainer uploads an image:

```
Trainer uploads image.jpg
        │
        ▼
System computes SHA-256 hash of the file → e.g., "a3f9c2..."
        │
        ▼
SQL query: SELECT count(*) FROM pa_data WHERE hash1 = "a3f9c2..."
        │
   ┌────┴────┐
   │         │
count = 0   count > 0
(new image)  (image already in DB)
   │         │
   ▼         ▼
Save image  Retrieve stored model_id and label_name
to DB       and compare with the current upload
                │
            ┌───┴───────────────────┐
       same model             different model
       same label             OR different label
            │                       │
            ▼                       ▼
         OK ✓                LABEL-FLIPPING ATTACK ✗
                                    │
                                    ▼
                          Log to blockchain (type: 'Attack')
                          Increment trainer.dstatus by 1
                          Add image filename to wrong.txt
                          Display warning page to trainer
                                    │
                               ┌────┴────┐
                               │         │
                          dstatus=1   dstatus=2
                          Warning     PERMANENTLY ELIMINATED
                          shown       Login blocked forever
                                      Elimination logged
                                      to blockchain
```

---

## SPFL Algorithm — Deep Dive

The `detection()` function in `main.py` implements Self-Purified Federated Learning. Here is how it works step by step:

```python
# Setup
num_clients = 5       # total number of trainers in the federation
num_malicious = 2     # first 2 trainers are simulated attackers

for each client:
    generate random training data (200 samples, 10 features)
    
    if client is malicious (client_id < 2):
        flip all labels:  y = (y + 1) % 10
        # Every label is shifted by 1, corrupting the training signal
    
    train a small Dense neural network (10→32→10) on this data
    extract all model weights flattened into a single 1D vector

# Result: 5 weight vectors — 2 poisoned, 3 clean

compute the MEAN of all 5 vectors → this is the "reference vector"

for each client's weight vector:
    cosine_similarity = dot(client_vec, reference) / (|client_vec| × |reference|)
    
    if cosine_similarity >= 0.85:
        mark this client as BENIGN  ✓
    else:
        mark this client as MALICIOUS  ✗  (exclude from aggregation)

aggregate (average) only the BENIGN weight vectors
→ this averaged vector becomes the new GLOBAL MODEL weights
```

**Why cosine similarity works:** Malicious trainers, having trained on flipped labels, will have weight vectors that point in a meaningfully different direction in high-dimensional space compared to honest trainers. Cosine similarity measures this angular difference — poisoned updates receive a low score and are filtered out before they can corrupt the global model.

---

## Blockchain Logging — Deep Dive

The `modelchain()` function creates and chains every block. Here is the exact data format:

**Raw format in `d1.txt`:**
```
<block_id>##<md5_hash>##<event_data>##<timestamp>
```

Multiple blocks are separated by `#|`:
```
1##hash1##event1##time1#|2##hash2##event2##time2#|3##hash3##event3##time3
```

**Real event data examples by type:**

| Event Type | Example Blockchain Entry |
|------------|--------------------------|
| Model created | `ID:1, Model:BirdsNet, New model created, Model File:M1birds.zip` |
| Label added | `ID:2, Model:BirdsNet, Label created, Label(1):Crow` |
| Image uploaded (legit) | `ID:5, Model:BirdsNet, Label:Crow, Image:F5crow.jpg, Hash:abc123, upload by trainer1` |
| Attack detected | `ID:9, Model:BirdsNet, Label:Sparrow, Label-Flipping Attack(F9crow.jpg), Hash:abc123, upload by trainer1` |
| Trainer eliminated | `ID:2, Model Trainer: trainer1, Eliminated` |
| User prediction hit | `ID:3, Username:user1, File:test.jpg, Hash:abc123, Predicted Label: Crow` |
| User prediction miss | `ID:4, Username:user1, File:unknown.jpg, Hash:xyz789, Not Predicted` |

**The blockchain viewer (`/view_block`) colour codes rows:**
- **Red** — any entry containing the word `Attack` or `Eliminated`
- **Green** — all other legitimate activity

---

## Sample Datasets Included

Three pre-built datasets and their corresponding `.pkl` model files are included in the `sample/` folder:

### BirdsNet
- **Classes:** Crow, Kingfisher, Peacock, Sparrow
- **Images:** ~4–5 per class
- **Model file:** `BirdsNet.pkl`

### WildNet
- **Classes:** Beer (Bear), Cow, Elephant, Horse
- **Images:** ~5–8 per class
- **Model file:** `WildNet.pkl`

### CrimeNet
- **Use case:** Face/person recognition
- **Model file:** `CrimeNet.pkl`

To generate a new `.pkl` from your own image folder, edit `test.py`:

```python
image_folder = 'static/dataset/YourModel/YourLabel'
```

Then run:
```bash
python test.py
```

---

## Default Credentials

| Role | Login URL | Username | Password |
|------|-----------|----------|----------|
| Admin | `/login` | `admin` | `admin` |
| Trainer | `/login_trainer` | *(register at `/reg_trainer`)* | *(your choice)* |
| User | `/login_user` | *(register at `/register`)* | *(your choice)* |

> **Security Note:** This is an academic/research project. Passwords are stored in plaintext. Do not deploy on a public server without adding proper password hashing (e.g., bcrypt) and HTTPS.

---

## Common Issues & Fixes

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| `DatabaseError` on startup | Wrong DB password or database not created | Check `passwd=` in `main.py`; ensure `poisoning_attack` database exists |
| `FileNotFoundError: static/key.txt` | Blockchain files not initialised | Run the `echo` commands in Installation Step 6 |
| `500 Internal Server Error` on upload | `static/temp` or `static/dataset` folder missing | Run `mkdir -p static/dataset static/temp static/upload static/test` |
| Blockchain viewer is blank | `d1.txt` is empty or first-run | Re-initialise: `echo "" > static/web/assets/js/d1.txt` and `echo "1" > static/key.txt` |
| TensorFlow installation fails | Python version incompatibility | Try `pip install tensorflow-cpu` or use Python 3.9–3.11 |
| Trainer cannot log in | Account was eliminated (`dstatus >= 2`) | This is expected behaviour — the login query requires `dstatus < 2` |
| Images not saving | `static/upload/` folder doesn't exist | Create it manually: `mkdir static/upload` |
| Hash not detected as attack | Image was slightly modified before re-upload | SHA-256 is byte-exact; any modification produces a different hash |
