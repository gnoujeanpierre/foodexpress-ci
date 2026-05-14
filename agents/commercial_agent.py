# agents\commercial_agent.py
"""
Commercial AGENT — La TEC (The Engineering & Creation)
LLM : gemini/gemini-1.5-flash
Recommandations : 1 (français CI) + 3 (validation humaine) + 5 (recherche web)

Cet agent gère la prospection commerciale, la rédaction de propositions
et la négociation auprès des PME/ETI en Côte d'Ivoire et Afrique francophone.
"""

import argparse
import json
import sqlite3
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from crewai import Agent, Task, Crew
from duckduckgo_search import DDGS
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# ─── Imports La TEC ───
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.json_validator import validate_agent_message, build_valid_message
from tools.seed_faiss_ci import search_similar_context


# ───────────────────────────────────────────────────────────────
# CONFIGURATION & CONSTANTES
# ───────────────────────────────────────────────────────────────

console = Console()

# Chemins Windows
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs" / "a_valider"
DB_PATH = BASE_DIR / "memory" / "la_tec_memory.db"

# Création du dossier de validation si inexistant
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Paramètres Gemini Flash
GEMINI_MODEL = "gemini/gemini-1.5-flash"
TEMPERATURE = 0.3

# Phrases types ivoiriennes pour enrichir le backstory (Recommandation 1)
PHRASES_TYPES_IVOIRIENNES = [
    "Bonjour Madame, Monsieur, j'espère que vous allez bien. Je me permets de vous contacter au sujet de...",
    "Compte tenu de la dynamique digitale à Abidjan et des opportunités du marché local, notre proposition s'adapte...",
    "Nous restons à votre entière disposition pour un rendez-vous au Plateau, à Cocody ou par visioconférence.",
]


# ───────────────────────────────────────────────────────────────
# SCHÉMAS PYDANTIC — DOCUMENTS COMMERCIAUX
# ───────────────────────────────────────────────────────────────

class BesoinClient(BaseModel):
    """Schéma de structuration du besoin client."""
    secteur_activite: str = Field(..., description="Secteur d'activité du prospect")
    taille_entreprise: str = Field(..., description="PME, ETI, Startup, etc.")
    besoin_principal: str = Field(..., description="Besoin exprimé en français")
    budget_estime: Optional[str] = Field(None, description="Budget indicatif en FCFA ou EUR")
    delai_souhaite: Optional[str] = Field(None, description="Délai souhaité")
    moyen_contact_prefere: Optional[str] = Field(
        default="WhatsApp / email",
        description="Canal de contact préféré du prospect"
    )
    localisation: Optional[str] = Field(
        default="Abidjan, Côte d'Ivoire",
        description="Ville / région du prospect"
    )


class PropositionCommerciale(BaseModel):
    """Schéma d'une proposition commerciale validée."""
    titre: str = Field(..., description="Titre de la proposition")
    destinataire: str = Field(..., description="Nom du prospect")
    contenu_markdown: str = Field(..., description="Corps de la proposition en markdown")
    prix_total_fcfa: int = Field(..., description="Prix total en FCFA")
    prix_total_eur: int = Field(..., description="Prix total en EUR (1 EUR = 655 FCFA)")
    delai_semaines: int = Field(..., description="Délai de livraison en semaines")
    moyens_paiement: List[str] = Field(
        default_factory=lambda: ["Orange Money", "Wave", "Virement bancaire"],
        description="Moyens de paiement proposés"
    )
    conditions: str = Field(
        default="50% à la commande, 50% à la livraison",
        description="Conditions de paiement"
    )
    date_emission: str = Field(
        default_factory=lambda: datetime.now().strftime("%d/%m/%Y"),
        description="Date d'émission JJ/MM/AAAA"
    )


# ───────────────────────────────────────────────────────────────
# OUTILS CREWAI INTÉGRÉS
# ───────────────────────────────────────────────────────────────

