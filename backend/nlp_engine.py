"""
Moteur NLP local basé sur regex et règles intelligentes.
Analyse les messages en langage naturel pour détecter les intentions
et extraire les paramètres pertinents.
"""

import re
from database import execute_query, get_all_families, get_stock_count, table_exists


# ============================================================
# Patterns de détection d'intention
# ============================================================

INTENT_PATTERNS = {
    'search_articles': [
        r'article[s]?\s+',
        r'donne[- ]?moi\s+',
        r'affiche[r]?\s+',
        r'montre[r]?\s+',
        r'voir\s+',
        r'cherche[r]?\s+.*article',
        r'je\s+veux\s+',
        r'trouve[r]?\s+',
    ],
    'get_cump': [
        r'cump',
        r'co[uû]t\s+(unitaire|moyen)',
        r'prix\s+(moyen|unitaire)',
    ],
    'get_total': [
        r'total\b',
        r'quantit[eé]',
        r'combien\s+(de|d\')\s*stock',
        r'en\s+stock',
    ],
    'get_fas': [
        r'fas',
        r'facteur\s+',
    ],
    'search_family': [
        r'famille\s+',
        r'cat[eé]gorie\s+',
        r'type\s+',
        r'groupe\s+',
    ],
    'search_description': [
        r'description\s+',
        r'd[eé]signation\s+',
        r'contient\s+',
        r'cherche[r]?\s+',
        r'recherche[r]?\s+',
    ],
    'show_all': [
        r'tout\s+(le\s+)?stock',
        r'tous\s+les\s+articles',
        r'liste\s+compl[eè]te',
        r'affiche[r]?\s+tout',
        r'montre[r]?\s+tout',
        r'tout\s+afficher',
    ],
    'stock_summary': [
        r'r[eé]sum[eé]',
        r'statistique',
        r'combien\s+d.*article',
        r'nombre\s+d.*article',
        r'aper[cç]u',
        r'vue\s+d\'ensemble',
    ],
    'list_families': [
        r'liste[r]?\s+.*familles',
        r'quelles\s+familles',
        r'familles\s+disponibles',
        r'cat[eé]gories\s+disponibles',
    ],
    'help': [
        r'aide',
        r'help',
        r'comment\s+',
        r'que\s+peux[- ]tu',
        r'qu.*est[- ]ce\s+que\s+tu\s+(peux|sais)',
        r'fonctionnalit',
    ],
}

# Mots-clés d'accueil
GREETING_PATTERNS = [
    r'^(salut|bonjour|bonsoir|hello|hi|hey|coucou|salam)',
]


def detect_intent(message):
    """
    Détecte l'intention principale du message.
    
    Args:
        message: Message de l'utilisateur
        
    Returns:
        str: Intention détectée
    """
    msg_lower = message.lower().strip()
    
    # Vérifier les salutations
    for pattern in GREETING_PATTERNS:
        if re.search(pattern, msg_lower):
            return 'greeting'
    
    # Vérifier chaque intention par priorité
    # Ordre important: intentions plus spécifiques d'abord
    priority_order = [
        'help', 'list_families', 'stock_summary', 'show_all',
        'get_cump', 'get_total', 'get_fas',
        'search_family', 'search_description', 'search_articles'
    ]
    
    for intent in priority_order:
        patterns = INTENT_PATTERNS[intent]
        for pattern in patterns:
            if re.search(pattern, msg_lower):
                return intent
    
    # Si le message semble contenir uniquement des numéros et des séparateurs basiques
    if re.fullmatch(r'[\d\s,;\-&]+', msg_lower):
        return 'search_articles'
    
    return 'unknown'


def extract_article_numbers(message):
    """
    Extrait les numéros d'articles du message.
    
    Args:
        message: Message de l'utilisateur
        
    Returns:
        list: Liste de numéros d'articles (strings)
    """
    numbers = re.findall(r'\d+', message)
    return numbers


