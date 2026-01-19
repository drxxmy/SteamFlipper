# Steam Flipper (SF)

Steam Flipper is a **Steam Market flip scanner** with a backend price analyzer and
a lightweight web frontend.

It monitors selected Steam Market items, evaluates potential flip profitability
(after fees), stores historical data, and notifies you when opportunities appear.

---

## Features

### Backend (Python)

* Periodically scans Steam Market prices
* Calculates net profit and ROI after Steam fees
* Risk classification based on liquidity & spread
* Duplicate and cooldown-based notification suppression
* Stores all scan results in SQLite
* Sends Telegram notifications for viable flips
* Watchlist stored in database

### Frontend (Vue.js)

* Displays detected flip opportunities
* Sortable and readable table UI
* Add items to the watchlist directly from the UI
* Open Steam Market listings from table rows

---

## Tech Stack

* **Backend**: Python, FastAPI, SQLite, aiosqlite
* **Frontend**: Vue 3, Vite, Tailwind CSS
* **Notifications**: Telegram Bot API
* **Dev Environment**: Nix, devenv, direnv

---

## Running the Project

### Prerequisites

* `nix` installed
* [Nix flakes](https://nixos.wiki/wiki/flakes) enabled
* `direnv` installed

---

### 1. Clone the repository

```bash
git clone https://github.com/drxxmy/SteamFlipper.git
cd steam-flipper
```

---

### 2. Allow direnv

```bash
direnv allow
```

This will automatically set up:

* Python virtual environment
* Node / pnpm
* All required dependencies

---

### 3. Start all services

```bash
devenv up
```

This launches:

* FastAPI backend
* Market scanner
* Vue frontend

---

## Project Structure (simplified)

```bash
.
├── backend/        # Python backend (Market scanner + FastAPI)
├── frontend/       # Vue.js frontend
└── flake.nix       # Nix + devenv config
```

---

## Disclaimer

This project is for **educational and research purposes**.
Steam Market behavior may change, and no guarantees of profitability are provided.
