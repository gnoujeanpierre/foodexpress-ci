# tools\seed_faiss_ci.py
"""
Script d'alimentation FAISS avec données marché Côte d'Ivoire.
Recommandation 2 : Mémoire FAISS enrichie marché CI.

Ce script crée un index FAISS vectoriel contenant les données
essentielles du marché ivoirien pour que les agents (notamment
les agents Gemini Flash) produisent des sorties localisées.
"""

import argparse
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# ───────────────────────────────────────────────────────────────
# CONFIGURATION
# ───────────────────────────────────────────────────────────────

INDEX_DIR = Path(__file__).resolve().parent.parent / "memory" / "faiss_ci"
INDEX_FILE = INDEX_DIR / "ci_market.index"
META_FILE = INDEX_DIR / "ci_market_metadata.pkl"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_DIM = 384  # Dimension de sortie de all-MiniLM-L6-v2


# ───────────────────────────────────────────────────────────────
# DONNÉES MARCHÉ CI
# ───────────────────────────────────────────────────────────────

CI_MARKET_DATA: List[Dict[str, Any]] = [
    # Taux de change
    {
        "category": "taux_change",
        "title": "Taux de change FCFA",
        "content": (
            "En Côte d'Ivoire, la devise officielle est le Franc CFA (FCFA), "
            "fixé à 1 EUR = 655,957 FCFA et environ 1 USD = 600 FCFA (taux variable). "
            "Les transactions internationales se font souvent en EUR ou USD, "
            "mais les paiements locaux sont toujours en FCFA."
        ),
    },
    {
        "category": "taux_change",
        "title": "Conversion rapide FCFA",
        "content": (
            "Règles de conversion pour les devis La TEC : "
            "100 000 FCFA ≈ 152 EUR. "
            "500 000 FCFA ≈ 762 EUR. "
            "1 000 000 FCFA ≈ 1 524 EUR. "
            "1 500 000 FCFA ≈ 2 286 EUR. "
            "2 000 000 FCFA ≈ 3 048 EUR. "
            "5 000 000 FCFA ≈ 7 620 EUR. "
            "10 000 000 FCFA ≈ 15 240 EUR."
        ),
    },

    # Prix du marché CI
    {
        "category": "prix_marche",
        "title": "Applications mobiles Côte d'Ivoire",
        "content": (
            "Prix indicatifs développement apps mobiles en CI (2026) : "
            "Application simple (vitrine, 3-5 écrans) : 800 000 - 1 500 000 FCFA. "
            "Application e-commerce standard : 2 000 000 - 4 000 000 FCFA. "
            "Application sur mesure avec backend : 3 500 000 - 8 000 000 FCFA. "
            "Application complexe (livraison, géolocalisation, paiement) : 5 000 000 - 15 000 000 FCFA. "
            "Maintenance annuelle : 15-25% du coût initial."
        ),
    },
    {
        "category": "prix_marche",
        "title": "Sites web Côte d'Ivoire",
        "content": (
            "Prix indicatifs sites web en CI (2026) : "
            "Site vitrine institutionnel (5-10 pages) : 300 000 - 800 000 FCFA. "
            "Site e-commerce de base : 1 000 000 - 2 500 000 FCFA. "
            "Site e-commerce avancé (multivendeurs, paiement intégré) : 3 000 000 - 6 000 000 FCFA. "
            "Blog / portfolio : 200 000 - 500 000 FCFA. "
            "Refonte site existant : 60-80% du prix d'un nouveau site. "
            "Hébergement + nom de domaine annuel : 50 000 - 150 000 FCFA."
        ),
    },
    {
        "category": "prix_marche",
        "title": "Logiciels et solutions digitales Côte d'Ivoire",
        "content": (
            "Prix indicatifs logiciels sur mesure en CI (2026) : "
            "Logiciel de gestion simple (stock, client) : 1 500 000 - 3 000 000 FCFA. "
            "ERP PME (compta, RH, vente) : 4 000 000 - 10 000 000 FCFA. "
            "Tableau de bord BI / Analytics : 2 000 000 - 5 000 000 FCFA. "
            "Automatisation processus (RPA) : 1 000 000 - 4 000 000 FCFA. "
            "Chatbot / assistant IA basique : 500 000 - 1 500 000 FCFA. "
            "Solution IA avancée (RAG, ML) : 3 000 000 - 12 000 000 FCFA."
        ),
    },

    # Opérateurs télécoms
    {
        "category": "telecoms",
        "title": "Opérateurs télécoms Côte d'Ivoire",
        "content": (
            "Principaux opérateurs télécoms en Côte d'Ivoire : "
            "Orange Côte d'Ivoire (leader marché, réseau 4G étendu, services Orange Money). "
            "MTN Côte d'Ivoire (ex-Airtel, forte présence urbaine, MTN Mobile Money). "
            "Moov Africa Côte d'Ivoire (Maroc Telecom, couverture nationale, Moov Money). "
            "Services de paiement mobile : Orange Money, MTN Mobile Money, Wave (fintech indépendante très populaire), "
            "Moov Money. Wave est particulièrement utilisée par les PME pour les paiements instantanés."
        ),
    },
    {
        "category": "telecoms",
        "title": "Moyens de paiement digitaux CI",
        "content": (
            "Moyens de paiement acceptés par les PME ivoiriennes : "
            "Orange Money (transfert, paiement marchand, factures). "
            "Wave (transfert gratuit entre utilisateurs, très populaire chez les jeunes et commerçants). "
            "MTN Mobile Money (transfert, paiement). "
            "Moov Money (transfert, paiement). "
            "Cartes bancaires Visa / Mastercard (acceptation croissante). "
            "Paiement à la livraison (encore très répandu en e-commerce local)."
        ),
    },

    # Types de PME ivoiriennes
    {
        "category": "pme_types",
        "title": "Types de PME en Côte d'Ivoire",
        "content": (
            "Principaux secteurs de PME en Côte d'Ivoire : "
            "Commerce de détail et de gros (boutiques, superettes, importateurs). "
            "Import / Export (produits alimentaires, textiles, électronique, matériaux). "
            "Restauration et Hôtellerie (maquis, restaurants, fast-food, cafés). "
            "BTP et Construction (entrepreneurs, fournisseurs de matériaux, architectes). "
            "Agriculture et Agro-industrie (coopératives, transformateurs, exportateurs de cacao, café, noix de cajou). "
            "Transport et Logistique (transporteurs, livraison, location véhicules). "
            "Services professionnels (consulting, comptabilité, juridique, marketing). "
            "Santé et Bien-être (cliniques, pharmacies, centres de fitness). "
            "Éducation et Formation (écoles, centres de formation, e-learning)."
        ),
    },

    # Organismes clés
    {
        "category": "organismes",
        "title": "Organismes clés Côte d'Ivoire",
        "content": (
            "Institutions et organismes clés pour les entreprises en CI : "
            "CEPICI (Centre de Promotion des Investissements en Côte d'Ivoire) : formalités création d'entreprise, "
            "guichet unique, investissements étrangers. "
            "CCI-CI (Chambre de Commerce et d'Industrie de Côte d'Ivoire) : accompagnement PME, "
            "arbitrage commercial, registre du commerce. "
            "ARTCI (Autorité de Régulation des Télécommunications de Côte d'Ivoire) : régulation telecom, "
            "numérotation, conformité services digitaux. "
            "BRVM (Bourse Régionale des Valeurs Mobilières) : marché financier régional, "
            "cotations, obligations, financement entreprises. "
            "ABIDJAN.NET / AFRICAN MANAGER : médias business locaux."
        ),
    },

    # Délais de développement
    {
        "category": "delais",
        "title": "Délais réalistes de développement CI",
        "content": (
            "Délais indicatifs de livraison projets digitaux en Côte d'Ivoire : "
            "Site vitrine : 2-4 semaines. "
            "Site e-commerce standard : 4-8 semaines. "
            "Application mobile simple : 4-6 semaines. "
            "Application mobile complexe : 8-16 semaines. "
            "Logiciel métier sur mesure : 6-12 semaines (MVP), 3-6 mois (version complète). "
            "Intégration IA / Chatbot : 2-4 semaines (basique), 6-10 semaines (avancé). "
            "Ces délais incluent les phases de recette et ajustements avec le client local."
        ),
    },

    # Exemples de propositions commerciales
    {
        "category": "propositions",
        "title": "Exemple proposition commerciale - Site vitrine",
        "content": (
            "Proposition type La TEC - Site vitrine PME Abidjan : "
            "'Madame, Monsieur, La TEC propose la création de votre site vitrine professionnel "
            "à partir de 350 000 FCFA (hors frais annuels hébergement 75 000 FCFA). "
            "Livraison en 3 semaines. Paiement en 2 tranches : 50% à la commande, 50% à la livraison. "
            "Moyens acceptés : Orange Money, Wave, virement bancaire. "
            "Inclus : design responsive, 7 pages, formulaire contact, référencement Google local.'"
        ),
    },
    {
        "category": "propositions",
        "title": "Exemple proposition commerciale - App mobile",
        "content": (
            "Proposition type La TEC - Application mobile livraison : "
            "'Bonjour, Pour votre projet de livraison à Abidjan, La TEC développe une application "
            "iOS + Android avec géolocalisation, paiement Wave/Orange Money intégré, "
            "et tableau de bord admin. Budget indicatif : 6 500 000 FCFA. "
            "Délai : 10 semaines. Maintenance annuelle : 1 200 000 FCFA. "
            "Nous proposons une réunion de cadrage gratuite au Plateau ou par visio.'"
        ),
    },
    {
        "category": "propositions",
        "title": "Formules de politesse commerciales ivoiriennes",
        "content": (
            "Formules de politesse pour propositions commerciales en CI : "
            "Ouverture : 'Bonjour Madame, Monsieur,' / 'Salutations distinguées,' / 'J'espère que vous allez bien.' "
            "Corps : 'Dans le cadre de votre activité...' / 'Conscient des enjeux du marché ivoirien...' / "
            "'Compte tenu de la dynamique digitale à Abidjan...' "
            "Fermeture : 'Dans l'attente de votre retour,' / 'Restant à votre entière disposition,' / "
            "'Cordialement,' / 'Bien à vous,'. "
            "Mentionner 'Abidjan', 'Côte d'Ivoire', ou 'marché local' renforce la crédibilité."
        ),
    },
]


