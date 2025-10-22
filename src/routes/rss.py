from flask import Blueprint, request, jsonify
import feedparser

rss_bp = Blueprint('rss', __name__)

@rss_bp.route('/parse-rss', methods=['POST'])
def parse_rss_feed():
    data = request.get_json()
    feed_url = data.get('feed_url')

    if not feed_url:
        return jsonify({'success': False, 'error': 'URL do feed RSS é obrigatória'}), 400

    try:
        feed = feedparser.parse(feed_url)
        
        if feed.bozo and feed.bozo_exception:
            # Log the exception for debugging, but still try to return what was parsed
            print(f"Erro ao analisar o feed: {feed.bozo_exception}")

        entries = []
        for entry in feed.entries:
            entries.append({
                'title': entry.title if hasattr(entry, 'title') else 'No Title',
                'link': entry.link if hasattr(entry, 'link') else '#',
                'published': entry.published if hasattr(entry, 'published') else '',
                'summary': entry.summary if hasattr(entry, 'summary') else '',
                'author': entry.author if hasattr(entry, 'author') else '',
                # Adicionar outros campos comuns que podem ser úteis
                'id': entry.id if hasattr(entry, 'id') else entry.link if hasattr(entry, 'link') else None,
                'media_content': entry.media_content if hasattr(entry, 'media_content') else []
            })
        
        return jsonify({
            'success': True,
            'feed_title': feed.feed.title if hasattr(feed.feed, 'title') else 'No Feed Title',
            'feed_link': feed.feed.link if hasattr(feed.feed, 'link') else '#',
            'entries': entries
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