def extract_family_name(message):
    """
    Extrait le nom de famille du message.
    
    Args:
        message: Message de l'utilisateur
        
    Returns:
        str: Nom de la famille extraite
    """
    msg_lower = message.lower().strip()
    
    # Pattern: "famille X" ou "catégorie X"
    patterns = [
        r'famille\s+["\']?([a-zéèêëàâùûôîïç\s\-]+)["\']?',
        r'cat[eé]gorie\s+["\']?([a-zéèêëàâùûôîïç\s\-]+)["\']?',
        r'type\s+["\']?([a-zéèêëàâùûôîïç\s\-]+)["\']?',
        r'groupe\s+["\']?([a-zéèêëàâùûôîïç\s\-]+)["\']?',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, msg_lower)
        if match:
            return match.group(1).strip()
    
    # Si pas trouvé via pattern, essayer de matcher avec les familles existantes
    families = get_all_families()
    for family in families:
        if family and family.lower() in msg_lower:
            return family
    
    return None


def extract_search_term(message):
    """
    Extrait un terme de recherche pour description.
    
    Args:
        message: Message de l'utilisateur
        
    Returns:
        str: Terme de recherche
    """
    msg_lower = message.lower().strip()
    msg_clean = msg_lower.replace("'", " ").replace('"', ' ').replace(':', ' ').replace('à', 'a')
    
    # Retirer les mots-clés connus pour isoler le terme de recherche
    stop_words = {
        'cherche', 'chercher', 'recherche', 'rechercher', 'trouve', 'trouver',
        'contient', 'contenant', 'avec', 'description', 'désignation', 'designation',
        'article', 'articles', 'le', 'la', 'les', 'l', 'un', 'une', 'des', 'de', 'du', 'd',
        'dans', 'qui', 'que', 'quoi', 'dont', 'ou',
        'moi', 'donne', 'affiche', 'montre', 'voir',
        'je', 'veux', 'peux', 'tu', 'me', 'donnez', 's', 'il', 'vous', 'plait',
        'correspondant', 'pour', 'sur', 'est', 'sont', 'et', 'au', 'aux', 'ce', 'cet', 'cette',
        'ces', 'mon', 'ton', 'son', 'notre', 'votre', 'leur', 'correspond', 'a'
    }
    
    words = msg_clean.split()
    filtered = [w for w in words if w not in stop_words and len(w) >= 2]
    
    return ' '.join(filtered) if filtered else None


def process_message(message):
    """
    Traite un message utilisateur et retourne la réponse appropriée.
    
    Args:
        message: Message de l'utilisateur
        
    Returns:
        dict: Réponse contenant le type, le message texte, et les données
    """
    if not message or not message.strip():
        return {
            'type': 'text',
            'message': "Je n'ai pas compris votre message. Pouvez-vous reformuler ?",
            'data': None
        }
    
    # Vérifier si la base de données est chargée
    if not table_exists():
        intent = detect_intent(message)
        if intent in ('greeting', 'help'):
            pass  # Laisser passer les salutations et l'aide
        else:
            return {
                'type': 'text',
                'message': "⚠️ Aucune base de données chargée. Veuillez d'abord uploader un fichier Excel via le bouton en haut de la page.",
                'data': None
            }
    
    intent = detect_intent(message)
    
    # ============================================================
    # Routage par intention
    # ============================================================
    
    if intent == 'greeting':
        return handle_greeting()
    
    elif intent == 'help':
        return handle_help()
    
    elif intent == 'search_articles':
        return handle_search_articles(message)
    
    elif intent == 'get_cump':
        return handle_get_cump(message)
    
    elif intent == 'get_total':
        return handle_get_total(message)
    
    elif intent == 'get_fas':
        return handle_get_fas(message)
    
    elif intent == 'search_family':
        return handle_search_family(message)
    
    elif intent == 'search_description':
        return handle_search_description(message)
    
    elif intent == 'show_all':
        return handle_show_all()
    
    elif intent == 'stock_summary':
        return handle_stock_summary()
    
    elif intent == 'list_families':
        return handle_list_families()
    
    else:
        return handle_unknown(message)


