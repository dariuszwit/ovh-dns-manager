from flask import Flask, redirect, request, render_template, url_for, session
from flask_babel import Babel, _
from config.settings import Settings
from frontend import frontend_bp  # Importujemy główny Blueprint z frontend/__init__.py

app = Flask(__name__)
app.config.from_object(Settings)

# Flask-Babel Configuration for Multiple Languages
app.config['BABEL_DEFAULT_LOCALE'] = 'pl'  # Default language is Polish
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

babel = Babel(app)

# Language Selection Based on User Session or Browser Settings
def get_locale():
    return session.get('lang') or request.accept_languages.best_match(['en', 'pl'])

babel.locale_selector_func = get_locale

# Ensure get_locale is available in Jinja2 templates
app.jinja_env.globals['get_locale'] = get_locale

# Register the main blueprint for frontend
app.register_blueprint(frontend_bp)

# Home Page - Redirects to Login
@app.route("/")
def home():
    return redirect(url_for('frontend.auth.login'))  # Auto redirect to login

# Change Language Route
@app.route("/change-language/<lang>")
def change_language(lang):
    if lang in ['en', 'pl']:
        session['lang'] = lang
        session.modified = True  # Ensure session updates
    return redirect(request.referrer or url_for('home'))

# Favicon Route
@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon-linis-it.ico'))

# Handle 404 Errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