class MemoireMarcheCITool:
    """
    Outil CrewAI qui interroge l'index FAISS des données marché CI
    pour enrichir le contexte de l'agent commercial.
    """
    name: str = "memoire_marche_ci"
    description: str = (
        "Interroge la mémoire vectorielle FAISS contenant les données "
        "du marché ivoirien (prix, délais, opérateurs, PME, organismes). "
        "Utilisez cet outil pour obtenir des informations localisées avant "
        "de rédiger une proposition commerciale."
    )

    def _run(self, query: str, top_k: int = 3) -> str:
        try:
            results = search_similar_context(query, top_k=top_k)
            if not results:
                return "Aucune donnée trouvée dans la mémoire marché CI."
            lines = []
            for i, r in enumerate(results, 1):
                lines.append(
                    f"[{i}] {r['title']} (score: {r['similarity_score']:.3f})\n"
                    f"    {r['content'][:500]}..."
                )
            return "\n\n".join(lines)
        except Exception as exc:
            return f"Erreur mémoire FAISS : {str(exc)}"


class ValidationHumaineTool:
    """
    Outil CrewAI qui déclenche une pause de validation humaine
    avant l'envoi d'un document client (Recommandation 3).
    """
    name: str = "validation_humaine"
    description: str = (
        "BLOQUE l'exécution et demande une validation humaine avant "
        "d'envoyer un document client (proposition, devis, contrat). "
        "L'agent doit TOUJOURS appeler cet outil avant de finaliser "
        "un document destiné à un client."
    )

    def _run(self, document_type: str, apercu: str) -> str:
        console.print()
        console.print(Panel(
            Text(
                f"📋 VALIDATION REQUISE\n\n"
                f"Type de document : {document_type}\n"
                f"Aperçu :\n{apercu[:800]}...\n\n"
                f"Vérifiez le document ci-dessus avant envoi au client.",
                style="yellow"
            ),
            title="[yellow]⚠️  PAUSE COMMERCIALE[/]",
            border_style="yellow",
        ))

        # Sauvegarde automatique dans logs\a_valider\
        file_name = f"prop_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.md"
        file_path = LOGS_DIR / file_name
        file_path.write_text(apercu, encoding="utf-8")
        console.print(f"[dim]💾 Document sauvegardé : {file_path}[/dim]")

        # Log horodaté dans SQLite
        _log_validation_event(document_type, apercu, file_path)

        # Pause interactive
        console.input(
            "\n[bold yellow]🔍 Appuyez sur Entrée pour confirmer la validation...[/bold yellow] "
        )
        console.print("[green]✅ Validation confirmée. Document approuvé pour envoi.[/green]")
        return "validation_confirmed"


class DuckDuckGoSearchToolCustom:
    """Outil de recherche web via DuckDuckGo pour CrewAI."""
    name: str = "duckduckgo_search"
    description: str = (
        "Effectue une recherche web via DuckDuckGo. "
        "Utilisez cet outil pour obtenir des informations en temps réel "
        "sur le marché, la concurrence, ou tout sujet d'actualité."
    )

    def _run(self, query: str) -> str:
        try:
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=5)
                if not results:
                    return "Aucun résultat trouvé pour cette requête."
                lines = []
                for i, r in enumerate(results, 1):
                    title = r.get("title", "Sans titre")
                    href = r.get("href", "N/A")
                    body = r.get("body", "")[:300]
                    lines.append(f"{i}. {title}\n   URL: {href}\n   {body}...")
                return "\n\n".join(lines)
        except Exception as exc:
            return f"Erreur recherche DuckDuckGo : {str(exc)}"


# ───────────────────────────────────────────────────────────────
# FONCTIONS UTILITAIRES
# ───────────────────────────────────────────────────────────────

