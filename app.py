"""
Trello Card Copier - Application Web
API Flask pour copier des cartes Trello entre tableaux
"""

from flask import Flask, render_template, jsonify, request, Response
from flask_cors import CORS
import json
from config import ConfigManager
from trello_api import TrelloClient

app = Flask(__name__)
CORS(app)

config_manager = ConfigManager()


@app.route('/')
def index():
    """Page principale de l'application"""
    return render_template('index.html')


@app.route('/api/config', methods=['GET'])
def get_config():
    """Récupère la configuration sauvegardée"""
    return jsonify({
        'source_board_id': config_manager.get_source_board_id(),
        'target_board_ids': config_manager.get_target_board_ids(),
        'label_name': config_manager.get_label_name()
    })


@app.route('/api/config', methods=['POST'])
def save_config():
    """Sauvegarde la configuration"""
    data = request.json
    config_manager.set_source_board_id(data.get('source_board_id', ''))
    config_manager.set_target_board_ids(data.get('target_board_ids', []))
    config_manager.set_label_name(data.get('label_name', ''))
    
    if config_manager.save_config():
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Erreur de sauvegarde'}), 500


@app.route('/api/copy', methods=['POST'])
def copy_cards():
    """Lance la copie des cartes et envoie les logs en streaming"""
    data = request.json
    source_board_id = data.get('source_board_id', '').strip()
    target_board_ids = data.get('target_board_ids', [])
    label_name = data.get('label_name', '').strip()
    
    # Validation
    if not source_board_id:
        return jsonify({'error': 'Source Board ID requis'}), 400
    if not target_board_ids:
        return jsonify({'error': 'Au moins un Target Board ID requis'}), 400
    if not label_name:
        return jsonify({'error': 'Label name requis'}), 400
    
    def generate_logs():
        """Générateur pour le streaming des logs"""
        logs = []
        
        def log_callback(message):
            logs.append(message)
            yield f"data: {json.dumps({'log': message})}\n\n"
        
        try:
            # Initialiser le client Trello
            api_key, token = config_manager.get_api_credentials()
            if not api_key or not token:
                yield f"data: {json.dumps({'error': 'API Key et Token requis dans config.json'})}\n\n"
                return
            
            trello_client = TrelloClient(api_key, token)
            
            # Effectuer la copie
            result = trello_client.copy_cards_to_multiple_boards(
                source_board_id=source_board_id,
                target_board_ids=target_board_ids,
                label_name=label_name,
                log_callback=log_callback
            )
            
            # Sauvegarder la config en cas de succès
            if result.get("success", 0) > 0:
                config_manager.set_source_board_id(source_board_id)
                config_manager.set_target_board_ids(target_board_ids)
                config_manager.set_label_name(label_name)
                config_manager.save_config()
            
            # Envoyer le résultat final
            yield f"data: {json.dumps({'result': result})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate_logs(), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
