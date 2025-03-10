#!/bin/bash

# URL de la page Boursorama de Tesla
URL="https://www.boursorama.com/cours/TSLA/"

# Extraire le prix de l'action à partir du HTML
price=$(curl -s "$URL" | grep -oP '<span class="c-instrument c-instrument--last"[^>]*>\K[0-9,]+' | head -n 1)

# Récupérer l'heure actuelle de la machine
current_time=$(date "+%Y-%m-%d %H:%M:%S")

# Sauvegarde dans un fichier CSV sans écraser les anciennes données
if [ ! -f prix_TSLA.csv ]; then
    echo "Date;Prix" > prix_TSLA.csv  # Ajouter l'en-tête si le fichier n'existe pas encore
fi

# Ajouter les nouvelles données sans recréer le fichier
echo "$current_time;$price" >> prix_TSLA.csv

# Afficher l'heure actuelle et le prix
echo "Heure actuelle : $current_time"
echo "Prix actuel de l'action Tesla : $price"

