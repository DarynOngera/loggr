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
2.  **Install dependencies and set up the virtual environment using Makefile:**
    ```bash
    make install
    ```

## Usage

### 1. Start the Keylogger
To begin monitoring and logging activities, use the Makefile:
```bash
make run_keylogger
```
This script will run in the background, collecting data and saving it to the `output/` directory.

### 2. Start the Web Interface
To view the collected data, use the Makefile to start the Flask web application:
```bash
make run_app
```
Once the server is running, open your web browser and navigate to `http://127.0.0.1:5000/` (or the address displayed in your terminal).

### Data Storage
All collected data (keystrokes, network activity, browser history, filesystem events, and screenshots) is stored in the `output/` directory within the project.

## Windows Specific Implementation

For Windows operating systems, a separate implementation is provided that stores all collected data in a SQLite database for improved data handling and querying.

### Setup (Windows)
1.  **Navigate to the Windows directory:**
    ```bash
    cd windows_keylogger
    ```
2.  **Install dependencies and set up the virtual environment using Makefile:**
    ```bash
    make install
    ```

### Usage (Windows)
1.  **Start the Keylogger (Windows):**
    ```bash
    make run_keylogger
    ```
    This script will run in the background, collecting data and saving it to `output/keylogger_data.db`.

2.  **Start the Web Interface (Windows):**
    ```bash
    make run_app
    ```
    Once the server is running, open your web browser and navigate to `http://127.0.0.1:5000/` (or the address displayed in your terminal).

### Data Storage (Windows)
All collected data for the Windows implementation is stored in `output/keylogger_data.db`.

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
├── Makefile                # Project build and management commands
├── windows_keylogger/      # Windows-specific implementation
│   ├── app.py
│   ├── keyloggermax.py
│   ├── requirements.txt
│   ├── Makefile
│   └── templates/
│       ├── index.html
│       ├── network.html
│       ├── browser.html
│       ├── filesystem.html
│       └── screenshots.html
└── README.md               # This file
```

## Contributing
Contributions are welcome! Please feel free to submit pull requests or open issues for any bugs or feature requests.

## License
This project is open-source and available under the [MIT License](LICENSE).
