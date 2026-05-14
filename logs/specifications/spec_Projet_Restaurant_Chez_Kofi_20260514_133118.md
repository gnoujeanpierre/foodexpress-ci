# Spec Projet_Restaurant_Chez_Kofi\n\n```json
{
  "titre": "Specification Fonctionnelle - Projet_Restaurant_Chez_Kofi",
  "version": "1.0",
  "date_redaction": "14/05/2026",
  "contexte": "Le marché de la restauration en Côte d'Ivoire est en pleine expansion, avec une demande croissante pour les services de commande en ligne et de livraison. Les clients recherchent des solutions pratiques et rapides pour accéder à leurs plats préférés, surtout dans des zones comme Cocody à Abidjan. Les paiements mobiles sont devenus la norme, et les applications doivent être conçues pour fonctionner même avec un réseau intermittent.",
  "objectifs": [
    "Développer une application mobile intuitive pour faciliter les commandes en ligne et la livraison."
  ],
  "perimetre_inclus": [
    "Développement d'une application mobile pour Android et iOS.",
    "Création d'une API backend pour gérer les commandes et les paiements.",
    "Intégration des solutions de paiement mobile (Wave, Orange Money, MTN MoMo)."
  ],
  "perimetre_exclu": [
    "Développement d'une version web de l'application.",
    "Services de marketing ou de promotion de l'application."
  ],
  "acteurs": [
    "M. Kofi Achi (Client)",
    "Développeurs (équipe technique)",
    "Utilisateurs finaux (clients du restaurant)"
  ],
  "users_stories": [
    {
      "id": "US-001",
      "en_tant_que": "Client",
      "je_veux": "passer une commande en ligne",
      "afin_de": "recevoir mes plats préférés à domicile",
      "critere_acceptation": "L'utilisateur peut sélectionner des plats, ajouter au panier et passer commande avec succès.",
      "priorite": "Haute"
    },
    {
      "id": "US-002",
      "en_tant_que": "Client",
      "je_veux": "payer ma commande en ligne",
      "afin_de": "faciliter le processus de commande sans espèces",
      "critere_acceptation": "L'utilisateur peut choisir parmi plusieurs options de paiement mobile et recevoir une confirmation de paiement.",
      "priorite": "Haute"
    },
    {
      "id": "US-003",
      "en_tant_que": "Client",
      "je_veux": "suivre l'état de ma commande",
      "afin_de": "savoir quand je vais recevoir ma commande",
      "critere_acceptation": "L'utilisateur peut voir l'état de sa commande en temps réel dans l'application.",
      "priorite": "Moyenne"
    },
    {
      "id": "US-004",
      "en_tant_que": "Client",
      "je_veux": "recevoir des notifications sur les promotions",
      "afin_de": "profiter des offres spéciales",
      "critere_acceptation": "L'utilisateur reçoit des notifications push pour les promotions et les nouveaux plats.",
      "priorite": "Basse"
    },
    {
      "id": "US-005",
      "en_tant_que": "Administrateur",
      "je_veux": "gérer les commandes et les menus",
      "afin_de": "maintenir l'application à jour avec les offres disponibles",
      "critere_acceptation": "L'administrateur peut ajouter, modifier ou supprimer des plats et gérer les commandes en cours.",
      "priorite": "Haute"
    }
  ],
  "regles_metier": [
    {
      "id": "RM-001",
      "libelle": "Gestion des paiements",
      "description": "Tous les paiements doivent être traités via des solutions de paiement mobile reconnues en Côte d'Ivoire.",
      "priorite": "Haute"
    },
    {
      "id": "RM-002",
      "libelle": "Notifications",
      "description": "Les utilisateurs doivent recevoir une notification pour chaque étape de leur commande (confirmation, préparation, livraison).",
      "priorite": "Moyenne"
    },
    {
      "id": "RM-003",
      "libelle": "Disponibilité des plats",
      "description": "Les plats affichés dans l'application doivent être disponibles en temps réel pour éviter les commandes de plats épuisés.",
      "priorite": "Haute"
    }
  ],
  "contraintes_techniques": [
    "L'application doit être optimisée pour fonctionner avec un réseau intermittent.",
    "L'application doit être compatible avec les versions Android et iOS les plus courantes."
  ],
  "livrables_attendus": [
    "Application mobile fonctionnelle pour Android et iOS.",
    "API backend opérationnelle.",
    "Documentation utilisateur et technique."
  ],
  "langue": "francais",
  "devise": "FCFA"
}
```