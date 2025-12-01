# 🤖 FootBot

> **Le compagnon Discord pour vos pronostics sportifs**

[![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Discord.py](https://img.shields.io/badge/Discord.py-Bot-5865F2?style=for-the-badge&logo=discord)](https://discordpy.readthedocs.io/)
[![API](https://img.shields.io/badge/API-Sports-green?style=for-the-badge)](https://www.api-football.com/)

**FootBot** est un bot Discord interactif qui anime votre serveur autour des matchs de football. Il permet aux membres de la communauté de consulter les calendriers, de faire des pronostics sur les rencontres à venir et de suivre leur classement en temps réel.

Le projet lie l'API de messagerie **Discord** avec des données sportives réelles via **API-Sports**.

## 🚀 Fonctionnalités

- 📅 **Calendrier Automatique** : Récupération et affichage des matchs de Ligue 1 directement dans Discord.
- 🔮 **Système de Pronostics** : Commandes simples pour parier sur le résultat d'un match.
- 🏆 **Classement Dynamique** : Gestion des scores des utilisateurs, stockés en base de données, et affichage du leaderboard du serveur.
- 🔄 **Mise à Jour Live** : Synchronisation avec les résultats réels pour valider les pronostics automatiquement.

## 🛠️ Technologies Utilisées

- **Langage** : Python 3
- **Framework Bot** : `discord.py` (Wrapper officiel pour l'API Discord)
- **Données Sportives** : Intégration de l'API externe [API-Sports](https://www.api-football.com/) via `requests`.