# ============================================================
# Handlers par intention
# ============================================================

def handle_greeting():
    return {
        'type': 'text',
        'message': ("👋 Bonjour ! Je suis Alia votre assistant de gestion de stock.\n\n"
                    "Vous pouvez me poser des questions comme :\n"
                    "• *donne-moi l'article 10*\n"
                    "• *quel est le CUMP de l'article 17*\n"
                    "• *affiche les articles de la famille réseau*\n"
                    "• *montre-moi tout le stock*\n\n"
                    "Tapez **aide** pour voir toutes les commandes disponibles."),
        'data': None
    }


def handle_help():
    return {
        'type': 'text',
        'message': ("📖 **Commandes disponibles :**\n\n"
                    "🔍 **Recherche d'articles**\n"
                    "• *donne-moi l'article 10*\n"
                    "• *donne-moi les articles 20, 30 et 34*\n"
                    "• *je veux voir les articles 5 7 9*\n\n"
                    "💰 **CUMP (Coût Unitaire Moyen Pondéré)**\n"
                    "• *quel est le CUMP de l'article 17*\n"
                    "• *CUMP articles 5, 10, 15*\n\n"
                    "📦 **Stock total**\n"
                    "• *quel est le total de l'article 10*\n"
                    "• *quantité en stock de l'article 25*\n\n"
                    "👨‍👩‍👧‍👦 **Recherche par famille**\n"
                    "• *affiche les articles de la famille réseau*\n"
                    "• *montre la famille électrique*\n\n"
                    "🔎 **Recherche par description**\n"
                    "• *cherche câble dans les articles*\n\n"
                    "📊 **Vue d'ensemble**\n"
                    "• *montre-moi tout le stock*\n"
                    "• *résumé du stock*\n"
                    "• *quelles familles sont disponibles*\n\n"
                    "📤 **Upload Excel**\n"
                    "• Utilisez le bouton d'upload en haut pour charger un fichier .xlsx"),
        'data': None
    }


def normalize_article_id(val):
    if val is None:
        return ""
    val_str = str(val).strip()
    if val_str.endswith('.0'):
        return val_str[:-2]
    return val_str


def handle_search_articles(message):
    numbers = extract_article_numbers(message)
    
    if not numbers:
        return {
            'type': 'text',
            'message': "🔍 Je n'ai pas trouvé de numéro d'article dans votre message. Essayez par exemple : *donne-moi l'article 10*",
            'data': None
        }
    
    placeholders = ','.join(['?' for _ in numbers])
    query = f'SELECT Article, Description, TOTAL, CUMP, "FAS à appliquer", Famille FROM stock_actif WHERE Article IN ({placeholders})'
    
    try:
        results = execute_query(query, numbers)
    except Exception as e:
        return {
            'type': 'text',
            'message': f"❌ Erreur lors de la requête : {str(e)}",
            'data': None
        }
    
    # Réorganiser les résultats selon l'ordre demandé et ajouter les vides pour les non-trouvés
    results_map = {normalize_article_id(r.get('Article', '')): r for r in results}
    ordered_results = []
    not_found = []
    
    for n in numbers:
        if n in results_map:
            ordered_results.append(results_map[n])
        else:
            not_found.append(n)
            # Ajouter une ligne vide pour cet article
            ordered_results.append({
                'Article': n,
                'Description': '— (Non trouvé) —',
                'TOTAL': None,
                'CUMP': None,
                'FAS à appliquer': '—',
                'Famille': '—'
            })
    
    msg = f"✅ Voici les résultats pour les articles demandés :"
    if not_found:
        msg += f"\n⚠️ **Attention** : Les articles suivants n'existent pas dans la base : **{', '.join(not_found)}**"
    
    return {
        'type': 'table',
        'message': msg,
        'data': ordered_results,
        'columns': ['Article', 'Description', 'TOTAL', 'CUMP', 'FAS à appliquer', 'Famille']
    }


