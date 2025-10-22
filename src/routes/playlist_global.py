from flask import Blueprint, request, jsonify
from src.models.playlist import db, Playlist, UserSession
import uuid
import json

playlist_global_bp = Blueprint('playlist_global', __name__)

@playlist_global_bp.route('/global-session', methods=['POST'])
def create_or_get_global_session():
    """Cria ou obtém uma sessão global compartilhada"""
    data = request.get_json() or {}
    global_session_id = data.get('global_session_id', 'global_default')
    
    # Usar um ID de sessão global fixo para todos os usuários
    session = UserSession.query.filter_by(session_id=global_session_id).first()
    if not session:
        session = UserSession(session_id=global_session_id)
        db.session.add(session)
        
        # Criar playlist padrão para a sessão global
        default_playlist = Playlist(name='default', user_id=global_session_id, items=[])
        db.session.add(default_playlist)
        
        db.session.commit()
    
    return jsonify({
        'success': True,
        'session': session.to_dict()
    })

@playlist_global_bp.route('/global-playlists', methods=['GET'])
def get_global_playlists():
    """Obtém todas as playlists globais"""
    global_session_id = 'global_default'
    session = UserSession.query.filter_by(session_id=global_session_id).first()
    
    if not session:
        # Criar sessão global se não existir
        session = UserSession(session_id=global_session_id)
        db.session.add(session)
        
        # Criar playlist padrão para a sessão global
        default_playlist = Playlist(name='default', user_id=global_session_id, items=[])
        db.session.add(default_playlist)
        
        db.session.commit()
    
    playlists = Playlist.query.filter_by(user_id=global_session_id).all()
    
    # Converter para formato de dicionário com nome da playlist como chave
    playlists_dict = {}
    for playlist in playlists:
        playlists_dict[playlist.name] = playlist.get_items()
    
    return jsonify({
        'success': True,
        'playlists': playlists_dict,
        'current_playlist': session.current_playlist
    })

@playlist_global_bp.route('/global-playlists/<playlist_name>', methods=['PUT'])
def update_global_playlist(playlist_name):
    """Atualiza uma playlist global"""
    global_session_id = 'global_default'
    playlist = Playlist.query.filter_by(user_id=global_session_id, name=playlist_name).first()
    
    if not playlist:
        # Criar playlist se não existir
        data = request.get_json() or {}
        items = data.get('items', [])
        
        playlist = Playlist(name=playlist_name, user_id=global_session_id, items=items)
        db.session.add(playlist)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'playlist': playlist.to_dict()
        })
    
    data = request.get_json() or {}
    items = data.get('items', [])
    
    playlist.set_items(items)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'playlist': playlist.to_dict()
    })

@playlist_global_bp.route('/global-current-playlist', methods=['PUT'])
def set_global_current_playlist():
    """Define a playlist atual global"""
    global_session_id = 'global_default'
    data = request.get_json() or {}
    playlist_name = data.get('playlist_name')
    
    if not playlist_name:
        return jsonify({
            'success': False,
            'error': 'Nome da playlist é obrigatório'
        }), 400
    
    session = UserSession.query.filter_by(session_id=global_session_id).first()
    if not session:
        session = UserSession(session_id=global_session_id)
        db.session.add(session)
    
    # Verificar se a playlist existe
    playlist = Playlist.query.filter_by(user_id=global_session_id, name=playlist_name).first()
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

@playlist_global_bp.route('/global-playlists/<playlist_name>', methods=['DELETE'])
def delete_global_playlist(playlist_name):
    """Deleta uma playlist global"""
    if playlist_name == 'default':
        return jsonify({
            'success': False,
            'error': 'Não é possível deletar a playlist padrão'
        }), 400
    
    global_session_id = 'global_default'
    playlist = Playlist.query.filter_by(user_id=global_session_id, name=playlist_name).first()
    
    if not playlist:
        return jsonify({
            'success': False,
            'error': 'Playlist não encontrada'
        }), 404
    
    db.session.delete(playlist)
    
    # Se era a playlist atual, mudar para default
    session = UserSession.query.filter_by(session_id=global_session_id).first()
    if session and session.current_playlist == playlist_name:
        session.current_playlist = 'default'
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Playlist deletada com sucesso'
    })

