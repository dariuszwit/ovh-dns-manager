# app.py
from flask import Flask
from config.settings import Settings
from frontend.views import frontend_bp

app = Flask(__name__)
app.config.from_object(Settings)

# Register blueprint with all widoki frontendu
app.register_blueprint(frontend_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
