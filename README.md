
# Organisateur de Photos et Vidéos (avec Géolocalisation)

## Description
Ce script organise vos photos et vidéos (formats `.jpg`, `.jpeg`, `.png`, `.mp4`) en fonction de la date de prise de vue et de la géolocalisation (latitude et longitude). Il ajoute également des métadonnées EXIF pour les photos et des métadonnées de géolocalisation dans les fichiers MP4.

## Fonctionnalités
- Trie les photos et vidéos dans des dossiers organisés par date et emplacement.
- Ajoute les informations de géolocalisation (latitude et longitude) dans les métadonnées EXIF des photos.
- Ajoute les métadonnées de géolocalisation dans les fichiers MP4 (avec `mutagen`).
- Détecte et déplace les doublons vers un dossier spécifique.

## Prérequis
Avant de pouvoir exécuter ce script, assurez-vous d'avoir installé toutes les dépendances nécessaires. Vous pouvez installer ces dépendances via `pip` :
```bash
pip install geopy piexif mutagen Pillow tqdm
```

## Procédure pour télécharger les photos et vidéos de Google Photos via Google Takeout
1. Allez sur [Google Takeout](https://takeout.google.com/) et sélectionnez les données que vous souhaitez télécharger (Photos et Vidéos).
2. Assurez-vous de sélectionner l'option pour télécharger les fichiers dans leur format original (cela inclura les fichiers EXIF et vidéo).
3. Téléchargez l'archive ZIP une fois qu'elle est prête.
4. Extrayez l'archive ZIP dans un dossier de votre choix.
5. Passez ce dossier en argument du script pour organiser vos fichiers.

## Utilisation
1. Téléchargez ou clonez ce script sur votre ordinateur.
2. Exécutez le script en utilisant la commande suivante :
```bash
python photo_organizer.py
```
3. Le script vous demandera :
   - Le chemin vers le dossier contenant vos photos et vidéos.
   - Si vous souhaitez déplacer les doublons détectés dans un dossier spécifique.
   - Votre adresse email pour le user-agent Nominatim (utilisé pour récupérer des informations de localisation).

Le script triera ensuite vos fichiers en fonction de la date et de l'emplacement, et ajoutera les métadonnées appropriées.

## Exemple de sortie
Les fichiers seront organisés dans des dossiers du type :
```
YYYY-MM-DD_Location
```
Où `YYYY-MM-DD` est la date de prise de vue et `Location` est le lieu associé.

Le script met à jour les informations EXIF pour les images et les métadonnées MP4 pour les vidéos avec la date et la géolocalisation.