def _log_validation_event(doc_type: str, content: str, file_path: Path) -> None:
    """Persiste un événement de validation dans SQLite."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS validations_humaines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            agent_name TEXT,
            document_type TEXT,
            file_path TEXT,
            content_hash TEXT,
            status TEXT
        )
        """
    )
    cursor.execute(
        """
        INSERT INTO validations_humaines (timestamp, agent_name, document_type, file_path, content_hash, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(),
            "commercial_agent",
            doc_type,
            str(file_path),
            str(hash(content) % 10**9),
            "pending_human_review",
        ),
    )
    conn.commit()
    conn.close()


def _enrichir_contexte_ci(besoin: str) -> str:
    """
    Enrichit le contexte de l'agent avec les données FAISS marché CI.
    """
    try:
        ctx = search_similar_context(besoin, top_k=3)
        if not ctx:
            return ""
        parts = ["\n# Contexte marché Côte d'Ivoire (FAISS) :"]
        for c in ctx:
            parts.append(f"- {c['title']} : {c['content'][:400]}")
        return "\n".join(parts)
    except Exception:
        return ""


def _transmettre_message_inter_agent(
    from_agent: str,
    to_agent: str,
    msg_type: str,
    payload: Dict[str, Any],
    project_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Wrapper de transmission inter-agents avec validation JSON obligatoire.
    """
    message = build_valid_message(
        from_agent=from_agent,
        to_agent=to_agent,
        message_type=msg_type,
        payload=payload,
        project_id=project_id,
    )
    validation = validate_agent_message(message)
    if not validation["valid"]:
        console.print(f"[red]❌ Échec validation JSON : {validation['message']}[/red]")
        return validation
    console.print(f"[dim]📤 Message inter-agent validé : {msg_type} → {to_agent}[/dim]")
    return validation


# ───────────────────────────────────────────────────────────────
# CLASSE PRINCIPALE — COMMERCIAL AGENT
# ───────────────────────────────────────────────────────────────

class CommercialAgent:
    """
    Agent commercial de La TEC.
    Gère la prospection, l'analyse des besoins clients et la rédaction
    de propositions commerciales localisées pour le marché ivoirien.
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.search_tool = DuckDuckGoSearchToolCustom()
        self.memoire_tool = MemoireMarcheCITool()
        self.validation_tool = ValidationHumaineTool()

        # ─── Backstory enrichi avec phrases types ivoiriennes (Recommandation 1) ───
        backstory_parts = [
            "Tu es le Commercial AGENT de La TEC, société de développement digital full-service basée à Abidjan.",
            "Tu t'exprimes en français professionnel adapté au marché ivoirien et ouest-africain francophone.",
            "Tu utilises les formules de politesse locales. Tu cites les prix en FCFA (1 EUR = 655 FCFA).",
            "Tu mentionnes les moyens de paiement locaux (Orange Money, Wave, MTN Mobile Money) quand pertinent.",
            "Tu connais les organismes clés : CEPICI, CCI-CI, ARTCI, BRVM.",
            "Tu adaptes tes propositions aux secteurs PME ivoiriennes : commerce, BTP, restauration, agriculture, transport.",
            "",
            "# Exemples de phrases types que tu utilises naturellement :",
        ]
        for i, phrase in enumerate(PHRASES_TYPES_IVOIRIENNES, 1):
            backstory_parts.append(f"{i}. \"{phrase}\"")
        backstory_parts.append(
            "\nTu es persuasif mais jamais agressif. Tu valorises la relation de confiance "
            "à long terme avec chaque prospect ivoirien."
        )

        self.agent = Agent(
            role="Commercial & Business Developer",
            goal=(
                "Prospecter des PME/ETI en Côte d'Ivoire, analyser leurs besoins digitaux, "
                "rédiger des propositions commerciales localisées en FCFA avec délais réalistes, "
                "et obtenir des rendez-vous qualifiés."
            ),
            backstory="\n".join(backstory_parts),
            llm=GEMINI_MODEL,
            temperature=TEMPERATURE,
            verbose=verbose,
            tools=[self.search_tool, self.memoire_tool, self.validation_tool],
        )

    # ─── TÂCHE 1 : Analyse du brief client ───
    def tache_analyse_besoin(self, brief_texte: str) -> BesoinClient:
        """
        Analyse le brief brut du client et structure les informations.
        """
        contexte_faiss = _enrichir_contexte_ci(brief_texte)

        tache = Task(
            description=(
                f"Analyse le besoin suivant d'un prospect ivoirien et extrais-en une structure JSON.\n\n"
                f"Brief brut :\n---\n{brief_texte}\n---\n"
                f"{contexte_faiss}\n\n"
                f"Réponds UNIQUEMENT avec un objet JSON contenant ces champs :\n"
                f"secteur_activite, taille_entreprise, besoin_principal, budget_estime, "
                f"delai_souhaite, moyen_contact_prefere, localisation.\n"
                f"Si une information manque, mets 'Non précisé'."
            ),
            expected_output="Un objet JSON structuré (BesoinClient).",
            agent=self.agent,
        )

        crew = Crew(agents=[self.agent], tasks=[tache], verbose=self.verbose)
        resultat = crew.kickoff()

        # Extraction et validation JSON
        try:
            raw = resultat.raw if hasattr(resultat, "raw") else str(resultat)
            # Nettoyage des balises markdown si présentes
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()
            data = json.loads(raw)
            besoin = BesoinClient(**data)
        except Exception as exc:
            console.print(f"[yellow]⚠️ Parsing JSON imparfait, fallback manuel : {exc}[/yellow]")
            besoin = BesoinClient(
                secteur_activite="Non précisé",
                taille_entreprise="PME",
                besoin_principal=brief_texte,
                localisation="Abidjan, Côte d'Ivoire",
            )

        # Transmission inter-agent validée
        _transmettre_message_inter_agent(
            from_agent="commercial",
            to_agent="chef_projet",
            msg_type="brief",
            payload={"besoin": besoin.dict(), "source": "prospection_directe"},
        )

        return besoin

    # ─── TÂCHE 2 : Prospection web (Recommandation 5) ───
    def tache_recherche_web(self, query: str) -> List[Dict[str, str]]:
        """
        Effectue une recherche web pour enrichir la prospection.
        """
        tache = Task(
            description=(
                f"Effectue une recherche web avec la requête : '{query}'\n"
                f"Résume les 3 premiers résultats pertinents pour le marché ivoirien "
                f"ou africain francophone. Pour chaque résultat, donne : titre, URL, résumé."
            ),
            expected_output="Liste de 3 résultats de recherche structurés.",
            agent=self.agent,
        )

        crew = Crew(agents=[self.agent], tasks=[tache], verbose=self.verbose)
        resultat = crew.kickoff()

        # Parsing simplifié
        lignes = str(resultat).split("\n")
        return [{"ligne": l.strip()} for l in lignes if l.strip()][:5]

    # ─── TÂCHE 3 : Rédaction proposition commerciale (Recommandation 3) ───
    def tache_rediger_proposition(
        self,
        besoin: BesoinClient,
        nom_prospect: str,
        services: List[str],
    ) -> PropositionCommerciale:
        """
        Rédige une proposition commerciale complète avec validation humaine.
        """
        contexte_faiss = _enrichir_contexte_ci(besoin.besoin_principal)

        tache = Task(
            description=(
                f"Rédige une proposition commerciale professionnelle pour :\n"
                f"Prospect : {nom_prospect}\n"
                f"Secteur : {besoin.secteur_activite}\n"
                f"Besoin : {besoin.besoin_principal}\n"
                f"Budget indicatif : {besoin.budget_estime or 'À définir'}\n"
                f"Délai souhaité : {besoin.delai_souhaite or 'À discuter'}\n"
                f"Services proposés : {', '.join(services)}\n\n"
                f"{contexte_faiss}\n\n"
                f"RÈGLES ABSOLUES :\n"
                f"- Prix en FCFA (conversion : 1 EUR = 655 FCFA).\n"
                f"- Mentionner Orange Money, Wave, MTN Mobile Money comme moyens de paiement.\n"
                f"- Délai réaliste en semaines pour le marché ivoirien.\n"
                f"- Ton professionnel, chaleureux, adapté au contexte local.\n"
                f"- Formules de politesse ivoiriennes (ouverture et fermeture).\n"
                f"- Structure : salutation, contexte, solution, prix/délai, conditions, CTA, signature.\n\n"
                f"Réponds avec un JSON contenant : titre, contenu_markdown, prix_total_fcfa, "
                f"prix_total_eur, delai_semaines, moyens_paiement, conditions."
            ),
            expected_output="Un objet JSON PropositionCommerciale complet.",
            agent=self.agent,
        )

        crew = Crew(agents=[self.agent], tasks=[tache], verbose=self.verbose)
        resultat = crew.kickoff()

        # Parsing JSON
        try:
            raw = resultat.raw if hasattr(resultat, "raw") else str(resultat)
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()
            data = json.loads(raw)
            prop = PropositionCommerciale(**data)
        except Exception as exc:
            console.print(f"[yellow]⚠️ Parsing proposition imparfait : {exc}[/yellow]")
            # Fallback : proposition minimale
            prop = PropositionCommerciale(
                titre=f"Proposition commerciale — {nom_prospect}",
                destinataire=nom_prospect,
                contenu_markdown=(
                    f"# Proposition commerciale\n\n"
                    f"**Destinataire :** {nom_prospect}\n"
                    f"**Besoin :** {besoin.besoin_principal}\n\n"
                    f"La TEC propose une solution sur mesure adaptée au marché ivoirien.\n\n"
                    f"**Budget :** À définir ensemble\n"
                    f"**Délai :** À discuter\n"
                    f"**Paiement :** Orange Money, Wave, virement bancaire\n\n"
                    f"Restant à votre entière disposition,\n"
                    f"**La TEC — The Engineering & Creation**\n"
                    f"Abidjan, Côte d'Ivoire"
                ),
                prix_total_fcfa=0,
                prix_total_eur=0,
                delai_semaines=0,
            )

        # ─── VALIDATION HUMAINE OBLIGATOIRE (Recommandation 3) ───
        apercu = (
            f"PROPOSITION COMMERCIALE\n"
            f"Destinataire : {prop.destinataire}\n"
            f"Titre : {prop.titre}\n"
            f"Prix : {prop.prix_total_fcfa:,} FCFA ({prop.prix_total_eur:,} EUR)\n"
            f"Délai : {prop.delai_semaines} semaines\n"
            f"Moyens de paiement : {', '.join(prop.moyens_paiement)}\n\n"
            f"--- APERÇU ---\n{prop.contenu_markdown[:1200]}\n..."
        )

        self.validation_tool._run(
            document_type="Proposition commerciale",
            apercu=apercu,
        )

        # Transmission inter-agent validée
        _transmettre_message_inter_agent(
            from_agent="commercial",
            to_agent="chef_projet",
            msg_type="client_document",
            payload={
                "type": "proposition_commerciale",
                "prospect": nom_prospect,
                "montant_fcfa": prop.prix_total_fcfa,
                "document": prop.contenu_markdown,
            },
            project_id=f"proj_{uuid.uuid4().hex[:8]}",
        )

        return prop

    # ─── Exécution complète du pipeline commercial ───
    def executer_pipeline(
        self,
        brief: str,
        nom_prospect: str,
        services: List[str],
    ) -> Dict[str, Any]:
        """
        Pipeline complet : Analyse → Recherche → Proposition.
        """
        console.print(Panel(
            f"[bold cyan]🚀 COMMERCIAL AGENT — Pipeline de prospection[/bold cyan]\n"
            f"Prospect : {nom_prospect}\n"
            f"Brief : {brief[:100]}...",
            title="La TEC",
            border_style="cyan",
        ))

        # Étape 1
        console.print("\n[bold]Étape 1/3 : Analyse du besoin client[/bold]")
        besoin = self.tache_analyse_besoin(brief)

        # Étape 2
        console.print("\n[bold]Étape 2/3 : Recherche web contextuelle[/bold]")
        recherche = self.tache_recherche_web(
            f"{besoin.secteur_activite} digital Côte d'Ivoire 2026"
        )

        # Étape 3
        console.print("\n[bold]Étape 3/3 : Rédaction de la proposition[/bold]")
        proposition = self.tache_rediger_proposition(besoin, nom_prospect, services)

        return {
            "besoin": besoin.dict(),
            "recherche": recherche,
            "proposition": proposition.dict(),
            "status": "pipeline_complete",
        }


# ───────────────────────────────────────────────────────────────
# POINT D'ENTRÉE CLI
# ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Commercial AGENT — La TEC (prospection & propositions)"
    )
    parser.add_argument(
        "--brief",
        type=str,
        required=True,
        help="Description du besoin du prospect",
    )
    parser.add_argument(
        "--prospect",
        type=str,
        required=True,
        help="Nom du prospect / entreprise",
    )
    parser.add_argument(
        "--services",
        type=str,
        nargs="+",
        default=["site web", "application mobile"],
        help="Services proposés (ex: --services site_web app_mobile)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Mode verbeux (défaut: True)",
    )

    args = parser.parse_args()

    agent = CommercialAgent(verbose=args.verbose)
    resultat = agent.executer_pipeline(
        brief=args.brief,
        nom_prospect=args.prospect,
        services=args.services,
    )

    console.print("\n[bold green]✅ Pipeline commercial terminé.[/bold green]")
    console.print(f"[dim]Proposition générée pour {args.prospect}[/dim]")


if __name__ == "__main__":
    main()