# Spec Projet_Restaurant_Chez_Kofi\n\n```json
{
  "titre": "Specification Fonctionnelle - Projet_Restaurant_Chez_Kofi",
  "version": "1.0",
  "date_redaction": "14/05/2026",
  "contexte": "Le marché de la restauration en Côte d'Ivoire est en pleine expansion, avec une demande croissante pour des solutions de commande en ligne et de livraison. Les clients recherchent des moyens pratiques pour commander leurs repas, surtout dans des zones comme Cocody à Abidjan. L'application mobile doit répondre à ces besoins tout en tenant compte des spécificités locales telles que les paiements mobiles et les problèmes de réseau intermittent.",
  "objectifs": [
    "Faciliter la commande en ligne pour les clients.",
    "Optimiser le processus de livraison.",
    "Améliorer l'expérience client."
  ],
  "perimetre_inclus": [
    "Développement d'une application mobile pour Android et iOS.",
    "Création d'une API backend pour gérer les commandes et les paiements.",
    "Intégration des systèmes de paiement mobile (Wave, Orange Money, MTN MoMo)."
  ],
  "perimetre_exclu": [
    "Développement d'une version web de l'application.",
    "Gestion des stocks et des approvisionnements."
  ],
  "acteurs": [
    "M. Kofi Achi (Client)",
    "Développeurs (équipe technique)",
    "Clients (utilisateurs finaux)"
  ],
  "users_stories": [
    {
      "id": "US-001",
      "en_tant_que": "client",
      "je_veux": "commander un repas en ligne",
      "afin_de": "recevoir ma commande à domicile",
      "critere_acceptation": "L'utilisateur peut sélectionner des plats, ajouter au panier et passer commande.",
      "priorite": "Haute"
    },
    {
      "id": "US-002",
      "en_tant_que": "client",
      "je_veux": "payer ma commande via mobile",
      "afin_de": "faciliter le processus de paiement",
      "critere_acceptation": "L'utilisateur peut choisir entre Wave, Orange Money et MTN MoMo pour le paiement.",
      "priorite": "Haute"
    },
    {
      "id": "US-003",
      "en_tant_que": "client",
      "je_veux": "suivre ma commande en temps réel",
      "afin_de": "savoir quand ma commande arrive",
      "critere_acceptation": "L'utilisateur reçoit des notifications sur l'état de sa commande.",
      "priorite": "Moyenne"
    },
    {
      "id": "US-004",
      "en_tant_que": "client",
      "je_veux": "créer un compte utilisateur",
      "afin_de": "enregistrer mes informations et mes commandes précédentes",
      "critere_acceptation": "L'utilisateur peut s'inscrire et se connecter avec ses informations.",
      "priorite": "Moyenne"
    },
    {
      "id": "US-005",
      "en_tant_que": "administrateur",
      "je_veux": "gérer les commandes et les utilisateurs",
      "afin_de": "optimiser le service client",
      "critere_acceptation": "L'administrateur peut voir toutes les commandes et les informations des utilisateurs.",
      "priorite": "Basse"
    }
  ],
  "regles_metier": [
    {
      "id": "RM-001",
      "libelle": "Validation de la commande",
      "description": "Une commande ne peut être validée que si tous les articles sont disponibles.",
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
      "libelle": "Notifications de livraison",
      "description": "Les clients doivent recevoir une notification lorsque leur commande est en route.",
      "priorite": "Basse"
    }
  ],
  "contraintes_techniques": [
    "L'application doit être compatible avec les versions Android et iOS.",
    "L'application doit fonctionner même avec un réseau intermittent."
  ],
  "livrables_attendus": [
    "Application mobile fonctionnelle pour Android et iOS.",
    "API backend opérationnelle.",
    "Documentation technique et utilisateur."
  ],
  "langue": "francais",
  "devise": "FCFA"
}
```