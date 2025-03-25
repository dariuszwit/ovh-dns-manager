# Check if Python and pip are available
if (-Not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python is not installed or not found in PATH."
    exit 1
}

if (-Not (Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Pip is not installed or not found in PATH."
    exit 1
}

# Install Flask-Babel
Write-Host "📦 Installing Flask-Babel..."
pip install Flask-Babel

# Create the translations directory if it does not exist
if (-Not (Test-Path "translations")) {
    Write-Host "📂 Creating translations directory..."
    mkdir translations
}

# Create language directories if they do not exist
if (-Not (Test-Path "translations\pl\LC_MESSAGES")) {
    mkdir translations\pl\LC_MESSAGES
}

if (-Not (Test-Path "translations\en\LC_MESSAGES")) {
    mkdir translations\en\LC_MESSAGES
}

# Create the babel.cfg configuration file if it does not exist
$babelConfigPath = "babel.cfg"
if (-Not (Test-Path $babelConfigPath)) {
    Write-Host "📄 Creating babel.cfg file..."
    Set-Content -Path $babelConfigPath -Value @"
[python]
keywords = _ gettext ngettext
mapping = **.py

[jinja2: templates/**.html]
extensions = jinja2.ext.autoescape, jinja2.ext.with_
"@
}

# Extract translatable strings
Write-Host "📥 Extracting translations..."
pybabel extract -F babel.cfg -o messages.pot .

# Check if messages.pot was generated
if (-Not (Test-Path "messages.pot")) {
    Write-Host "❌ Error: messages.pot file was not created. Check babel.cfg syntax."
    exit 1
}

# Initialize languages (if they do not exist)
if (-Not (Test-Path "translations/pl/LC_MESSAGES/messages.po")) {
    Write-Host "🌎 Initializing Polish language..."
    pybabel init -i messages.pot -d translations -l pl
}

if (-Not (Test-Path "translations/en/LC_MESSAGES/messages.po")) {
    Write-Host "🌎 Initializing English language..."
    pybabel init -i messages.pot -d translations -l en
}

# Check if messages.po files exist before modifying them
$plPoPath = "translations/pl/LC_MESSAGES/messages.po"
$enPoPath = "translations/en/LC_MESSAGES/messages.po"

if (-Not (Test-Path $plPoPath) -or -Not (Test-Path $enPoPath)) {
    Write-Host "❌ Error: messages.po files were not created properly."
    exit 1
}

# Compile translations
Write-Host "⚙️ Compiling translations..."
pybabel compile -d translations

Write-Host "✅ Translation setup completed successfully!"
