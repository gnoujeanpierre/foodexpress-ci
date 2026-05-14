# tools\json_validator.py
"""
Module de validation JSON inter-agents pour La TEC.
Recommandation 4 : Validateur JSON inter-agents.

Ce module contient validate_agent_message() qui vérifie chaque message
inter-agents avant transmission. En cas d'erreur : log dans SQLite +
message d'erreur structuré renvoyé à l'agent émetteur.
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ValidationError, validator


# ───────────────────────────────────────────────────────────────
# CONFIGURATION
# ───────────────────────────────────────────────────────────────

# Chemin vers la base SQLite partagée (même base que memory_manager.py)
_DB_PATH = Path(__file__).resolve().parent.parent / "memory" / "la_tec_memory.db"

# Types de messages inter-agents autorisés
_ALLOWED_MESSAGE_TYPES = {
    "task_assignment",    # Attribution d'une tâche
    "result",             # Résultat d'une tâche
    "query",              # Requête d'information
    "decision",           # Décision à valider
    "status_update",      # Mise à jour de statut
    "brief",              # Brief de projet
    "notification",       # Notification générale
    "validation_request", # Demande de validation humaine
    "client_document",    # Document destiné au client
    "specification_fonctionnelle",  # Spécification fonctionnelle produite par l'analyste
    "specification_finalisee",      # Spécification validée et finalisée
}


# ───────────────────────────────────────────────────────────────
# SCHÉMAS PYDANTIC
# ───────────────────────────────────────────────────────────────

class AgentMessagePayload(BaseModel):
    """Schéma de la charge utile d'un message inter-agents."""
    content: str = Field(
        ...,
        description="Contenu textuel principal du message"
    )
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Données structurées additionnelles (JSON serialisable)"
    )

    class Config:
        # Autorise les champs supplémentaires pour la flexibilité CrewAI
        extra = "allow"


class AgentMessage(BaseModel):
    """Schéma complet d'un message inter-agents La TEC."""
    message_id: str = Field(
        ...,
        description="Identifiant unique du message (UUID ou ULID)"
    )
    from_agent: str = Field(
        ...,
        description="Identifiant de l'agent émetteur (ex: chef_projet, commercial)"
    )
    to_agent: str = Field(
        ...,
        description="Identifiant de l'agent destinataire (ex: dev_frontend, qa)"
    )
    message_type: str = Field(
        ...,
        description="Type de message selon la taxonomie La TEC"
    )
    payload: Dict[str, Any] = Field(
        ...,
        description="Charge utile du message (dict Python)"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Horodatage ISO 8601 de l'émission"
    )
    project_id: Optional[str] = Field(
        None,
        description="Identifiant du projet concerné"
    )
    priority: Optional[str] = Field(
        default="normal",
        description="Priorité : low, normal, high, urgent"
    )

    @validator("message_type")
    def _check_message_type(cls, v: str) -> str:
        """Vérifie que le type de message est autorisé."""
        if v not in _ALLOWED_MESSAGE_TYPES:
            raise ValueError(
                f"Type '{v}' non autorisé. Types acceptés : {_ALLOWED_MESSAGE_TYPES}"
            )
        return v

    @validator("priority")
    def _check_priority(cls, v: Optional[str]) -> Optional[str]:
        """Vérifie la priorité."""
        if v is not None and v not in {"low", "normal", "high", "urgent"}:
            raise ValueError("Priorité doit être : low, normal, high, urgent")
        return v

    @validator("from_agent", "to_agent")
    def _check_agent_id(cls, v: str) -> str:
        """Vérifie que l'identifiant d'agent n'est pas vide."""
        if not v or not v.strip():
            raise ValueError("L'identifiant d'agent ne peut pas être vide")
        return v.strip()

    class Config:
        extra = "allow"  # Flexibilité pour extensions futures


# ───────────────────────────────────────────────────────────────
# LOGGING SQLITE
# ───────────────────────────────────────────────────────────────

