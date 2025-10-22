from src.models.user import db
import json
from datetime import datetime

class Playlist(db.Model):
    __tablename__ = 'playlists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(100), nullable=False)  # Para identificar o usuário/sessão
    items = db.Column(db.Text, nullable=False, default='[]')  # JSON string dos itens
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, name, user_id, items=None):
        self.name = name
        self.user_id = user_id
        self.items = json.dumps(items or [])
    
    def get_items(self):
        """Retorna os itens da playlist como lista Python"""
        try:
            return json.loads(self.items)
        except:
            return []
    
    def set_items(self, items_list):
        """Define os itens da playlist a partir de uma lista Python"""
        self.items = json.dumps(items_list)
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
            'items': self.get_items(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    current_playlist = db.Column(db.String(100), default='default')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, session_id, current_playlist='default'):
        self.session_id = session_id
        self.current_playlist = current_playlist
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'current_playlist': self.current_playlist,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None
        }

