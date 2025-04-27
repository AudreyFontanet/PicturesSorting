import os
import json
import shutil
import hashlib
import piexif
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim
from datetime import datetime
from tqdm import tqdm
from mutagen.mp4 import MP4
from mutagen.id3 import ID3, TIT2

geolocator = None

def get_exif_data(filepath):
    img = Image.open(filepath)
    exif_data = {}
    info = img._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]
                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value
    return exif_data

def convert_to_degrees(value):
    d, m, s = value
    return d[0] / d[1] + (m[0] / m[1]) / 60 + (s[0] / s[1]) / 3600

def get_coordinates(gps_info):
    try:
        lat = convert_to_degrees(gps_info['GPSLatitude'])
        if gps_info.get('GPSLatitudeRef') != 'N':
            lat = -lat
        lon = convert_to_degrees(gps_info['GPSLongitude'])
        if gps_info.get('GPSLongitudeRef') != 'E':
            lon = -lon
        return lat, lon
    except (KeyError, TypeError):
        return None, None

def get_date(filepath, json_data):
    date_taken = None
    if filepath.lower().endswith((".jpg", ".jpeg", ".png")):
        exif = get_exif_data(filepath)
        date_taken = exif.get("DateTimeOriginal") or exif.get("DateTime")
        if date_taken:
            try:
                date_taken = datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")
            except Exception:
                date_taken = None
    elif filepath.lower().endswith(".mp4"):
        try:
            video = MP4(filepath)
            date_taken = video.get("\xa9day", None)
            if date_taken:
                try:
                    date_taken = datetime.strptime(date_taken, "%Y-%m-%d")
                except Exception:
                    date_taken = None
        except Exception:
            pass
    if date_taken is None and json_data and "photoTakenTime" in json_data:
        try:
            timestamp = int(json_data["photoTakenTime"]["timestamp"])
            date_taken = datetime.fromtimestamp(timestamp, datetime.UTC)
        except Exception:
            pass
    if date_taken is None:
        return "Unknown_Date"
    return date_taken.strftime("%Y-%m-%d")


def get_lat_lon(filepath, json_data):
    lat, lon = None, None
    if filepath.lower().endswith((".jpg", ".jpeg", ".png")):
        exif = get_exif_data(filepath)
        gps_info = exif.get("GPSInfo", {})
        if gps_info:
            lat, lon = get_coordinates(gps_info)

    elif filepath.lower().endswith(".mp4"):
        try:
            video = MP4(filepath)
            location_str = video.get("\xa9cmt", None)
            if location_str:
                coords = location_str.split(",")
                if len(coords) == 2:
                    lat, lon = map(float, [coords[0].split(":")[1].strip(), coords[1].split(":")[1].strip()])
        except Exception:
            pass

    if lat is None or lon is None:
        if json_data and "geoDataExif" in json_data:
            geo = json_data["geoDataExif"]
            lat = geo.get("latitude")
            lon = geo.get("longitude")
            try:
                lat = float(lat) if lat is not None else None
                lon = float(lon) if lon is not None else None
            except (ValueError, TypeError):
                lat, lon = None, None

    return lat, lon

def get_location(lat, lon):
    if lat is None or lon is None:
        return "Unknown_Location"
    try:
        location = geolocator.reverse((lat, lon), timeout=10, language="fr")
        if location and 'address' in location.raw:
            address = location.raw['address']
            city = (address.get('city') or
                    address.get('town') or
                    address.get('village') or
                    address.get('state'))
            if city:
                return city.replace(' ', '_')
    except Exception:
        pass
    return "Unknown_Location"

def read_json(filepath):
    folder_path = os.path.dirname(filepath)
    file_name = os.path.basename(filepath)
    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)):
            if file_name in file and file.lower().endswith(".json"):
                json_path = os.path.join(folder_path, file)
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
    return None

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def deg_to_dms_rational(deg_float):
    deg = int(deg_float)
    min_float = (deg_float - deg) * 60
    min = int(min_float)
    sec = round((min_float - min) * 60 * 100)
    return ((deg, 1), (min, 1), (sec, 100))

def clean_exif_dict(exif_dict):
    for ifd in ("0th", "Exif", "GPS", "1st"):
        if ifd in exif_dict:
            tags = exif_dict[ifd]
            keys_to_delete = []
            for tag, value in tags.items():
                if isinstance(value, int):
                    keys_to_delete.append(tag)
            for tag in keys_to_delete:
                del tags[tag]
    return exif_dict

