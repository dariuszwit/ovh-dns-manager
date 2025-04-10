from flask import Flask, redirect, request, render_template, url_for, session
from flask_babel import Babel, _
from config.settings import Settings
from frontend import frontend_bp  # Import głównego Blueprinta

app = Flask(__name__)
app.config.from_object(Settings)

# Flask-Babel – obsługa wielu języków
app.config['BABEL_DEFAULT_LOCALE'] = 'pl'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
babel = Babel(app)

# Dynamiczny wybór języka
def get_locale():
    return session.get('lang') or request.accept_languages.best_match(['en', 'pl'])

babel.locale_selector_func = get_locale
app.jinja_env.globals['get_locale'] = get_locale

# Rejestracja blueprinta frontendowego
app.register_blueprint(frontend_bp)

# Strona główna przekierowuje do logowania
@app.route("/")
def home():
    return redirect(url_for('frontend.auth.login'))

# Zmiana języka
@app.route("/change-language/<lang>")
def change_language(lang):
    if lang in ['en', 'pl']:
        session['lang'] = lang
        session.modified = True
    return redirect(request.referrer or url_for('home'))

# Obsługa favicon
@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon-linis-it.ico'))

# Obsługa błędów 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404

# Uruchamianie serwera Flask z portem z JSON-a
if __name__ == "__main__":
    print(f"[INFO] Starting Flask app on port {Settings.PORT}")
    app.run(host="0.0.0.0", port=Settings.PORT, debug=Settings.DEBUG)
