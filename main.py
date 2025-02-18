from picamzero import Camera
import cv2, piexif
from datetime import datetime, timedelta
import time, math

# Funktion til at hente tidspunktet fra EXIF-data
def get_time(img):
    return datetime.strptime(
        piexif.load(img)["Exif"].get(piexif.ExifIFD.DateTimeOriginal, b"").decode(),
        "%Y:%m:%d %H:%M:%S"
    )

# Funktion til at beregne position (centroid) ud fra den største kontur
def get_pos(img):
    contours = cv2.findContours(
        cv2.threshold(cv2.imread(img, 0), 200, 255, cv2.THRESH_BINARY)[1],
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )[0]
    M = cv2.moments(max(contours, key=cv2.contourArea, default=[]))
    return (M["m10"]/M["m00"], M["m01"]/M["m00"]) if M.get("m00") else None

# Funktion til at beregne tidsforskellen mellem to billeder (i sekunder)
def get_time_difference(img1, img2):
    t1 = get_time(img1)
    t2 = get_time(img2)
    return (t2 - t1).total_seconds()

# Funktion til at konvertere billedfiler til OpenCV-objekter
def convert_to_cv(img1, img2):
    return cv2.imread(img1), cv2.imread(img2)

# Funktion til at beregne keypoints og descriptors med ORB
def calculate_features(img1, img2):
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    return kp1, kp2, des1, des2

# Funktion til at matche descriptors ved brug af BFMatcher
def calculate_matches(des1, des2):
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    return bf.match(des1, des2)

# Funktion til at finde koordinater for de matchende keypoints
def find_matching_coordinates(kp1, kp2, matches):
    coords1 = [kp1[m.queryIdx].pt for m in matches]
    coords2 = [kp2[m.trainIdx].pt for m in matches]
    return coords1, coords2

# Funktion til at beregne den gennemsnitlige afstand mellem matchende koordinater
def calculate_mean_distance(coords1, coords2):
    if not coords1:
        return 0
    distances = [math.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2) for c1, c2 in zip(coords1, coords2)]
    return sum(distances) / len(distances)

# Funktion til at beregne hastigheden i km/s
def calculate_speed_in_kmps(mean_distance, GSD, time_difference):
    # Konverter pixels til kilometer: afstand = mean_distance * GSD
    distance_km = mean_distance * GSD
    return distance_km / time_difference if time_difference else 0

# Hovedprogrammet
if __name__ == "__main__":
    cam = Camera()
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=10)

    previous_image = None
    all_speeds = []

    print("Starting ISS speed measurement...")

    while datetime.now() < end_time:
        image_name = f"photo_{datetime.now().strftime('%H%M%S')}.jpg"
        cam.take_photo(image_name)
        time.sleep(30)  # Vent 30 sekunder mellem billeder

        if previous_image:
            time_difference = get_time_difference(previous_image, image_name)
            img1_cv, img2_cv = convert_to_cv(previous_image, image_name)
            kp1, kp2, des1, des2 = calculate_features(img1_cv, img2_cv)
            matches = calculate_matches(des1, des2)
            coords1, coords2 = find_matching_coordinates(kp1, kp2, matches)
            mean_distance = calculate_mean_distance(coords1, coords2)

            GSD = 12468  # Eksempelværdi for Ground Sampling Distance (km/pixel)
            speed = calculate_speed_in_kmps(mean_distance, GSD, time_difference)
            all_speeds.append(speed)

            print(f"Calculated speed: {speed:.4f} km/s")

        previous_image = image_name  # Opdater til næste iteration

    # Beregn gennemsnitshastigheden
    final_speed = sum(all_speeds) / len(all_speeds) if all_speeds else 0

    # Gem resultatet i result.txt
    with open("result.txt", "w") as file:
        file.write(f"Speed: {final_speed:.5g} km/s")
