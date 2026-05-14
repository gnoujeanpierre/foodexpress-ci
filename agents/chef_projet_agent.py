"""
Chef de Projet AGENT - La TEC
Decoupe les specifications en taches, planifie, estime les ressources.
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


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


# --- SCHEMAS ---

class Tache(BaseModel):
    id: str = Field(default_factory=lambda: f"TACHE-{uuid.uuid4().hex[:6].upper()}")
    titre: str
    description: str
    responsable: str  # ex: "Developpeur Frontend", "Developpeur Backend", "Designer"
    duree_jours: int
    dependances: List[str] = []  # IDs des taches prerequises
    priorite: str = "Moyenne"  # Haute, Moyenne, Basse
    livrable: str  # Ce qui est produit a la fin de la tache


class Planning(BaseModel):
    date_debut: str
    date_fin: str
    duree_totale_semaines: int
    jalons: List[Dict[str, str]]  # [{"nom": "MVP livre", "date": "..."}]


class PlanProjet(BaseModel):
    titre: str
    projet_id: str = Field(default_factory=lambda: f"PROJ-{uuid.uuid4().hex[:8].upper()}")
    date_creation: str = Field(default_factory=lambda: datetime.now().strftime("%d/%m/%Y"))
    resume_spec: str
    taches: List[Tache]
    planning: Planning
    equipe_requise: List[str]  # ["1 Dev Frontend", "1 Dev Backend", "1 Designer UI/UX"]
    risques: List[str]
    budget_estime_fcfa: int
    notes: str = ""


# --- AGENT ---

class ChefProjetAgent:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.llm = _get_llm()
        self.agent = Agent(
            role="Chef de Projet Senior",
            goal="Transformer les specifications fonctionnelles en plan d'execution concret",
            backstory=(
                "Chef de projet experimente dans le digital en Afrique francophone. "
                "Expert en gestion agile, planification de sprints, et estimation des ressources. "
                "Maitrise les contraintes locales : reseau intermittent, paiement mobile, "
                "multilinguisme, et contexte PME ivoirien."
            ),
            llm=self.llm,
            verbose=verbose,
            allow_delegation=False,
        )

    def tache_decouper_spec(self, spec_json: str, nom_projet: str, budget_fcfa: Optional[int] = None) -> PlanProjet:
        budget_str = f"Budget total: {budget_fcfa:,} FCFA." if budget_fcfa else ""

        prompt = f"""
Tu es Chef de Projet pour le projet '{nom_projet}'.

Voici la specification fonctionnelle au format JSON :
---
{spec_json[:4000]}
---

{budget_str}

DECOMPOSE cette specification en un PLAN DE PROJET complet.

STRUCTURE JSON ATTENDUE :
{{
  "titre": "Plan de Projet - {nom_projet}",
  "resume_spec": "<resume de 3-4 lignes du besoin>",
  "taches": [
    {{
      "titre": "<nom de la tache>",
      "description": "<description detaillee>",
      "responsable": "<role: Developpeur Frontend|Developpeur Backend|Designer|DevOps|QA>",
      "duree_jours": <nombre entier>,
      "dependances": ["<ID tache prerequise ou vide>"],
      "priorite": "Haute|Moyenne|Basse",
      "livrable": "<ce qui est produit>"
    }}
  ],
  "planning": {{
    "date_debut": "{datetime.now().strftime('%d/%m/%Y')}",
    "date_fin": "<date estimée JJ/MM/AAAA>",
    "duree_totale_semaines": <nombre entier>,
    "jalons": [
      {{"nom": "<nom du jalon>", "date": "<JJ/MM/AAAA>"}}
    ]
  }},
  "equipe_requise": ["<1 Dev Frontend>", "<1 Dev Backend>", "<1 Designer UI/UX>"],
  "risques": ["<risque 1>", "<risque 2>"],
  "budget_estime_fcfa": <nombre entier>,
  "notes": "<notes complementaires>"
}}

