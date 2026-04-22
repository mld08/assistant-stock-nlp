"""
Application Flask - Gestion Intelligente de Stock avec Chatbot IA
Point d'entrée principal du backend.
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from database import init_db, import_dataframe
from nlp_engine import process_message

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialiser la base de données
init_db()


def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Endpoint pour uploader un fichier Excel.
    Lit la feuille 'Stock actif' et remplace la table SQLite.
    """
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'message': "❌ Aucun fichier trouvé dans la requête."
        }), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({
            'success': False,
            'message': "❌ Aucun fichier sélectionné."
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'message': "❌ Format non supporté. Veuillez uploader un fichier .xlsx ou .xls"
        }), 400

    try:
        # Sauvegarder le fichier
        filepath = os.path.join(UPLOAD_FOLDER, 'current_stock.xlsx')
        file.save(filepath)

        # Lire le fichier Excel
        try:
            # Essayer d'abord avec la feuille 'Stock actif'
            df = pd.read_excel(filepath, sheet_name='Stock actif')
        except ValueError:
            try:
                # Essayer des variantes du nom
                xls = pd.ExcelFile(filepath)
                sheet_names = xls.sheet_names
                
                # Chercher une feuille qui ressemble à "Stock actif"
                target_sheet = None
                for name in sheet_names:
                    if 'stock' in name.lower():
                        target_sheet = name
                        break
                
                if target_sheet:
                    df = pd.read_excel(filepath, sheet_name=target_sheet)
                else:
                    # Utiliser la première feuille par défaut
                    df = pd.read_excel(filepath, sheet_name=0)
                    
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f"❌ Erreur lors de la lecture du fichier : {str(e)}"
                }), 400

        # Importer dans SQLite
        row_count = import_dataframe(df)

        return jsonify({
            'success': True,
            'message': f"✅ Base mise à jour avec succès ! {row_count} article(s) importé(s).",
            'row_count': row_count
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"❌ Erreur lors du traitement : {str(e)}"
        }), 500


@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint chatbot.
    Reçoit un message, l'analyse via le moteur NLP, et retourne les résultats.
    """
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({
            'success': False,
            'type': 'text',
            'message': "❌ Message manquant dans la requête.",
            'data': None
        }), 400

    message = data['message'].strip()

    if not message:
        return jsonify({
            'success': False,
            'type': 'text',
            'message': "❌ Le message est vide.",
            'data': None
        }), 400

    try:
        result = process_message(message)
        result['success'] = True
        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'type': 'text',
            'message': f"❌ Erreur interne : {str(e)}",
            'data': None
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de vérification de santé."""
    return jsonify({'status': 'ok', 'message': 'Le serveur fonctionne correctement.'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
