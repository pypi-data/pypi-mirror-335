import argparse
import os
import re

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import APIKeyHeader
import platform
import subprocess
import json
import logging
import socket
import uuid

from watchman_http_server.config import settings

app = FastAPI()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

WATCHMAN_API_KEY = settings.WATCHMAN_API_KEY  # La clé API que vous avez générée

# Créer un middleware pour la clé API
api_key_header = APIKeyHeader(name="WATCHMAN-API-KEY")


# Fonction pour valider la clé API
def api_key_required(api_key: str = Depends(api_key_header)):
    if api_key != WATCHMAN_API_KEY:
        raise HTTPException(
            status_code=403, detail="Forbidden: Invalid API Key"
        )


def get_system_info():
    """Récupère les infos système : OS, IP, MAC, etc."""
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    # Récupération propre de l'adresse MAC
    mac_address = ':'.join(['{:02X}'.format((uuid.getnode() >> i) & 0xFF) for i in range(0, 2 * 6, 8)][::-1])

    architecture = platform.machine()
    os_info = f"{platform.system()} {platform.release()}"

    return {
        "hostname": hostname,
        "ip": ip_address,
        "mac": mac_address,
        "architecture": architecture,
        "os": os_info
    }


def get_installed_apps():
    """Récupère la liste des applications installées selon l'OS."""
    system = platform.system()
    apps = []

    if system == "Windows":
        try:
            output = subprocess.check_output(
                ["wmic", "product", "get", "name,vendor,version"],
                universal_newlines=True,
                errors='ignore'
            )
            lines = output.strip().split("\n")

            # Suppression de la première ligne (en-tête)
            if len(lines) > 1:
                lines = lines[1:]
            for line in lines:
                parts = line.strip().split("  ")
                parts = [p.strip() for p in parts if p.strip()]
                if len(parts) == 3:
                    apps.append({"name": parts[0], "vendor": parts[1], "version": parts[2], "type": "application"})

        except Exception as e:
            logging.error(f"Error retrieving applications on Windows: {e}")
            return {"error": str(e)}

    elif system == "Linux":
        try:
            output = subprocess.check_output(
                ["dpkg-query", "-W", "-f=${Package} ${Version} ${Maintainer}\n"],
                universal_newlines=True,
                errors='ignore'
            )
            for line in output.strip().split("\n"):
                parts = line.split(" ")
                if len(parts) >= 3:
                    name = parts[0]
                    version = parts[1]
                    vendor = " ".join(parts[2:])
                    apps.append({"name": name, "vendor": vendor, "version": version, "type": "application"})
        except Exception as e:
            logging.error(f"Error retrieving applications on Linux: {e}")
            return {"error": str(e)}

    elif system == "Darwin":  # macOS
        try:
            output = subprocess.check_output(["system_profiler", "SPApplicationsDataType", "-json"],
                                             universal_newlines=True, errors='ignore')
            data = json.loads(output)
            if "SPApplicationsDataType" in data:
                for app in data["SPApplicationsDataType"]:
                    name = app.get("_name", "Unknown")
                    version = app.get("version", "Unknown")
                    vendor = app.get("obtained_from", "Unknown")
                    apps.append({"name": name, "vendor": vendor, "version": version, "type": "application"})
        except Exception as e:
            logging.error(f"Error retrieving applications on macOS: {e}")
            return {"error": str(e)}

    return apps


@app.get("/apps")
def list_apps(api_key: str = Depends(api_key_required)):
    """Endpoint pour récupérer les applications installées avec infos système."""
    system_info = get_system_info()
    applications = get_installed_apps()

    # Ajouter l'OS en tant qu'application
    system_info_app = {
        "name": system_info["os"],
        "version": platform.release(),
        "vendor": system_info["os"],
        "type": "os"
    }

    response = {
        "system_info": system_info,
        "applications": [system_info_app] + applications
    }

    return response


# def main():
#     import uvicorn
#     logging.info("Starting Watchman HTTP Server on port 8001...")
#     uvicorn.run("watchman_http_server.main:app", host="127.0.0.1", port=8001, log_level="info")

def main():
    import uvicorn
    # Créer un parseur d'arguments
    parser = argparse.ArgumentParser(description="Démarrer le serveur Watchman HTTP.")

    # Ajouter un argument pour le port
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port sur lequel démarrer le serveur (par défaut : 8001)"
    )

    # Ajouter un argument pour la clé API
    parser.add_argument(
        "--api-key",
        type=str,
        required=True,
        help="Clé API pour accéder au serveur."
    )

    # Analyser les arguments
    args = parser.parse_args()

    # Vérifier si la clé API est correcte
    if args.api_key != settings.WATCHMAN_API_KEY:
        logging.error("Clé API incorrecte!")
        return

    # Si tout est bon, démarrer le serveur
    logging.info(f"Starting Watchman HTTP Server on port {args.port}...")
    uvicorn.run("watchman_http_server.main:app", host="0.0.0.0", port=args.port, log_level="info", )


if __name__ == "__main__":
    main()