def handle_get_cump(message):
    numbers = extract_article_numbers(message)
    
    if not numbers:
        return {
            'type': 'text',
            'message': "🔍 Veuillez préciser le numéro d'article. Exemple : *quel est le CUMP de l'article 17*",
            'data': None
        }
    
    placeholders = ','.join(['?' for _ in numbers])
    query = f'SELECT Article, Description, CUMP FROM stock_actif WHERE Article IN ({placeholders})'
    
    try:
        results = execute_query(query, numbers)
    except Exception as e:
        return {
            'type': 'text',
            'message': f"❌ Erreur : {str(e)}",
            'data': None
        }
    
    # Réorganiser les résultats selon l'ordre demandé et ajouter les vides
    results_map = {normalize_article_id(r.get('Article', '')): r for r in results}
    ordered_results = []
    not_found = []
    
    for n in numbers:
        if n in results_map:
            ordered_results.append(results_map[n])
        else:
            not_found.append(n)
            ordered_results.append({
                'Article': n,
                'Description': '— (Inconnu) —',
                'CUMP': None
            })
    
    msg = f"💰 CUMP pour les articles demandés :"
    if not_found:
        msg += f"\n⚠️ Articles non trouvés : {', '.join(not_found)}"
    
    return {
        'type': 'table',
        'message': msg,
        'data': ordered_results,
        'columns': ['Article', 'Description', 'CUMP']
    }


def handle_get_total(message):
    numbers = extract_article_numbers(message)
    
    if not numbers:
        return {
            'type': 'text',
            'message': "🔍 Veuillez préciser le numéro d'article. Exemple : *quel est le total de l'article 10*",
            'data': None
        }
    
    placeholders = ','.join(['?' for _ in numbers])
    query = f'SELECT Article, Description, TOTAL FROM stock_actif WHERE Article IN ({placeholders})'
    
    try:
        results = execute_query(query, numbers)
    except Exception as e:
        return {
            'type': 'text',
            'message': f"❌ Erreur : {str(e)}",
            'data': None
        }
    
    # Réorganiser les résultats selon l'ordre demandé
    results_map = {normalize_article_id(r.get('Article', '')): r for r in results}
    ordered_results = []
    not_found = []
    
    for n in numbers:
        if n in results_map:
            ordered_results.append(results_map[n])
        else:
            not_found.append(n)
            ordered_results.append({
                'Article': n,
                'Description': '— (Inconnu) —',
                'TOTAL': None
            })
    
    msg = f"📦 Stock total pour les articles demandés :"
    if not_found:
        msg += f"\n⚠️ Articles non trouvés : {', '.join(not_found)}"

    return {
        'type': 'table',
        'message': msg,
        'data': ordered_results,
        'columns': ['Article', 'Description', 'TOTAL']
    }


def handle_get_fas(message):
    numbers = extract_article_numbers(message)
    
    if not numbers:
        return {
            'type': 'text',
            'message': "🔍 Veuillez préciser le numéro d'article. Exemple : *FAS de l'article 10*",
            'data': None
        }
    
    placeholders = ','.join(['?' for _ in numbers])
    query = f'SELECT Article, Description, "FAS à appliquer" FROM stock_actif WHERE Article IN ({placeholders})'
    
    try:
        results = execute_query(query, numbers)
    except Exception as e:
        return {
            'type': 'text',
            'message': f"❌ Erreur : {str(e)}",
            'data': None
        }
    
    # Réorganiser les résultats selon l'ordre demandé
    results_map = {normalize_article_id(r.get('Article', '')): r for r in results}
    ordered_results = []
    not_found = []
    
    for n in numbers:
        if n in results_map:
            ordered_results.append(results_map[n])
        else:
            not_found.append(n)
            ordered_results.append({
                'Article': n,
                'Description': '— (Inconnu) —',
                'FAS à appliquer': '—'
            })
    
    msg = f"📋 FAS pour les articles demandés :"
    if not_found:
        msg += f"\n⚠️ Articles non trouvés : {', '.join(not_found)}"

    return {
        'type': 'table',
        'message': msg,
        'data': ordered_results,
        'columns': ['Article', 'Description', 'FAS à appliquer']
    }


