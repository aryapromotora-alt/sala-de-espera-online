import os
import sys
# DON\'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from flask_cors import CORS
from src.models.user import db
from src.models.playlist import Playlist, UserSession
from src.routes.user import user_bp
from src.routes.playlist_global import playlist_global_bp
from src.routes.rss import rss_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Configurar CORS para permitir requisições do frontend
CORS(app, origins="*")

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(playlist_global_bp, url_prefix='/api')
app.register_blueprint(rss_bp, url_prefix='/api')

# Vercel does not support SQLite for persistent storage.
# Please configure an external database (e.g., PostgreSQL, MongoDB) and update the connection string.
# Example: app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
# db.init_app(app)
# with app.app_context():
#     db.create_all()

# The `serve` route for static files is no longer needed as Vercel handles static files.
# The `if __name__ == '__main__':` block is also removed as Vercel manages the execution.

