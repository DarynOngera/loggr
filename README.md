# Keylogger Max

## Overview
Keylogger Max is a comprehensive system designed for monitoring and logging various user activities on a system. It captures keystrokes, network connections, browser history, filesystem changes, and periodic screenshots. All collected data is stored locally and can be viewed through a user-friendly web interface.

## Features
- **Keystroke Logging**: Records all keyboard inputs.
- **Network Activity Monitoring**: Logs active network connections, including process details, local, and remote addresses.
- **Browser History Logging**: Collects browsing history from popular web browsers (Chrome, Firefox, Edge).
- **Filesystem Activity Monitoring**: Tracks file and directory creations, deletions, modifications, and movements.
- **Screenshot Capture**: Periodically captures screenshots of the desktop.
- **Web Interface**: Provides a Flask-based web application for visualizing the collected data in an organized manner.

## Installation

### Prerequisites
- Python 3.x
- pip (Python package installer)

### Setup
1.  **Clone the repository (if applicable):**
    ```bash
    git clone <repository_url>
    cd keylogger_max
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: This project uses `ruff` for linting. If you wish to run lint checks, you may need to install it separately: `pip install ruff`.*

## Usage

### 1. Start the Keylogger
To begin monitoring and logging activities, run the `keyloggermax.py` script:
```bash
python3 keyloggermax.py
```
This script will run in the background, collecting data and saving it to the `output/` directory.

### 2. Start the Web Interface
To view the collected data, start the Flask web application:
```bash
python3 app.py
```
Once the server is running, open your web browser and navigate to `http://127.0.0.1:5000/` (or the address displayed in your terminal).

### Data Storage
All collected data (keystrokes, network activity, browser history, filesystem events, and screenshots) is stored in the `output/` directory within the project.

## Project Structure
```
keylogger_max/
├── app.py                  # Flask web application for data visualization
├── keyloggermax.py         # Main script for logging activities
├── requirements.txt        # Python dependencies
├── output/                 # Directory for collected logs and screenshots
│   ├── activity.csv        # Keystroke logs
│   ├── network_activity.csv# Network connection logs
│   ├── browser_history.csv # Browser history logs
│   ├── filesystem_activity.csv # Filesystem event logs
│   └── screenshots/        # Captured screenshots
├── templates/              # HTML templates for the web interface
│   ├── index.html
│   ├── network.html
│   ├── browser.html
│   ├── filesystem.html
│   └── screenshots.html
└── README.md               # This file
```

## Contributing
Contributions are welcome! Please feel free to submit pull requests or open issues for any bugs or feature requests.

## License
This project is open-source and available under the [MIT License](LICENSE).
