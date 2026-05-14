"""
Commercial AGENT - La TEC (version light)
Prospection et propositions commerciales.
"""

import argparse
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from crewai import Agent, Task, Crew, Process
from pydantic import BaseModel, Field


# --- SCHEMAS ---

class BesoinClient(BaseModel):
    secteur_activite: str = Field(default="Non precise")
    taille_entreprise: str = Field(default="PME")
    besoin_principal: str
    budget_estime: Optional[str] = None
    delai_souhaite: Optional[str] = None
    moyen_contact_prefere: str = "WhatsApp / email"
    localisation: str = "Abidjan, Cote d Ivoire"


class PropositionCommerciale(BaseModel):
    titre: str
    destinataire: str
    contenu_markdown: str
    prix_total_fcfa: int = 0
    prix_total_eur: int = 0
    delai_semaines: int = 0
    moyens_paiement: List[str] = ["Orange Money", "Wave", "Virement"]
    conditions: str = "50% a la commande, 50% a la livraison"
    date_emission: str = Field(default_factory=lambda: datetime.now().strftime("%d/%m/%Y"))


# --- AGENT ---

class CommercialAgent:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.agent = Agent(
            role="Commercial Senior",
            goal="Prospection B2B et propositions commerciales en Afrique francophone",
            backstory=(
                "Expert en prospection digitale en Cote d Ivoire. "
                "Maitrise les specificites locales : paiement mobile, contexte PME, delais realistes."
            ),
            verbose=verbose,
            allow_delegation=False,
        )

    def tache_analyse_besoin(self, brief_texte: str) -> BesoinClient:
        prompt = (
            f"Analyse ce brief client et extrais les informations structurees:\\n"
            f"{brief_texte}\\n\\n"
            f"Reponds UNIQUEMENT avec un JSON valide contenant: "
            f"secteur_activite, taille_entreprise, besoin_principal, "
            f"budget_estime, delai_souhaite, moyen_contact_prefere, localisation."
        )
        task = Task(
            description=prompt,
            expected_output="JSON valide avec les champs BesoinClient.",
            agent=self.agent,
        )
        crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential, verbose=self.verbose)
        resultat = crew.kickoff()

        try:
            raw = str(resultat)
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()
            data = json.loads(raw)
            return BesoinClient(**data)
        except Exception as e:
            print(f"[WARN] Parsing imparfait ({e}), fallback.")
            return BesoinClient(besoin_principal=brief_texte)

    def tache_rediger_proposition(
        self, besoin: BesoinClient, nom_prospect: str, services: List[str]
    ) -> PropositionCommerciale:
        prompt = (
            f"Redige une proposition commerciale pour {nom_prospect}.\\n"
            f"Besoin: {besoin.besoin_principal}\\n"
            f"Secteur: {besoin.secteur_activite}\\n"
            f"Services proposes: {', '.join(services)}\\n\\n"
            f"Regles ABSOLUES:\\n"
            f"- Prix en FCFA (1 EUR = 655 FCFA)\\n"
            f"- Mentionner Orange Money et Wave comme moyens de paiement\\n"
            f"- Delai realiste en semaines pour le marche ivoirien\\n"
            f"- Ton professionnel, chaleureux, adapte au contexte local\\n"
            f"- Structure: salutation, contexte, solution, prix/delai, conditions, CTA, signature\\n\\n"
            f"Reponds avec un JSON contenant: titre, contenu_markdown, prix_total_fcfa, "
            f"prix_total_eur, delai_semaines, moyens_paiement, conditions."
        )
        task = Task(
            description=prompt,
            expected_output="JSON valide PropositionCommerciale.",
            agent=self.agent,
        )
        crew = Crew(agents=[self.agent], tasks=[task], process=Process.sequential, verbose=self.verbose)
        resultat = crew.kickoff()

        try:
            raw = str(resultat)
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()
            data = json.loads(raw)
            return PropositionCommerciale(**data)
        except Exception as e:
            print(f"[WARN] Parsing proposition imparfait ({e}), fallback.")
            return PropositionCommerciale(
                titre=f"Proposition - {nom_prospect}",
                destinataire=nom_prospect,
                contenu_markdown=(
                    f"# Proposition commerciale\\n\\n"
                    f"**Destinataire:** {nom_prospect}\\n\\n"
                    f"**Besoin:** {besoin.besoin_principal}\\n\\n"
                    f"La TEC propose une solution sur mesure adaptee au marche ivoirien.\\n\\n"
                    f"**Paiement:** Orange Money, Wave, virement bancaire\\n\\n"
                    f"Restant a votre entiere disposition,\\n"
                    f"**La TEC — The Engineering & Creation**\\n"
                    f"Abidjan, Cote d Ivoire"
                ),
            )

    def executer_pipeline(
        self, brief: str, nom_prospect: str, services: List[str]
    ) -> Dict[str, Any]:
        print(f"\\n=== COMMERCIAL AGENT — Pipeline {nom_prospect} ===")
        
        print("[Etape 1/2] Analyse du besoin...")
        besoin = self.tache_analyse_besoin(brief)
        
        print("[Etape 2/2] Redaction de la proposition...")
        proposition = self.tache_rediger_proposition(besoin, nom_prospect, services)
        
        return {
            "besoin": besoin.model_dump(),
            "proposition": proposition.model_dump(),
            "status": "pipeline_complete",
        }


def main():
    parser = argparse.ArgumentParser(description="Commercial AGENT — La TEC")
    parser.add_argument("--brief", required=True, help="Description du besoin")
    parser.add_argument("--prospect", required=True, help="Nom du prospect")
    parser.add_argument("--services", nargs="+", default=["site web", "app mobile"])
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    agent = CommercialAgent(verbose=args.verbose)
    result = agent.executer_pipeline(
        brief=args.brief, nom_prospect=args.prospect, services=args.services
    )
    print(f"\\n✅ Pipeline termine pour {args.prospect}")
    print(f"   Proposition: {result['proposition']['titre']}")


if __name__ == "__main__":
    main()