# ───────────────────────────────────────────────────────────────
# FONCTIONS FAISS
# ───────────────────────────────────────────────────────────────

def _ensure_index_dir() -> None:
    """Crée le répertoire de stockage FAISS s'il n'existe pas."""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)


def _get_text_for_embedding(item: Dict[str, Any]) -> str:
    """
    Concatène les champs pertinents d'un document en un seul texte
    pour l'embedding.
    """
    parts = [
        f"Catégorie: {item.get('category', '')}",
        f"Titre: {item.get('title', '')}",
        item.get("content", ""),
    ]
    return "\n".join(parts)


def build_faiss_index(force_rebuild: bool = False) -> Tuple[faiss.Index, List[Dict[str, Any]]]:
    """
    Construit (ou recharge) l'index FAISS avec les données marché CI.

    Args:
        force_rebuild: Si True, reconstruit l'index même s'il existe déjà.

    Returns:
        Tuple (index_faiss, metadata_list)
    """
    _ensure_index_dir()

    # Rechargement si l'index existe déjà
    if not force_rebuild and INDEX_FILE.exists() and META_FILE.exists():
        print(f"[FAISS CI] Chargement de l'index existant depuis {INDEX_DIR}")
        index = faiss.read_index(str(INDEX_FILE))
        with open(META_FILE, "rb") as f:
            metadata = pickle.load(f)
        return index, metadata

    print(f"[FAISS CI] Construction de l'index avec le modèle {MODEL_NAME}...")
    print("[FAISS CI] Téléchargement du modèle d'embeddings (premier lancement)...")

    # Chargement du modèle d'embeddings
    model = SentenceTransformer(MODEL_NAME)

    # Préparation des textes et métadonnées
    texts = [_get_text_for_embedding(item) for item in CI_MARKET_DATA]
    metadata = CI_MARKET_DATA.copy()

    # Génération des embeddings
    print(f"[FAISS CI] Encodage de {len(texts)} documents...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    # Normalisation L2 pour utiliser IndexFlatIP (produit scalaire = similarité cosinus)
    faiss.normalize_L2(embeddings)

    # Création de l'index FAISS
    index = faiss.IndexFlatIP(VECTOR_DIM)
    index.add(embeddings)

    # Sauvegarde
    faiss.write_index(index, str(INDEX_FILE))
    with open(META_FILE, "wb") as f:
        pickle.dump(metadata, f)

    print(f"[FAISS CI] Index sauvegardé : {INDEX_FILE}")
    print(f"[FAISS CI] Métadonnées sauvegardées : {META_FILE}")
    print(f"[FAISS CI] {len(metadata)} documents vectorisés avec succès.")

    return index, metadata


def search_similar_context(
    query: str,
    top_k: int = 3,
    index: Optional[faiss.Index] = None,
    metadata: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    Recherche les documents les plus similaires à la requête dans l'index FAISS.

    Args:
        query: Texte de la requête.
        top_k: Nombre de résultats à retourner.
        index: Index FAISS pré-chargé (optionnel).
        metadata: Métadonnées pré-chargées (optionnel).

    Returns:
        Liste des top_k documents avec score de similarité.
    """
    _ensure_index_dir()

    # Chargement si non fourni
    if index is None:
        if not INDEX_FILE.exists():
            raise FileNotFoundError(
                "L'index FAISS n'existe pas encore. Exécutez d'abord build_faiss_index()."
            )
        index = faiss.read_index(str(INDEX_FILE))

    if metadata is None:
        if not META_FILE.exists():
            raise FileNotFoundError(
                "Les métadonnées FAISS n'existent pas encore. Exécutez d'abord build_faiss_index()."
            )
        with open(META_FILE, "rb") as f:
            metadata = pickle.load(f)

    # Chargement du modèle
    model = SentenceTransformer(MODEL_NAME)

    # Embedding de la requête
    query_embedding = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)

    # Recherche
    scores, indices = index.search(query_embedding, top_k)

    # Formatage des résultats
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1 or idx >= len(metadata):
            continue
        doc = metadata[idx].copy()
        doc["similarity_score"] = float(score)
        results.append(doc)

    return results


# ───────────────────────────────────────────────────────────────
# POINT D'ENTRÉE CLI
# ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Alimentation et recherche FAISS - Données marché CI"
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Force la reconstruction de l'index FAISS",
    )
    parser.add_argument(
        "--search",
        type=str,
        metavar="QUERY",
        help="Requête de recherche dans l'index (ex: 'prix app mobile')",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Nombre de résultats à retourner (défaut: 3)",
    )

    args = parser.parse_args()

    if args.build or not INDEX_FILE.exists():
        build_faiss_index(force_rebuild=args.build)

    if args.search:
        results = search_similar_context(args.search, top_k=args.top_k)
        print(f"\nRésultats pour '{args.search}' :")
        for i, r in enumerate(results, 1):
            print(f"\n--- Résultat {i} (score: {r['similarity_score']:.4f}) ---")
            print(f"Catégorie : {r['category']}")
            print(f"Titre     : {r['title']}")
            print(f"Contenu   : {r['content'][:300]}...")