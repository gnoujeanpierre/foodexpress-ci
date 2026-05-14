"""
Agent Analyste Fonctionnel & Business Analyst — La TEC
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# from dotenv import load_dotenv
# load_dotenv()

from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.json_validator import build_valid_message

LOG_DIR = Path(__file__).resolve().parent.parent / "logs" / "a_valider"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def _get_llm() -> LLM:
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Clé API manquante. Définissez OPENROUTER_API_KEY dans .env")
    return LLM(
        model="openai/gpt-4o-mini",
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.3,
    )


class AnalysteFonctionnelAgent:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.llm = _get_llm()
        self.agent = Agent(
            role="Analyste Fonctionnel & Business Analyst",
            goal="Produire des spécifications fonctionnelles complètes pour le marché ivoirien",
            backstory=(
                "Tu es un analyste fonctionnel senior spécialisé dans les projets digitaux "
                "en Côte d'Ivoire. Tu maîtrises les spécificités locales : paiement mobile "
                "(Wave, Orange Money), réseau intermittent, multilinguisme, et contexte PME."
            ),
            llm=self.llm,
            verbose=verbose,
            allow_delegation=False,
        )

    def tache_analyse_besoin_fonctionnel(
        self, brief: str, nom_projet: str, client: str, budget_fcfa: Optional[int] = None
    ) -> str:
        contexte_marche = (
            "Contexte marché Côte d'Ivoire (2026) : "
            "- Délais indicatifs : app mobile simple 4-6 sem, complexe 8-16 sem. "
            "- Prix apps mobiles CI : simple 800K-1.5M FCFA, e-commerce 2M-4M, "
            "  sur mesure avec backend 3.5M-8M, complexe (livraison, géoloc, paiement) 5M-15M FCFA. "
            "- Maintenance annuelle : 15-25% du coût initial. "
            "- Paiements mobiles dominants : Wave, Orange Money, MTN MoMo."
        )
        budget_str = f"Budget indicatif : {budget_fcfa:,} FCFA." if budget_fcfa else ""

        prompt_spec = f"""
Tu es Analyste Fonctionnel pour le projet '{nom_projet}' du client '{client}'.

Analyse le brief suivant et produis une SPÉCIFICATION FONCTIONNELLE COMPLÈTE en JSON.

Brief brut :
---
{brief}
---

# Contexte marché Côte d'Ivoire :
{contexte_marche}
{budget_str}

STRUCTURE JSON ATTENDUE :
{{
  "titre": "Spécification Fonctionnelle — {nom_projet}",
  "version": "1.0",
  "date_redaction": "{datetime.now().strftime('%d/%m/%Y')}",
  "redacteur": "Analyste Fonctionnel — La TEC",
  "projet": "{nom_projet}",
  "contexte": "<contexte métier détaillé>",
  "objectifs": ["<objectif 1 mesurable>", "<objectif 2>"],
  "perimetre_inclus": ["<scope 1>", "<scope 2>"],
  "perimetre_exclu": ["<hors scope 1>", "<hors scope 2>"],
  "acteurs": ["<acteur 1>", "<acteur 2>"],
  "users_stories": [
    {{
      "id": "US-001",
      "en_tant_que": "<rôle>",
      "je_veux": "<action>",
      "afin_de": "<bénéfice>",
      "critere_acceptation": "<critère testable>",
      "priorite": "Haute|Moyenne|Basse",
      "effort_jours": <float|null>
    }}
  ],
  "regles_metier": [
    {{
      "id": "RM-001",
      "libelle": "<titre règle>",
      "description": "<description détaillée>",
      "declencheur": "<événement>",
      "consequence": "<action>",
      "priorite": "Haute|Moyenne|Basse"
    }}
  ],
  "processus_cles": ["<description processus 1>", "<processus 2>"],
  "maquettes_description": "<description des écrans principaux>",
  "contraintes_techniques": ["<contrainte 1>", "<contrainte 2>"],
  "contraintes_reglementaires": ["<contrainte légale 1>"],
  "livrables_attendus": ["<livrable 1>", "<livrable 2>"],
  "langue": "français",
  "devise": "FCFA"
}}

