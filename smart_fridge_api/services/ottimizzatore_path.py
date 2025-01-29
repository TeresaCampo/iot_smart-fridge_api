import requests
import itertools
from geopy.geocoders import Nominatim

# Funzione per ottenere l'indirizzo a partire dalle coordinate
def get_address(coord):
    geolocator = Nominatim(user_agent="routing_app")  # User agent obbligatorio
    lat, lon = map(float, coord.split(','))
    try:
        location = geolocator.reverse((lat, lon), timeout=10) # Timeout per geocoding
        if location:
            return location.address
        else:
            return "Indirizzo non trovato"
    except Exception as e:
        print(f"Errore geocoding per {coord}: {e}")
        return "Errore geocoding"


# Funzione per calcolare la distanza tra due coordinate su strada usando OSRM
def get_distance_osrm(coord1, coord2):
    lat1, lon1 = map(float, coord1.split(','))
    lat2, lon2 = map(float, coord2.split(','))

    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"

    try:
        response = requests.get(url, timeout=10)  # Timeout di 10 secondi
        response.raise_for_status()  # Solleva un'eccezione per errori HTTP
        data = response.json()

        if 'routes' in data and data['routes']:
            return data['routes'][0]['legs'][0]['distance'] / 1000  # distanza in km
        else:
            print(f"Nessuna rotta trovata tra {coord1} e {coord2}")
            return float('inf')

    except requests.exceptions.Timeout:
        print(f"Timeout raggiunto durante la richiesta per {coord1} -> {coord2}")
        return float('inf')
    except requests.exceptions.RequestException as e:
        print(f"Errore durante la richiesta API per {coord1} -> {coord2}: {e}")
        return float('inf')


# Funzione per trovare il percorso più corto usando brute force
def find_shortest_path(start, end, waypoints):
    points = [start] + waypoints + [end]
    permutations = itertools.permutations(waypoints)

    min_distance = float('inf')
    best_route = None

    for perm in permutations:
        route = [start] + list(perm) + [end]
        total_distance = 0
        for i in range(len(route) - 1):
            distance = get_distance_osrm(route[i], route[i + 1])
            total_distance += distance
            if total_distance == float('inf'):
                break  # Se si verifica un errore, fermiamo il calcolo
        if total_distance < min_distance:
            min_distance = total_distance
            best_route = route

    return best_route, min_distance

# Funzione per rimuovere spazi da una stringa
def remove_spaces(input_string):
    return input_string.replace(" ", "")

# Funzione per creare l'URL di Google Maps
def create_google_maps_url(route):
    base_url = "https://www.google.com/maps/dir/"
    url = base_url + "/".join(remove_spaces(coord) for coord in route)
    return url

# Funzione per inviare un messaggio su Telegram
def invia_msg_telegram(token, chat_id, msg):
    telegram_api_url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"Ecco il percorso migliore: {msg}"
    }

    try:
        response = requests.post(telegram_api_url, json=payload, timeout=10)
        response.raise_for_status()
        print("Messaggio inviato con successo su Telegram.")
    except requests.exceptions.RequestException as e:
        print(f"Errore nell'invio del messaggio su Telegram: {e}")

#   Funzione per ottenere automaticamente il chat_id
#   Restituisce il primo chat_id trovato negli aggiornamenti"""

#   Funzione per stampare il risultato
def print_result(best_route, min_distance, token_bot, chat_id):
    if best_route:
        route_info= ""
        print("Il percorso migliore è:")
        for point in best_route:
            address = get_address(point)
            print(f"Coordinate: {point}, Indirizzo: {address}")
            route_info += f"Coordinate: {point}, Indirizzo: {address}\n"
        print(f"Distanza totale: {min_distance:.2f} km")
        route_info += f"Distanza totale: {min_distance} km\n"
        
        # Crea l'URL di Google Maps
        maps_url = create_google_maps_url(best_route)
        print(f"Puoi visualizzare il percorso su Google Maps: {maps_url}")

        # Invia il link su Telegram
        invia_msg_telegram(token_bot, chat_id , route_info) # invia dati tetsuali
        invia_msg_telegram(token_bot, chat_id , maps_url) # invia link maps
    else:
        print("Nessun percorso valido trovato.")

# Funzione principale per eseguire il programma
def start(waypoints):
    start = "44.641671341043946, 10.944602679703342"
    end = start
    token_bot = '7866846279:AAHyRghb2w2oP304RJrt3KSb4IGgVRODVxg' # Sostituisci con il token del tuo bot
    chat_id = "-4728044238" # id grupp id chat me stesso->"6655843792"
    # Calcola il percorso migliore
    best_route, min_distance = find_shortest_path(start, end, waypoints)
    # Stampa il risultato e invia il messaggio
    print_result(best_route, min_distance, token_bot , chat_id)


"""def main():
    # Esempi di input
    start = "44.641671341043946, 10.944602679703342"
    end = start
    waypoints = [
        "44.640816907742966, 10.943840935582177",
        "44.618755062079956, 10.925267955098636",
        "44.659959380847084, 10.920971281282684" # con 5 elemti circa 6:09 minuti con  4 1:07
    ]

    token_bot = '7866846279:AAHyRghb2w2oP304RJrt3KSb4IGgVRODVxg' # Sostituisci con il token del tuo bot
    chat_id = "-4728044238" # id grupp id chat me stesso->"6655843792"
    # Calcola il percorso migliore
    best_route, min_distance = find_shortest_path(start, end, waypoints)

    # Stampa il risultato e invia il messaggio
    #print_result(best_route, min_distance, token_bot, chat_id)
    print_result(best_route, min_distance, token_bot , chat_id)
# Avvia il programma

if __name__ == "__main__":
    main()"""