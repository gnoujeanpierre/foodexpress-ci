"""
Orchestrateur La TEC — Coordination multi-agents
Workflow: Commercial -> Analyste Fonctionnel
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.commercial_agent import CommercialAgent
from agents.analyste_fonctionnel_agent import AnalysteFonctionnelAgent


class OrchestrateurLaTEC:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.commercial = CommercialAgent(verbose=verbose)
        self.analyste = AnalysteFonctionnelAgent(verbose=verbose)

    def run_prospect_complet(
        self,
        brief: str,
        nom_prospect: str,
        client_final: str,
        services: list,
        budget_fcfa: int = None,
    ) -> Dict[str, Any]:
        print("=" * 60)
        print("   LA TEC — ORCHESTRATEUR MULTI-AGENTS")
        print("   Workflow: Commercial -> Analyste Fonctionnel")
        print("=" * 60)

        # --- ETAPE 1: Commercial ---
        print(f"\\n>>> [1/2] AGENT COMMERCIAL: Prospection {nom_prospect}")
        result_commercial = self.commercial.executer_pipeline(
            brief=brief, nom_prospect=nom_prospect, services=services,
        )
        besoin = result_commercial["besoin"]
        proposition = result_commercial["proposition"]

        print(f"\\n   Besoin: {besoin['besoin_principal'][:80]}...")
        print(f"   Proposition: {proposition['titre']}")
        print(f"   Prix: {proposition['prix_total_fcfa']:,} FCFA")

        # --- ETAPE 2: Analyste Fonctionnel ---
        print(f"\\n>>> [2/2] AGENT ANALYSTE FONCTIONNEL: Specification")
        brief_enrichi = (
            f"PROSPECT: {nom_prospect}\\n"
            f"BESOIN: {besoin['besoin_principal']}\\n"
            f"SECTEUR: {besoin['secteur_activite']}\\n"
            f"TAILLE: {besoin['taille_entreprise']}\\n"
            f"LOCALISATION: {besoin['localisation']}\\n\\n"
            f"PROPOSITION:\\n"
            f"Services: {', '.join(services)}\\n"
            f"Prix: {proposition['prix_total_fcfa']:,} FCFA\\n"
            f"Delai: {proposition['delai_semaines']} semaines\\n\\n"
            f"BRIEF ORIGINAL:\\n{brief}"
        )

        result_analyste = self.analyste.executer_pipeline(
            brief=brief_enrichi,
            nom_projet=f"Projet_{nom_prospect.replace(' ', '_')}",
            client=client_final,
            budget_fcfa=budget_fcfa,
        )

        print(f"\\n   Spec sauvegardee: {result_analyste['fichier']}")

        return {
            "workflow": "commercial -> analyste_fonctionnel",
            "prospect": nom_prospect,
            "client_final": client_final,
            "besoin": besoin,
            "proposition_commerciale": proposition,
            "specification_fonctionnelle": result_analyste["specification"],
            "fichier_spec": result_analyste["fichier"],
            "status": "workflow_complete",
        }


def main():
    parser = argparse.ArgumentParser(description="Orchestrateur La TEC")
    parser.add_argument("--brief", required=True, help="Brief du prospect")
    parser.add_argument("--prospect", required=True, help="Nom du prospect")
    parser.add_argument("--client", required=True, help="Nom du client final")
    parser.add_argument("--services", nargs="+", default=["site web", "app mobile"])
    parser.add_argument("--budget", type=int, default=None)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    orchestrateur = OrchestrateurLaTEC(verbose=args.verbose)
    resultat = orchestrateur.run_prospect_complet(
        brief=args.brief,
        nom_prospect=args.prospect,
        client_final=args.client,
        services=args.services,
        budget_fcfa=args.budget,
    )

    rapport_dir = Path(__file__).resolve().parent.parent / "logs" / "rapports"
    rapport_dir.mkdir(parents=True, exist_ok=True)
    rapport_file = rapport_dir / f"rapport_{args.prospect.replace(' ', '_')}.json"
    rapport_file.write_text(
        json.dumps(resultat, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("\\n" + "=" * 60)
    print("   WORKFLOW TERMINE AVEC SUCCES")
    print(f"   Rapport: {rapport_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
