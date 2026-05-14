"""
Agent Analyste Fonctionnel — La TEC (version light)
Specifications fonctionnelles.
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM


def _get_llm() -> LLM:
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Cle API manquante. Definissez OPENROUTER_API_KEY dans .env")
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
            role="Analyste Fonctionnel Senior",
            goal="Produire des specifications fonctionnelles completes",
            backstory=(
                "Analyste fonctionnel senior specialise dans les projets digitaux "
                "en Cote d Ivoire. Maitrise les specificites locales."
            ),
            llm=self.llm,
            verbose=verbose,
            allow_delegation=False,
        )

    def tache_analyse_besoin_fonctionnel(
        self, brief: str, nom_projet: str, client: str, budget_fcfa: Optional[int] = None
    ) -> str:
        contexte_marche = (
            "Contexte marche Cote d Ivoire (2026): "
            "Delais apps simples 4-6 sem, complexes 8-16 sem. "
            "Prix: simple 800K-1.5M FCFA, e-commerce 2M-4M, sur mesure 3.5M-8M FCFA. "
            "Maintenance: 15-25% du cout initial. Paiements: Wave, Orange Money, MTN MoMo."
        )
        budget_str = f"Budget: {budget_fcfa:,} FCFA." if budget_fcfa else ""

        prompt = f"""
Tu es Analyste Fonctionnel pour le projet '{nom_projet}' du client '{client}'.

Analyse le brief et produis une SPECIFICATION FONCTIONNELLE COMPLETE en JSON.

Brief:
---
{brief}
---

{contexte_marche}
{budget_str}

STRUCTURE JSON:
{{
  "titre": "Specification Fonctionnelle - {nom_projet}",
  "version": "1.0",
  "date_redaction": "{datetime.now().strftime('%d/%m/%Y')}",
  "contexte": "<contexte metier detaille>",
  "objectifs": ["<<objectif 1>"],
  "perimetre_inclus": ["<<scope 1>"],
  "perimetre_exclu": ["<<hors scope 1>"],
  "acteurs": ["<<acteur 1>"],
  "users_stories": [
    {{
      "id": "US-001",
      "en_tant_que": "<role>",
      "je_veux": "<action>",
      "afin_de": "<benefice>",
      "critere_acceptation": "<critere testable>",
      "priorite": "Haute|Moyenne|Basse"
    }}
  ],
  "regles_metier": [
    {{
      "id": "RM-001",
      "libelle": "<titre>",
      "description": "<description>",
      "priorite": "Haute|Moyenne|Basse"
    }}
  ],
  "contraintes_techniques": ["<<contrainte 1>"],
  "livrables_attendus": ["<<livrable 1>"],
  "langue": "francais",
  "devise": "FCFA"
}}

REGLES:
- Minimum 5 users stories avec criteres d acceptation testables.
- Minimum 3 regles metier formalisees.
- Mentionner specificites locales: paiement mobile, reseau intermittent.
- Reponds UNIQUEMENT avec le JSON valide, sans texte autour.
"""

        task = Task(
            description=prompt,
            expected_output="JSON valide representant la specification fonctionnelle complete.",
            agent=self.agent,
        )
        crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential, verbose=self.verbose)
        return str(crew.kickoff())

    def executer_pipeline(
        self, brief: str, nom_projet: str, client: str, budget_fcfa: Optional[int] = None
    ) -> Dict[str, Any]:
        print(f"\\n=== ANALYSTE FONCTIONNEL — Pipeline {nom_projet} ===")

        try:
            spec = self.tache_analyse_besoin_fonctionnel(brief, nom_projet, client, budget_fcfa)
            print("[OK] Specification generee.")
        except Exception as e:
            print(f"[ERREUR] Generation spec: {e}")
            spec = f"ERREUR: {str(e)}"

        log_dir = Path(__file__).resolve().parent.parent / "logs" / "specifications"
        log_dir.mkdir(parents=True, exist_ok=True)
        filepath = log_dir / f"spec_{nom_projet}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath.write_text(f"# Spec {nom_projet}\\n\\n{spec}", encoding="utf-8")
        print(f"[OK] Sauvegarde: {filepath}")

        return {
            "specification": spec,
            "fichier": str(filepath),
            "status": "pipeline_complete",
        }


def main():
    parser = argparse.ArgumentParser(description="Agent Analyste Fonctionnel — La TEC")
    parser.add_argument("--brief", required=True, help="Brief du client")
    parser.add_argument("--projet", required=True, help="Nom du projet")
    parser.add_argument("--client", required=True, help="Nom du client")
    parser.add_argument("--budget-fcfa", type=int, default=None)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    agent = AnalysteFonctionnelAgent(verbose=args.verbose)
    result = agent.executer_pipeline(
        brief=args.brief, nom_projet=args.projet, client=args.client, budget_fcfa=args.budget_fcfa
    )
    print(f"\\n✅ Pipeline termine. Fichier: {result['fichier']}")


if __name__ == "__main__":
    main()
