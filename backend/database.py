"""
Module de gestion de la base de données SQLite.
Gère l'initialisation, l'import depuis pandas DataFrame, et les requêtes.
"""

import sqlite3
import os
import pandas as pd

DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database')
DATABASE_PATH = os.path.join(DATABASE_DIR, 'stock.db')


def get_connection():
    """Crée et retourne une connexion SQLite."""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialise la base de données avec la table stock_actif si elle n'existe pas."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_actif (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Article TEXT,
            Description TEXT,
            TOTAL REAL,
            CUMP REAL,
            "FAS à appliquer" TEXT,
            Famille TEXT
        )
    ''')
    conn.commit()
    conn.close()


def import_dataframe(df):
    """
    Importe un DataFrame pandas dans la table stock_actif.
    Remplace toutes les données existantes.
    
    Args:
        df: pandas DataFrame contenant les données du stock
        
    Returns:
        int: Nombre de lignes importées
    """
    conn = get_connection()
    
    # Supprimer l'ancienne table et recréer
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS stock_actif')
    conn.commit()
    
    # Normaliser les noms de colonnes pour matcher ceux attendus
    column_mapping = {}
    for col in df.columns:
        col_lower = str(col).strip().lower()
        if 'article' in col_lower:
            column_mapping[col] = 'Article'
        elif 'description' in col_lower or 'désignation' in col_lower or 'designation' in col_lower:
            column_mapping[col] = 'Description'
        elif col_lower == 'total':
            column_mapping[col] = 'TOTAL'
        elif 'cump' in col_lower:
            column_mapping[col] = 'CUMP'
        elif 'fas' in col_lower:
            column_mapping[col] = 'FAS à appliquer'
        elif 'famille' in col_lower:
            column_mapping[col] = 'Famille'
    
    if column_mapping:
        df = df.rename(columns=column_mapping)
    
    # Garder uniquement les colonnes attendues
    expected_columns = ['Article', 'Description', 'TOTAL', 'CUMP', 'FAS à appliquer', 'Famille']
    existing_columns = [col for col in expected_columns if col in df.columns]
    
    if not existing_columns:
        raise ValueError("Aucune colonne reconnue dans le fichier Excel. "
                        "Colonnes attendues: Article, Description, TOTAL, CUMP, FAS à appliquer, Famille")
    
    df_filtered = df[existing_columns].copy()
    
    # Supprimer les lignes entièrement vides
    df_filtered = df_filtered.dropna(how='all')
    
    # Écrire dans SQLite
    df_filtered.to_sql('stock_actif', conn, if_exists='replace', index=False)
    
    row_count = len(df_filtered)
    conn.close()
    
    return row_count


def execute_query(query, params=None):
    """
    Exécute une requête SQL et retourne les résultats sous forme de liste de dictionnaires.
    
    Args:
        query: Requête SQL
        params: Paramètres pour la requête (optionnel)
        
    Returns:
        list: Liste de dictionnaires contenant les résultats
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        rows = cursor.fetchall()
        
        if rows:
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
        else:
            results = []
            
    except sqlite3.OperationalError as e:
        conn.close()
        raise e
    
    conn.close()
    return results


def get_all_families():
    """Retourne la liste de toutes les familles distinctes."""
    try:
        results = execute_query('SELECT DISTINCT Famille FROM stock_actif WHERE Famille IS NOT NULL ORDER BY Famille')
        return [r['Famille'] for r in results if r['Famille']]
    except Exception:
        return []


def get_stock_count():
    """Retourne le nombre total d'articles en stock."""
    try:
        results = execute_query('SELECT COUNT(*) as count FROM stock_actif')
        return results[0]['count'] if results else 0
    except Exception:
        return 0


def table_exists():
    """Vérifie si la table stock_actif existe et contient des données."""
    try:
        results = execute_query('SELECT COUNT(*) as count FROM stock_actif')
        return results[0]['count'] > 0 if results else False
    except Exception:
        return False