def write_metadata_from_json(filepath, json_data):
    if filepath.lower().endswith((".jpg", ".jpeg", ".png")):
        exif_dict = piexif.load(filepath)
        if json_data and "photoTakenTime" in json_data:
            try:
                timestamp = int(json_data["photoTakenTime"]["timestamp"])
                dt = datetime.fromtimestamp(timestamp, datetime.UTC)
                dt_str = dt.strftime("%Y:%m:%d %H:%M:%S")
                if piexif.ExifIFD.DateTimeOriginal not in exif_dict['Exif']:
                    exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = dt_str.encode('utf-8')
                if piexif.ImageIFD.DateTime not in exif_dict['0th']:
                    exif_dict['0th'][piexif.ImageIFD.DateTime] = dt_str.encode('utf-8')

            except Exception:
                pass
        if json_data and "geoDataExif" in json_data:
            geo = json_data["geoDataExif"]
            lat = geo.get("latitude")
            lon = geo.get("longitude")
            if lat and lon:
                if 'GPS' not in exif_dict or piexif.GPSIFD.GPSLatitude not in exif_dict['GPS']:
                    gps_ifd = {
                        piexif.GPSIFD.GPSLatitudeRef: 'N'.encode('utf-8') if lat >= 0 else 'S'.encode('utf-8'),
                        piexif.GPSIFD.GPSLatitude: deg_to_dms_rational(abs(lat)),
                        piexif.GPSIFD.GPSLongitudeRef: 'E'.encode('utf-8') if lon >= 0 else 'W'.encode('utf-8'),
                        piexif.GPSIFD.GPSLongitude: deg_to_dms_rational(abs(lon)),
                    }
                    exif_dict['GPS'] = gps_ifd
        exif_dict = clean_exif_dict(exif_dict)
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, filepath)

    elif filepath.lower().endswith(".mp4"):
        try:
            video = MP4(filepath)
            if json_data and "geoDataExif" in json_data:
                geo = json_data["geoDataExif"]
                lat = geo.get("latitude")
                lon = geo.get("longitude")
                if lat and lon:
                    if "\xa9cmt" not in video:
                        location_str = f"Latitude: {lat}, Longitude: {lon}"
                        video["\xa9cmt"] = location_str
                        video.save()
            else:
                pass

            if json_data and "photoTakenTime" in json_data:
                try:
                    timestamp = int(json_data["photoTakenTime"]["timestamp"])
                    dt = datetime.fromtimestamp(timestamp, datetime.UTC)
                    date_formatted = dt.strftime("%Y-%m-%d")
                    if "\xa9day" not in video:
                        video["\xa9day"] = date_formatted
                        video.save()
                except Exception:
                    pass

        except Exception as e:
            pass
        
def organize_photos(source_folder, move_duplicates=True, doublons_folder=None):
    if move_duplicates:
        doublons_folder = doublons_folder or os.path.join(source_folder, "Doublons")
        os.makedirs(doublons_folder, exist_ok=True)

    size_dict = {}
    for root, _, files in os.walk(source_folder):
        for filename in files:
            if filename.lower().endswith((".jpg", ".jpeg", ".png", ".mp4")):
                filepath = os.path.join(root, filename)
                size = os.path.getsize(filepath)
                size_dict.setdefault(size, []).append(filepath)

    for size, filepaths in tqdm(size_dict.items(), desc="Organisation des photos"):
        if len(filepaths) == 1:
            filepath = filepaths[0]
            process_file(filepath, source_folder)
        else:
            hash_dict = {}
            for filepath in filepaths:
                file_hash = calculate_md5(filepath)
                if file_hash in hash_dict:
                    if move_duplicates:
                        move_to_doublons(filepath, doublons_folder)
                else:
                    hash_dict[file_hash] = filepath
                    process_file(filepath, source_folder)

def process_file(filepath, source_folder):
    filename = os.path.basename(filepath)
    json_data = read_json(filepath)

    date_formatted = get_date(filepath, json_data)
    lat, lon = get_lat_lon(filepath, json_data)
    location = get_location(lat, lon)

    if json_data:
        write_metadata_from_json(filepath, json_data)
    
    folder_name = f"{date_formatted}_{location}"
    folder_path = os.path.join(source_folder, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    destination = os.path.join(folder_path, filename)
    if os.path.abspath(filepath) != os.path.abspath(destination):
        shutil.move(filepath, destination)

def move_to_doublons(filepath, doublons_folder):
    filename = os.path.basename(filepath)
    doublon_path = os.path.join(doublons_folder, filename)
    count = 1
    while os.path.exists(doublon_path):
        name, ext = os.path.splitext(filename)
        doublon_path = os.path.join(doublons_folder, f"{name}_dup{count}{ext}")
        count += 1
    shutil.move(filepath, doublon_path)

if __name__ == "__main__":
    source_folder = input("📁 Chemin vers le dossier contenant les fichiers : ").strip('"')
    if not os.path.isdir(source_folder):
        print("❌ Dossier introuvable. Vérifie le chemin.")
        exit(1)

    move_dup_input = input("❓ Voulez-vous déplacer les doublons ? (oui/non) : ").strip().lower()
    move_duplicates = move_dup_input in ["oui", "o", "yes", "y"]

    doublons_folder = None
    if move_duplicates:
        custom_path = input("📁 Chemin du dossier pour les doublons (laisser vide pour défaut) : ").strip('"')
        if custom_path:
            doublons_folder = os.path.abspath(custom_path)

    user_agent_email = input("✉️ Entrez votre adresse email pour le user-agent Nominatim : ").strip()
    geolocator = Nominatim(user_agent=user_agent_email)

    organize_photos(source_folder, move_duplicates, doublons_folder)
    print("✅ Organisation terminée !")
