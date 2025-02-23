import time
import math
from astro_pi_orbit import ISS

# Jordens gennemsnitlige radius i kilometer
EARTH_RADIUS = 6371.0

# Initialiser ISS-objektet
iss = ISS()

# Definér måleperiode (10 minutter)
DURATION = 10 * 60  # sekunder
start_time = time.time()

# Liste til at gemme hastighedsmålinger
speeds = []
measurement_count = 0

# Funktion til at beregne afstand med Haversine-formlen
def haversine(lat1, lon1, lat2, lon2, radius):
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    return radius * c  # Afstand i km

# Løkke til målinger i 10 minutter
while time.time() - start_time < DURATION:
    # Hent den første GPS-position og højde
    lat1, lon1, alt1 = iss.latitude, iss.longitude, iss.altitude  # (grader, grader, km)
    t1 = time.time()

    # Vent et par sekunder (fx 5 sekunder)
    time.sleep(5)

    # Hent den anden GPS-position og højde
    lat2, lon2, alt2 = iss.latitude, iss.longitude, iss.altitude
    t2 = time.time()

    # Beregn tidsforskellen
    dt = t2 - t1  # sekunder
    if dt <= 0:
        continue  # Spring over hvis tidsforskellen er ugyldig

    # Beregn den gennemsnitlige ISS-højde (i km)
    alt_avg = (alt1 + alt2) / 2.0

    # Effektiv radius: Jordens radius + ISS-højde (km)
    effective_radius = EARTH_RADIUS + alt_avg

    # Beregn afstanden mellem de to punkter med Haversine-formlen
    distance = haversine(lat1, lon1, lat2, lon2, effective_radius)  # km

    # Beregn hastigheden i km/s
    speed = distance / dt
    speeds.append(speed)
    measurement_count += 1

    print(f"Måling {measurement_count}: Hastighed: {speed:.5f} km/s, Tidsinterval: {dt:.2f} s, Afstand: {distance:.5f} km")

# Beregn gennemsnitshastigheden over alle målinger
avg_speed = sum(speeds) / len(speeds) if speeds else 0

# Skriv resultatet til result.txt
with open("result.txt", "w") as f:
    f.write(f"Gennemsnitshastighed: {avg_speed:.5f} km/s\nAntal målinger: {measurement_count}\n")

print(f"Programmet afsluttet efter 10 minutter.\nGennemsnitshastighed: {avg_speed:.5f} km/s")
