# 📸 Script d'Organisation de Photos et Vidéos

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg) ![License](https://img.shields.io/badge/License-MIT-green.svg)

Ce script organise automatiquement vos **photos** et **vidéos** (`.jpg`, `.jpeg`, `.png`, `.mp4`) en les triant par **date** et **lieu** à partir des **métadonnées EXIF** ou des **fichiers JSON** générés par **Google Takeout**.

Il détecte et déplace aussi les **doublons**.

---

## ✨ Fonctionnalités

- 🔎 Lecture automatique des métadonnées EXIF et JSON.
- 🗂️ Classement des fichiers dans des dossiers `AAAA-MM-JJ_Lieu`.
- 🛰️ Utilisation des coordonnées GPS pour nommer les lieux.
- 🧹 Détection et déplacement automatique des doublons.
- 🌍 Géolocalisation via Nominatim OpenStreetMap.
- ⚙️ Compatible avec Python 3.8 à 3.12+.

---

## 📥 Télécharger vos Photos avec Google Takeout

1. Allez sur [Google Takeout](https://takeout.google.com/).
2. Cliquez sur "**Désélectionner tout**".
3. Sélectionnez uniquement "**Google Photos**".
4. Cliquez sur "**Tous les albums photo inclus**" pour affiner votre sélection si besoin.
5. Cliquez sur "**Suivant**".
6. Choisissez :
   - **Type d’exportation** : une seule fois
   - **Type de fichier** : `.zip`
   - **Taille du fichier** : 2 Go (ou plus selon votre espace disque)
7. Cliquez sur "**Créer une exportation**" et attendez.
8. Téléchargez et extrayez votre archive.

> **Important** : Les fichiers `.json` générés sont essentiels pour retrouver les métadonnées.

---

## ⚙️ Installation des dépendances

Installez les bibliothèques requises :

```bash
pip install pillow piexif geopy tqdm
