#!/bin/bash

# URL de la page Boursorama de Tesla
URL="https://www.boursorama.com/cours/TSLA/"

# Etape 1: On récupère les données qui nous intéressent du site

# On commence par extraire le prix de l'action
price=$(curl -s "$URL" | grep -oP '<span class="c-instrument c-instrument--last"[^>]*>\K[0-9,]+' | head -n 1)

# On extrait ensuite le score ESG
esg_score=$(curl -s "$URL" | grep -oP '(\d{1,2},\d{1,2} /100)' | head -n 1)

# On extrait la variation de prix depuis la dernière clotûre
variation=$(curl -s "$URL" | grep -oP '<span class="c-instrument c-instrument--variation"[^>]*>\K[^<]+' | head -n 1)

# On extrait du site les valeurs des quantités et des prix du bid et du ask
values=$(curl -s "$URL" | grep -oP '<td class="c-table__cell c-table__cell--dotted"[^>]*>\K[\d\s,]+')

quantite_bid=$(echo "$values" | sed -n '1p') 
prix_bid=$(echo "$values" | sed -n '2p')    
quantite_ask=$(echo "$values" | sed -n '3p')  
prix_ask=$(echo "$values" | sed -n '4p') 

# On extrait le prix de clôture précédent
previous_close=$(curl -s "$URL" | grep -oP '<span class="c-instrument c-instrument--previousclose"[^>]*>\K[\d,]+')

# On extrait le prix le plus haut de la journée
high_price=$(curl -s "$URL" | grep -oP '<span class="c-instrument c-instrument--high"[^>]*>\K[\d,]+')

# On extrait le prix le plus bas de la journée
low_price=$(curl -s "$URL" | grep -oP '<span class="c-instrument c-instrument--low"[^>]*>\K[\d,]+')

# On détermine l'heure à laquelle notre machine a récupéré ces informations
current_time=$(date "+%Y-%m-%d %H:%M:%S")


# Etape 2: On sauvegarde dans un fichier .csv toutes les informations

# Si le fichier n'existe pas alors on le crée
if [ ! -f prix_TSLA.csv ]; then
    echo "Date;Prix;ESG Score;Variation;Quantite_Bid;Prix_Bid;Quantite_Ask;Prix_Ask;Cloture_Precedente;Plus_Haut;Plus_Bas" > prix_TSLA.csv  # Ajouter l'en-tête si le fichier n'existe pas encore
fi

# Ajouter les nouvelles données sans recréer le fichier
echo "$current_time;$price;$esg_score;$variation;$quantite_bid;$prix_bid;$quantite_ask;$prix_ask;$previous_close;$high_price;$low_price" >> prix_TSLA.csv
echo "$current_time;$price;$esg_score;$variation;$quantite_bid;$prix_bid;$quantite_ask;$prix_ask;$previous_close;$high_price;$low_price"