RÈGLES ABSOLUES :
- Minimum 5 users stories avec critères d'acceptation testables.
- Minimum 3 règles métier formalisées.
- Mentionner les spécificités locales : paiement mobile, réseau intermittent, langues.
- Les acteurs doivent refléter la réalité ivoirienne (client final, vendeur, livreur, admin, etc.).
- Réponds UNIQUEMENT avec le JSON valide, sans texte autour.
"""

        task = Task(
            description=prompt_spec,
            expected_output="Un document JSON valide représentant la spécification fonctionnelle complète.",
            agent=self.agent,
        )
        crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential, verbose=self.verbose)
        resultat = crew.kickoff()
        return str(resultat)

    def tache_recherche_contextuelle(self, query: str, nom_projet: str) -> str:
        prompt = (
            f"Effectue une analyse de marché pour '{nom_projet}' en Côte d'Ivoire. "
            f"Requête : {query}. Résume en 3 points clés avec sources."
        )
        task = Task(description=prompt, expected_output="Un résumé structuré du contexte marché.", agent=self.agent)
        crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential, verbose=self.verbose)
        return str(crew.kickoff())

    def tache_rediger_specifications_completes(self, spec_brute: str, client: str) -> str:
        prompt = (
            "Reprends la spécification suivante et assure-toi qu'elle est "
            "complète, cohérente et prête pour transmission au Chef de Projet. "
            f"Client : {client}.\n\n{spec_brute}"
        )
        task = Task(description=prompt, expected_output="La spécification fonctionnelle finalisée.", agent=self.agent)
        crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential, verbose=self.verbose)
        return str(crew.kickoff())

    def _transmettre_message_inter_agent(
        self, expediteur: str, destinataire: str, type_message: str,
        contenu: str, projet_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {"content": contenu, "data": {}}
        try:
            msg = build_valid_message(
                from_agent=expediteur, to_agent=destinataire,
                message_type=type_message, payload=payload,
                project_id=projet_id, priority="high",
            )
            return {"success": True, "message": msg}
        except ValueError as exc:
            return {"success": False, "error": str(exc)}

    def executer_pipeline(
        self, brief: str, nom_projet: str, client: str, budget_fcfa: Optional[int] = None
    ) -> Dict[str, Any]:
        print(f"\n🚀 Lancement pipeline Analyste Fonctionnel — {nom_projet}")

        try:
            recherche = self.tache_recherche_contextuelle(f"{nom_projet} digital Côte d'Ivoire", nom_projet)
            if self.verbose:
                print("\n📊 Contexte marché :", recherche[:300], "...")
        except Exception as exc:
            print(f"⚠️ Recherche contextuelle ignorée : {exc}")
            recherche = ""

        print("\n📝 Génération de la spécification fonctionnelle...")
        spec = self.tache_analyse_besoin_fonctionnel(brief=brief, nom_projet=nom_projet, client=client, budget_fcfa=budget_fcfa)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        uid = uuid.uuid4().hex[:6]
        filename = f"spec_{timestamp}_{uid}.md"
        filepath = LOG_DIR / filename
        filepath.write_text(spec, encoding="utf-8")
        print(f"\n💾 Document sauvegardé : {filepath}")

        print("\n" + "─" * 60)
        print("📋 VALIDATION REQUISE — ANALYSTE FONCTIONNEL")
        print("─" * 60)
        print(f"Type de document : Spécification Fonctionnelle")
        print(f"Projet : {nom_projet}")
        print(f"Client : {client}")
        print("\nVérifiez la cohérence métier, la complétude et la faisabilité.")
        input("\n🔔 Appuyez sur Entrée pour confirmer la validation... ")
        print("✅ Validation confirmée. Document approuvé pour transmission.")

        print("\n🔧 Finalisation de la spécification...")
        spec_final = self.tache_rediger_specifications_completes(spec, client)

        print("\n📡 Transmission au Chef de Projet...")
        transmission = self._transmettre_message_inter_agent(
            expediteur="analyste_fonctionnel",
            destinataire="chef_projet",
            type_message="specification_finalisee",
            contenu=spec_final,
            projet_id=nom_projet,
        )

        if transmission["success"]:
            print("✅ Transmission réussie.")
        else:
            print(f"⚠️ Transmission échouée : {transmission.get('error')}")
            print("   Le document reste disponible localement.")

        return {"specification": spec_final, "fichier": str(filepath), "transmission": transmission}


def main():
    parser = argparse.ArgumentParser(description="Agent Analyste Fonctionnel — La TEC")
    parser.add_argument("--brief", required=True, help="Brief du client")
    parser.add_argument("--projet", required=True, help="Nom du projet")
    parser.add_argument("--client", required=True, help="Nom du client")
    parser.add_argument("--budget-fcfa", type=int, default=None, help="Budget indicatif en FCFA")
    parser.add_argument("--verbose", action="store_true", help="Mode verbeux")
    args = parser.parse_args()

    agent = AnalysteFonctionnelAgent(verbose=args.verbose)
    resultat = agent.executer_pipeline(
        brief=args.brief, nom_projet=args.projet, client=args.client, budget_fcfa=args.budget_fcfa
    )

    print("\n" + "═" * 60)
    print("📋 PIPELINE TERMINÉ")
    print("═" * 60)
    print(f"Fichier : {resultat['fichier']}")
    print(f"Transmission : {'✅ OK' if resultat['transmission']['success'] else '⚠️ Échec'}")


if __name__ == "__main__":
    main()
