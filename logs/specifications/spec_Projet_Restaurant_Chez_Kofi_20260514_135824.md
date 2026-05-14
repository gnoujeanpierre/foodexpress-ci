# Spec Projet_Restaurant_Chez_Kofi\n\n```json
{
  "titre": "Specification Fonctionnelle - Projet_Restaurant_Chez_Kofi",
  "version": "1.0",
  "date_redaction": "14/05/2026",
  "contexte": "Le secteur de la restauration en Côte d'Ivoire connaît une forte croissance, avec une demande accrue pour des solutions de commande en ligne et de livraison. Les consommateurs recherchent des moyens pratiques et rapides pour commander leurs repas, surtout dans des zones comme Abidjan Cocody. L'application mobile proposée vise à répondre à ce besoin tout en tenant compte des spécificités locales telles que les paiements mobiles et les défis liés à la connectivité.",
  "objectifs": [
    "Développer une application mobile permettant aux clients de passer des commandes en ligne et de choisir la livraison."
  ],
  "perimetre_inclus": [
    "Développement de l'application mobile pour Android et iOS.",
    "Création d'une API backend pour gérer les commandes et les paiements.",
    "Intégration des systèmes de paiement mobile (Wave, Orange Money, MTN MoMo)."
  ],
  "perimetre_exclu": [
    "Développement d'une version web de l'application.",
    "Gestion des stocks et des approvisionnements."
  ],
  "acteurs": [
    "M. Kofi Achi (Client)",
    "Développeurs",
    "Utilisateurs finaux (clients du restaurant)"
  ],
  "users_stories": [
    {
      "id": "US-001",
      "en_tant_que": "Client",
      "je_veux": "passer une commande en ligne",
      "afin_de": "recevoir mes plats préférés à domicile",
      "critere_acceptation": "L'utilisateur peut sélectionner des plats, les ajouter au panier et passer commande.",
      "priorite": "Haute"
    },
    {
      "id": "US-002",
      "en_tant_que": "Client",
      "je_veux": "choisir un mode de paiement",
      "afin_de": "payer ma commande facilement",
      "critere_acceptation": "L'utilisateur peut choisir entre Wave, Orange Money et MTN MoMo lors du paiement.",
      "priorite": "Haute"
    },
    {
      "id": "US-003",
      "en_tant_que": "Client",
      "je_veux": "suivre ma commande",
      "afin_de": "savoir quand elle sera livrée",
      "critere_acceptation": "L'utilisateur peut voir le statut de sa commande en temps réel.",
      "priorite": "Moyenne"
    },
    {
      "id": "US-004",
      "en_tant_que": "Client",
      "je_veux": "recevoir des notifications",
      "afin_de": "être informé des promotions et de l'état de ma commande",
      "critere_acceptation": "L'utilisateur reçoit des notifications push pour les mises à jour de commande et les promotions.",
      "priorite": "Moyenne"
    },
    {
      "id": "US-005",
      "en_tant_que": "Administrateur",
      "je_veux": "gérer les commandes",
      "afin_de": "assurer le bon fonctionnement du service",
      "critere_acceptation": "L'administrateur peut voir, modifier et annuler les commandes dans le système.",
      "priorite": "Basse"
    }
  ],
  "regles_metier": [
    {
      "id": "RM-001",
      "libelle": "Validation des commandes",
      "description": "Toute commande doit être validée avant d'être traitée pour éviter les erreurs.",
      "priorite": "Haute"
    },
    {
      "id": "RM-002",
      "libelle": "Limite de paiement",
      "description": "Le montant maximum d'une commande ne doit pas dépasser 100,000 FCFA.",
      "priorite": "Moyenne"
    },
    {
      "id": "RM-003",
      "libelle": "Gestion des promotions",
      "description": "Les promotions doivent être appliquées automatiquement lors du passage de la commande si elles sont valides.",
      "priorite": "Basse"
    }
  ],
  "contraintes_techniques": [
    "L'application doit être compatible avec les versions Android et iOS.",
    "L'application doit fonctionner avec une connexion internet intermittente."
  ],
  "livrables_attendus": [
    "Application mobile pour Android et iOS.",
    "API backend opérationnelle.",
    "Documentation technique et utilisateur."
  ],
  "langue": "francais",
  "devise": "FCFA"
}
```