def handle_search_family(message):
    family_name = extract_family_name(message)
    
    if not family_name:
        families = get_all_families()
        if families:
            families_list = ', '.join([f"**{f}**" for f in families[:20]])
            return {
                'type': 'text',
                'message': f"🔍 Je n'ai pas identifié la famille. Familles disponibles :\n{families_list}\n\nExemple : *affiche les articles de la famille réseau*",
                'data': None
            }
        return {
            'type': 'text',
            'message': "🔍 Je n'ai pas identifié la famille. Essayez : *affiche les articles de la famille réseau*",
            'data': None
        }
    
    query = 'SELECT Article, Description, TOTAL, CUMP, "FAS à appliquer", Famille FROM stock_actif WHERE LOWER(Famille) LIKE ?'
    
    try:
        results = execute_query(query, [f'%{family_name.lower()}%'])
    except Exception as e:
        return {
            'type': 'text',
            'message': f"❌ Erreur : {str(e)}",
            'data': None
        }
    
    if not results:
        return {
            'type': 'text',
            'message': f"😕 Aucun article trouvé pour la famille **{family_name}**.",
            'data': None
        }
    
    return {
        'type': 'table',
        'message': f"👨‍👩‍👧‍👦 {len(results)} article(s) trouvé(s) dans la famille **{family_name}** :",
        'data': results,
        'columns': ['Article', 'Description', 'TOTAL', 'CUMP', 'FAS à appliquer', 'Famille']
    }


def search_catalog(words):
    if not words:
        return []
        
    conditions = []
    params = []
    for w in words:
        conditions.append('LOWER(Description) LIKE ?')
        params.append(f'%{w.lower()}%')
        
    # 1. Modèle strict (AND)
    where_clause = ' AND '.join(conditions)
    query = f'SELECT Article, Description, TOTAL, CUMP, "FAS à appliquer", Famille FROM stock_actif WHERE {where_clause} LIMIT 20'
    
    try:
        results = execute_query(query, params)
        if results:
            return results
    except Exception:
        pass
        
    # 2. Modèle souple (OR) + Scoring
    where_clause_or = ' OR '.join(conditions)
    query_or = f'SELECT Article, Description, TOTAL, CUMP, "FAS à appliquer", Famille FROM stock_actif WHERE {where_clause_or}'
    
    try:
        results = execute_query(query_or, params)
        if results:
            def score_func(r):
                d = str(r.get('Description', '')).lower()
                a = str(r.get('Article', '')).lower()
                score = 0
                for w in words:
                    wl = w.lower()
                    if wl in d: score += 1
                    if wl in a: score += 2  # Forte pondération si match ID
                return score
            
            scored_results = [r for r in results if score_func(r) > 0]
            scored_results.sort(key=score_func, reverse=True)
            return scored_results[:20]
    except Exception:
        pass
        
    return []


def handle_search_description(message):
    term = extract_search_term(message)
    
    if not term:
        return {
            'type': 'text',
            'message': "🔍 Veuillez préciser ce que vous cherchez. Exemple : *cherche câble*",
            'data': None
        }
    
    words = [w for w in term.split() if w]
    results = search_catalog(words)
    
    if not results:
        return {
            'type': 'text',
            'message': f"😕 Aucun article trouvé pour la recherche : **{term}**.",
            'data': None
        }
    
    return {
        'type': 'table',
        'message': f"🔎 {len(results)} résultat(s) pertinent(s) priorisé(s) pour **{term}** :",
        'data': results,
        'columns': ['Article', 'Description', 'TOTAL', 'CUMP', 'FAS à appliquer', 'Famille']
    }