def _ensure_db_and_table() -> None:
    """
    Crée la base SQLite et la table validation_errors si elles n'existent pas.
    Cette fonction est idempotente.
    """
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS validation_errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            from_agent TEXT,
            to_agent TEXT,
            message_type TEXT,
            error_message TEXT NOT NULL,
            raw_payload TEXT,
            project_id TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def _log_validation_error(
    from_agent: str,
    to_agent: str,
    message_type: str,
    error_message: str,
    raw_payload: str,
    project_id: Optional[str] = None,
) -> None:
    """
    Persiste une erreur de validation dans SQLite.
    """
    _ensure_db_and_table()
    conn = sqlite3.connect(str(_DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO validation_errors (
            timestamp, from_agent, to_agent, message_type,
            error_message, raw_payload, project_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(),
            from_agent,
            to_agent,
            message_type,
            error_message,
            raw_payload,
            project_id,
        ),
    )
    conn.commit()
    conn.close()


# ───────────────────────────────────────────────────────────────
# FONCTION PUBLIQUE
# ───────────────────────────────────────────────────────────────

def validate_agent_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valide un message inter-agents selon le schéma AgentMessage.

    Args:
        message: Dictionnaire représentant le message à transmettre.

    Returns:
        Dict contenant :
            - valid (bool) : True si le message est conforme.
            - message (str) : Description du résultat.
            - error_details (List[Dict]) : Erreurs Pydantic détaillées.
            - structured_error (Optional[Dict]) : Message d'erreur à
              renvoyer à l'agent émetteur si la validation échoue.
            - validated_data (Optional[Dict]) : Données nettoyées si valide.
    """
    # Sérialisation du payload brut pour le logging (avant validation)
    raw_payload = json.dumps(message, ensure_ascii=False, default=str)

    try:
        # Validation Pydantic stricte
        validated = AgentMessage(**message)
        return {
            "valid": True,
            "message": "Message inter-agents validé avec succès.",
            "error_details": [],
            "structured_error": None,
            "validated_data": validated.dict(),
        }

    except ValidationError as exc:
        errors = exc.errors()
        error_summary = (
            f"Validation échouée pour le message "
            f"'{message.get('message_type', 'inconnu')}' "
            f"de '{message.get('from_agent', 'inconnu')}' "
            f"vers '{message.get('to_agent', 'inconnu')}'."
        )

        # Log horodaté dans SQLite
        _log_validation_error(
            from_agent=message.get("from_agent", "inconnu"),
            to_agent=message.get("to_agent", "inconnu"),
            message_type=message.get("message_type", "inconnu"),
            error_message=str(errors),
            raw_payload=raw_payload,
            project_id=message.get("project_id"),
        )

        # Construction du message d'erreur structuré pour l'émetteur
        structured_error = {
            "status": "validation_failed",
            "target_agent": message.get("from_agent"),
            "error": (
                "Le message que vous avez envoyé ne respecte pas "
                "le schéma inter-agents requis de La TEC."
            ),
            "details": errors,
            "timestamp": datetime.now().isoformat(),
            "original_message_id": message.get("message_id"),
            "required_schema": "AgentMessage (tools\\json_validator.py)",
        }

        return {
            "valid": False,
            "message": error_summary,
            "error_details": errors,
            "structured_error": structured_error,
        }

    except Exception as exc:
        # Erreur inattendue (non-validation)
        error_msg = f"Erreur inattendue lors de la validation : {str(exc)}"
        _log_validation_error(
            from_agent=message.get("from_agent", "inconnu"),
            to_agent=message.get("to_agent", "inconnu"),
            message_type=message.get("message_type", "inconnu"),
            error_message=error_msg,
            raw_payload=raw_payload,
            project_id=message.get("project_id"),
        )

        structured_error = {
            "status": "validation_failed",
            "target_agent": message.get("from_agent"),
            "error": error_msg,
            "details": [],
            "timestamp": datetime.now().isoformat(),
            "original_message_id": message.get("message_id"),
        }

        return {
            "valid": False,
            "message": error_msg,
            "error_details": [{"error": str(exc)}],
            "structured_error": structured_error,
        }


def build_valid_message(
    from_agent: str,
    to_agent: str,
    message_type: str,
    payload: Dict[str, Any],
    project_id: Optional[str] = None,
    priority: Optional[str] = "normal",
) -> Dict[str, Any]:
    """
    Helper pour construire un message valide prêt à l'envoi.

    Args:
        from_agent: Identifiant de l'émetteur.
        to_agent: Identifiant du destinataire.
        message_type: Type de message.
        payload: Charge utile (doit contenir au moins 'content').
        project_id: Identifiant de projet (optionnel).
        priority: Priorité du message.

    Returns:
        Dict représentant le message formaté et validé.
    """
    message = {
        "message_id": str(uuid.uuid4()),
        "from_agent": from_agent,
        "to_agent": to_agent,
        "message_type": message_type,
        "payload": payload,
        "timestamp": datetime.now().isoformat(),
        "project_id": project_id,
        "priority": priority,
    }

    # On valide immédiatement pour garantir la conformité
    result = validate_agent_message(message)
    if not result["valid"]:
        raise ValueError(
            f"Message construit invalide : {result['message']}"
        )

    return message
