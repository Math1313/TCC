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
        import sys
        
        def log_callback(message):
            # Cette fonction est appelée de façon synchrone, on ne peut pas yield ici
            # On doit utiliser une autre approche
            pass
        
        try:
            # Initialiser le client Trello
            api_key, token = config_manager.get_api_credentials()
            if not api_key or not token:
                yield f"data: {json.dumps({'error': 'API Key et Token requis dans config.json'})}\n\n"
                return
            
            trello_client = TrelloClient(api_key, token)
            
            # Créer une liste partagée pour les logs
            import queue
            import threading
            
            log_queue = queue.Queue()
            
            def queued_log_callback(message):
                log_queue.put(message)
            
            # Lancer la copie dans un thread séparé
            result_container = [None]
            exception_container = [None]
            
            def run_copy():
                try:
                    result = trello_client.copy_cards_to_multiple_boards(
                        source_board_id=source_board_id,
                        target_board_ids=target_board_ids,
                        label_name=label_name,
                        log_callback=queued_log_callback
                    )
                    result_container[0] = result
                except Exception as e:
                    exception_container[0] = e
                finally:
                    log_queue.put(None)  # Signal de fin
            
            thread = threading.Thread(target=run_copy)
            thread.start()
            
            # Envoyer les logs au fur et à mesure qu'ils arrivent
            while True:
                try:
                    message = log_queue.get(timeout=0.1)
                    if message is None:  # Signal de fin
                        break
                    yield f"data: {json.dumps({'log': message})}\n\n"
                except queue.Empty:
                    continue
            
            thread.join()
            
            # Vérifier s'il y a eu une exception
            if exception_container[0]:
                yield f"data: {json.dumps({'error': str(exception_container[0])})}\n\n"
                return
            
            result = result_container[0]
            
            # Sauvegarder la config en cas de succès
            if result and result.get("success", 0) > 0:
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