def handle_show_all():
    query = 'SELECT Article, Description, TOTAL, CUMP, "FAS à appliquer", Famille FROM stock_actif LIMIT 100'
    
    try:
        results = execute_query(query)
        total = get_stock_count()
    except Exception as e:
        return {
            'type': 'text',
            'message': f"❌ Erreur : {str(e)}",
            'data': None
        }
    
    if not results:
        return {
            'type': 'text',
            'message': "📦 Le stock est vide. Veuillez uploader un fichier Excel.",
            'data': None
        }
    
    msg = f"📦 Affichage de {len(results)} article(s)"
    if total > 100:
        msg += f" sur {total} au total (limité à 100)"
    msg += " :"
    
    return {
        'type': 'table',
        'message': msg,
        'data': results,
        'columns': ['Article', 'Description', 'TOTAL', 'CUMP', 'FAS à appliquer', 'Famille']
    }


def handle_stock_summary():
    try:
        total = get_stock_count()
        families = get_all_families()
        
        # Calculer quelques stats
        stats_query = 'SELECT SUM(TOTAL) as sum_total, AVG(CUMP) as avg_cump, MIN(CUMP) as min_cump, MAX(CUMP) as max_cump FROM stock_actif'
        stats = execute_query(stats_query)
        
        msg = f"📊 **Résumé du stock**\n\n"
        msg += f"• **Nombre total d'articles :** {total}\n"
        msg += f"• **Nombre de familles :** {len(families)}\n"
        
        if stats and stats[0]:
            s = stats[0]
            if s.get('sum_total') is not None:
                msg += f"• **Stock total (somme) :** {s['sum_total']:,.2f}\n"
            if s.get('avg_cump') is not None:
                msg += f"• **CUMP moyen :** {s['avg_cump']:,.2f}\n"
            if s.get('min_cump') is not None:
                msg += f"• **CUMP min :** {s['min_cump']:,.2f}\n"
            if s.get('max_cump') is not None:
                msg += f"• **CUMP max :** {s['max_cump']:,.2f}\n"
        
        if families:
            msg += f"\n**Familles :** {', '.join(families[:20])}"
            if len(families) > 20:
                msg += f" ... et {len(families) - 20} autres"
        
        return {
            'type': 'text',
            'message': msg,
            'data': None
        }
    except Exception as e:
        return {
            'type': 'text',
            'message': f"❌ Erreur : {str(e)}",
            'data': None
        }


def handle_list_families():
    families = get_all_families()
    
    if not families:
        return {
            'type': 'text',
            'message': "📦 Aucune famille trouvée. Le stock est-il chargé ?",
            'data': None
        }
    
    families_list = '\n'.join([f"• **{f}**" for f in families])
    return {
        'type': 'text',
        'message': f"👨‍👩‍👧‍👦 **{len(families)} famille(s) disponible(s) :**\n\n{families_list}",
        'data': None
    }


def handle_unknown(message):
    # Dernière tentative : chercher si le message contient un mot qui matche une description
    term = extract_search_term(message)
    if not term:
        term = message.strip()
        
    if term and len(term) >= 2:
        words = [w for w in term.split() if len(w) >= 2]
        results = search_catalog(words)
        
        if results:
            return {
                'type': 'table',
                'message': f"🔎 J'ai cherché **{term}** dans le catalogue et trouvé {len(results)} résultat(s) pertinent(s) :",
                'data': results,
                'columns': ['Article', 'Description', 'TOTAL', 'CUMP', 'FAS à appliquer', 'Famille']
            }
    
    return {
        'type': 'text',
        'message': ("🤔 Je n'ai pas bien compris votre demande.\n\n"
                    "Essayez par exemple :\n"
                    "• *donne-moi l'article 10*\n"
                    "• *CUMP de l'article 5*\n"
                    "• *articles de la famille réseau*\n"
                    "• *cherche câble*\n\n"
                    "Tapez **aide** pour voir toutes les commandes."),
        'data': None
    }
