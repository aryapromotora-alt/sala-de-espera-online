from flask import Blueprint, request, jsonify
from src.models.playlist import db, Playlist, UserSession
import uuid
import json

playlist_bp = Blueprint('playlist', __name__)

def get_or_create_session(session_id=None):
    """Obtém ou cria uma sessão de usuário"""
    if not session_id:
        session_id = str(uuid.uuid4())
    
    session = UserSession.query.filter_by(session_id=session_id).first()
    if not session:
        session = UserSession(session_id=session_id)
        db.session.add(session)
        
        # Criar playlist padrão para nova sessão
        default_playlist = Playlist(name='default', user_id=session_id, items=[])
        db.session.add(default_playlist)
        
        db.session.commit()
    
    return session

@playlist_bp.route('/session', methods=['POST'])
def create_or_get_session():
    """Cria ou obtém uma sessão de usuário"""
    data = request.get_json() or {}
    session_id = data.get("session_id") or request.headers.get("X-Session-ID")
    
    session = get_or_create_session(session_id)
    
    return jsonify({
        'success': True,
        'session': session.to_dict()
    })

@playlist_bp.route('/playlists/<session_id>', methods=['GET'])
def get_playlists(session_id):
    """Obtém todas as playlists de um usuário"""
    session = get_or_create_session(session_id)
    playlists = Playlist.query.filter_by(user_id=session_id).all()
    
    return jsonify({
        'success': True,
        'playlists': [playlist.to_dict() for playlist in playlists],
        'current_playlist': session.current_playlist
    })

@playlist_bp.route('/playlists/<session_id>/<playlist_name>', methods=['GET'])
def get_playlist(session_id, playlist_name):
    """Obtém uma playlist específica"""
    playlist = Playlist.query.filter_by(user_id=session_id, name=playlist_name).first()
    
    if not playlist:
        return jsonify({
            'success': False,
            'error': 'Playlist não encontrada'
        }), 404
    
    return jsonify({
        'success': True,
        'playlist': playlist.to_dict()
    })

@playlist_bp.route('/playlists/<session_id>/<playlist_name>', methods=['POST'])
def create_playlist(session_id, playlist_name):
    """Cria uma nova playlist"""
    session = get_or_create_session(session_id)
    
    # Verificar se já existe
    existing = Playlist.query.filter_by(user_id=session_id, name=playlist_name).first()
    if existing:
        return jsonify({
            'success': False,
            'error': 'Playlist já existe'
        }), 400
    
    data = request.get_json() or {}
    items = data.get('items', [])
    
    playlist = Playlist(name=playlist_name, user_id=session_id, items=items)
    db.session.add(playlist)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'playlist': playlist.to_dict()
    })

@playlist_bp.route('/playlists/<session_id>/<playlist_name>', methods=['PUT'])
def update_playlist(session_id, playlist_name):
    """Atualiza uma playlist existente"""
    playlist = Playlist.query.filter_by(user_id=session_id, name=playlist_name).first()
    
    if not playlist:
        return jsonify({
            'success': False,
            'error': 'Playlist não encontrada'
        }), 404
    
    data = request.get_json() or {}
    items = data.get('items', [])
    
    playlist.set_items(items)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'playlist': playlist.to_dict()
    })

@playlist_bp.route('/playlists/<session_id>/<playlist_name>', methods=['DELETE'])
def delete_playlist(session_id, playlist_name):
    """Deleta uma playlist"""
    if playlist_name == 'default':
        return jsonify({
            'success': False,
            'error': 'Não é possível deletar a playlist padrão'
        }), 400
    
    playlist = Playlist.query.filter_by(user_id=session_id, name=playlist_name).first()
    
    if not playlist:
        return jsonify({
            'success': False,
            'error': 'Playlist não encontrada'
        }), 404
    
    db.session.delete(playlist)
    
    # Se era a playlist atual, mudar para default
    session = UserSession.query.filter_by(session_id=session_id).first()
    if session and session.current_playlist == playlist_name:
        session.current_playlist = 'default'
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Playlist deletada com sucesso'
    })

@playlist_bp.route('/session/<session_id>/current-playlist', methods=['PUT'])
def set_current_playlist(session_id):
    """Define a playlist atual do usuário"""
    data = request.get_json() or {}
    playlist_name = data.get('playlist_name')
    
    if not playlist_name:
        return jsonify({
            'success': False,
            'error': 'Nome da playlist é obrigatório'
        }), 400
    
    session = get_or_create_session(session_id)
    
    # Verificar se a playlist existe
    playlist = Playlist.query.filter_by(user_id=session_id, name=playlist_name).first()
    if not playlist:
        return jsonify({
            'success': False,
            'error': 'Playlist não encontrada'
        }), 404
    
    session.current_playlist = playlist_name
    db.session.commit()
    
    return jsonify({
        'success': True,
        'current_playlist': playlist_name
    })

@playlist_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        'success': True,
        'message': 'API funcionando corretamente',
        'total_playlists': Playlist.query.count(),
        'total_sessions': UserSession.query.count()
    })