REGLES ABSOLUES :
- Minimum 8 taches couvrant tout le cycle de vie (conception, dev frontend, dev backend, integration, tests, deploiement).
- Les dependances doivent etre coherentes (une tache ne depend pas d'elle-meme).
- Duree realiste pour le marche ivoirien (tenir compte du reseau, des validations client).
- Mentionner les specificites locales dans les risques (reseau, paiement mobile, delais de validation).
- Budget en FCFA, realiste par rapport au marche local.
- Reponds UNIQUEMENT avec le JSON valide, sans texte autour.
"""

        task = Task(
            description=prompt,
            expected_output="JSON valide representant le plan de projet complet.",
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

            # Validation et injection de securite
            if "titre" not in data or not data["titre"]:
                data["titre"] = f"Plan de Projet - {nom_projet}"
            if "projet_id" not in data:
                data["projet_id"] = f"PROJ-{uuid.uuid4().hex[:8].upper()}"
            if "date_creation" not in data:
                data["date_creation"] = datetime.now().strftime("%d/%m/%Y")

            # Convertir les taches en objets Tache
            taches = []
            for i, t in enumerate(data.get("taches", [])):
                if "id" not in t or not t["id"]:
                    t["id"] = f"TACHE-{uuid.uuid4().hex[:6].upper()}"
                taches.append(Tache(**t))
            data["taches"] = taches

            # Convertir le planning
            if "planning" in data:
                data["planning"] = Planning(**data["planning"])

            return PlanProjet(**data)
        except Exception as e:
            print(f"[WARN] Parsing plan imparfait ({e}), fallback minimal.")
            return PlanProjet(
                titre=f"Plan de Projet - {nom_projet}",
                resume_spec="Application mobile de livraison de repas",
                taches=[
                    Tache(
                        titre="Conception UI/UX",
                        description="Maquettes et wireframes de l'application",
                        responsable="Designer UI/UX",
                        duree_jours=7,
                        priorite="Haute",
                        livrable="Maquettes Figma"
                    ),
                    Tache(
                        titre="Developpement Backend API",
                        description="API REST avec authentification et gestion des commandes",
                        responsable="Developpeur Backend",
                        duree_jours=14,
                        dependances=["TACHE-001"],
                        priorite="Haute",
                        livrable="API fonctionnelle"
                    ),
                    Tache(
                        titre="Developpement Frontend Mobile",
                        description="Application mobile Flutter/React Native",
                        responsable="Developpeur Frontend",
                        duree_jours=21,
                        dependances=["TACHE-001"],
                        priorite="Haute",
                        livrable="App mobile fonctionnelle"
                    ),
                    Tache(
                        titre="Integration et Tests",
                        description="Tests end-to-end et correction des bugs",
                        responsable="QA / Developpeurs",
                        duree_jours=7,
                        dependances=["TACHE-002", "TACHE-003"],
                        priorite="Moyenne",
                        livrable="Application testee"
                    ),
                    Tache(
                        titre="Deploiement",
                        description="Mise en production sur les stores et serveurs",
                        responsable="DevOps",
                        duree_jours=3,
                        dependances=["TACHE-004"],
                        priorite="Haute",
                        livrable="App en production"
                    ),
                ],
                planning=Planning(
                    date_debut=datetime.now().strftime("%d/%m/%Y"),
                    date_fin=(datetime.now() + timedelta(days=52)).strftime("%d/%m/%Y"),
                    duree_totale_semaines=8,
                    jalons=[
                        {"nom": "Maquettes validees", "date": (datetime.now() + timedelta(days=7)).strftime("%d/%m/%Y")},
                        {"nom": "MVP Backend", "date": (datetime.now() + timedelta(days=21)).strftime("%d/%m/%Y")},
                        {"nom": "MVP Complet", "date": (datetime.now() + timedelta(days=42)).strftime("%d/%m/%Y")},
                        {"nom": "Livraison", "date": (datetime.now() + timedelta(days=52)).strftime("%d/%m/%Y")},
                    ]
                ),
                equipe_requise=["1 Designer UI/UX", "1 Developpeur Backend", "1 Developpeur Frontend", "1 QA"],
                risques=[
                    "Reseau intermittent en Cote d Ivoire - necessite mode offline",
                    "Delais de validation client - prevoir des points hebdomadaires",
                    "Integration paiement mobile (Wave, Orange Money) - complexite API",
                ],
                budget_estime_fcfa=budget_fcfa or 5000000,
                notes="Plan genere automatiquement par l'agent Chef de Projet La TEC."
            )

    def executer_pipeline(
        self, spec_json: str, nom_projet: str, client: str, budget_fcfa: Optional[int] = None
    ) -> Dict[str, Any]:
        print(f"\n=== CHEF DE PROJET — Pipeline {nom_projet} ===")
        
        print("[Etape 1/1] Decoupage de la spec en plan d'execution...")
        plan = self.tache_decouper_spec(spec_json, nom_projet, budget_fcfa)
        
        print(f"\n   ✅ Plan: {plan.titre}")
        print(f"   📋 Taches: {len(plan.taches)}")
        print(f"   📅 Duree: {plan.planning.duree_totale_semaines} semaines")
        print(f"   👥 Equipe: {', '.join(plan.equipe_requise)}")
        print(f"   💰 Budget estime: {plan.budget_estime_fcfa:,} FCFA")
        print(f"   ⚠️  Risques: {len(plan.risques)} identifies")

        # Sauvegarde
        log_dir = Path(__file__).resolve().parent.parent / "logs" / "plans"
        log_dir.mkdir(parents=True, exist_ok=True)
        filepath = log_dir / f"plan_{nom_projet}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Serialisation manuelle pour eviter les problemes Pydantic
        plan_dict = {
            "titre": plan.titre,
            "projet_id": plan.projet_id,
            "date_creation": plan.date_creation,
            "resume_spec": plan.resume_spec,
            "taches": [t.model_dump() for t in plan.taches],
            "planning": plan.planning.model_dump() if plan.planning else {},
            "equipe_requise": plan.equipe_requise,
            "risques": plan.risques,
            "budget_estime_fcfa": plan.budget_estime_fcfa,
            "notes": plan.notes,
        }
        filepath.write_text(json.dumps(plan_dict, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"   💾 Sauvegarde: {filepath}")

        return {
            "plan": plan_dict,
            "fichier": str(filepath),
            "status": "pipeline_complete",
        }


def main():
    parser = argparse.ArgumentParser(description="Chef de Projet AGENT — La TEC")
    parser.add_argument("--spec", required=True, help="Chemin vers le fichier JSON de specification")
    parser.add_argument("--projet", required=True, help="Nom du projet")
    parser.add_argument("--client", required=True, help="Nom du client")
    parser.add_argument("--budget", type=int, default=None, help="Budget en FCFA")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    spec_content = Path(args.spec).read_text(encoding="utf-8")
    agent = ChefProjetAgent(verbose=args.verbose)
    result = agent.executer_pipeline(
        spec_json=spec_content, nom_projet=args.projet, client=args.client, budget_fcfa=args.budget
    )
    print(f"\n✅ Pipeline Chef de Projet termine. Fichier: {result['fichier']}")


if __name__ == "__main__":
    main()
