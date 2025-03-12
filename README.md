# OVH API Manager

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-1.svg)](https://www.buymeacoffee.com/dariuszwit)

OVH API Manager is a web application that allows managing OVH domains via the OVH API.

## Version
- **Current Release:** 1.0.0

## Features
- User authentication
- OVH account selection
- Domain browsing and management
- Adding and deleting DNS records

## Requirements
- Python 3.11+
- Flask
- OVH API Client

## Installation and Configuration
1. **Clone the repository**
   ```sh
   git clone https://github.com/your-username/ovh-api-manager-python.git
   cd ovh-api-manager-python
   ```

2. **Create and activate a virtual environment**
   ```sh
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Application Configuration**
   - Settings are in the `config/settings.py` file. Fill in `SECRET_KEY` with a random key.
   - Configure the `ovh_accounts.json` file with your OVH API credentials (do not add this file to the repository).

5. **Run the application**
   ```sh
   python app.py
   ```

6. **Access the application**
   - The application runs at `http://127.0.0.1:8000/`
   - On Windows, the `.bat` file will automatically open the dashboard in a browser.

## Updating the `.bat` Script
To make accessing the dashboard easier, modify the `ovh-manager.bat` file to include the following command at the end:
```bat
start http://127.0.0.1:8000/
```
This will open the web application in your default browser once the server starts.

## Protecting Private Data
To secure your repository from leaking private data:
- **Add `ovh_accounts.json` and `users.json` to `.gitignore`**
- **Remove credentials from files before publishing**
- **Use environment variables instead of hardcoding sensitive information**

## Publishing on GitHub
To publish the project on GitHub, follow these steps:

1. **Initialize the repository**
   ```sh
   git init
   git branch -M main
   ```

2. **Create a `.gitignore` file** (ensure it contains the following entries)
   ```
   venv/
   *.pyc
   __pycache__/
   ovh_accounts.json
   users.json
   instance/
   config/settings.py
   ```

3. **Add and commit files**
   ```sh
   git add .
   git commit -m "Initial commit"
   ```

4. **Create a GitHub repository and link it to the local repository**
   ```sh
   git remote add origin https://github.com/your-username/ovh-api-manager-python.git
   git push -u origin main
   ```

After these steps, your project will be available on GitHub, and sensitive data will remain secure.

## Support the Project
If you find this project useful and would like to support its development, you can buy me a coffee:

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-1.svg)](https://www.buymeacoffee.com/dariuszwit)

