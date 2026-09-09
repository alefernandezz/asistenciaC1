"""
Moodle Attendance Watcher
--------------------------
Este script NO marca la asistencia por vos. Solo:
  1. Inicia sesión en Moodle con tu usuario y contraseña.
  2. Revisa si la actividad "Asistencia TT" aparece visible en la página del curso
     (lo cual indica que la profesora la habilitó).
  3. Si aparece y no te habíamos avisado ya, te manda un mail para que entres
     vos mismo y la marques manualmente.

Nunca hace clic en "Submit attendance" ni envía ningún dato de asistencia.
"""

import os
import re
import sys
import smtplib
from email.mime.text import MIMEText

import requests
from bs4 import BeautifulSoup

# ----------------------------------------------------------------------
# Configuración (viene de variables de entorno / GitHub Secrets)
# ----------------------------------------------------------------------
MOODLE_BASE_URL = "https://virtual.um.edu.ar"
LOGIN_URL = f"{MOODLE_BASE_URL}/login/index.php"
COURSE_URL = f"{MOODLE_BASE_URL}/course/view.php?id=189&section=2"

MOODLE_USER = os.environ["MOODLE_USER"]
MOODLE_PASS = os.environ["MOODLE_PASS"]

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", GMAIL_USER)

# Texto que buscamos en la página del curso. Ajustalo si la profesora
# le puso otro nombre a la actividad.
TARGET_PATTERN = re.compile(r"asistencia\s*tt", re.IGNORECASE)

STATE_FILE = os.path.join(os.path.dirname(__file__), "state", "tt_enabled.flag")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AttendanceWatcher/1.0)"
}


def send_email(subject: str, body: str) -> None:
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = NOTIFY_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, [NOTIFY_EMAIL], msg.as_string())


def login(session: requests.Session) -> None:
    resp = session.get(LOGIN_URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    token_input = soup.find("input", {"name": "logintoken"})
    logintoken = token_input["value"] if token_input else ""

    payload = {
        "username": MOODLE_USER,
        "password": MOODLE_PASS,
        "logintoken": logintoken,
    }

    login_resp = session.post(LOGIN_URL, data=payload, headers=HEADERS, timeout=20)
    login_resp.raise_for_status()

    # Si el login falla, Moodle te devuelve a la misma página de login
    # con un div de error, o la URL contiene "testsession"/"login/index.php"
    if "loginerrormessage" in login_resp.text or "Invalid login" in login_resp.text:
        raise RuntimeError("Login falló: usuario o contraseña incorrectos, o Moodle cambió su formulario.")


def is_tt_enabled(session: requests.Session) -> bool:
    resp = session.get(COURSE_URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return bool(TARGET_PATTERN.search(resp.text))


def read_state() -> bool:
    return os.path.exists(STATE_FILE)


def write_state(enabled: bool) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    if enabled:
        with open(STATE_FILE, "w") as f:
            f.write("enabled\n")
    else:
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)


def main() -> int:
    session = requests.Session()

    try:
        login(session)
        enabled_now = is_tt_enabled(session)
    except Exception as exc:  # noqa: BLE001
        # Avisamos por mail si algo se rompió (ej. cambiaron el HTML de Moodle)
        send_email(
            subject="⚠️ Error revisando asistencia en Moodle",
            body=f"El script tuvo un error y no pudo revisar la asistencia:\n\n{exc}",
        )
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    was_enabled = read_state()

  
    if enabled_now and not was_enabled:
        send_email(
            subject="✅ Asistencia TT habilitada",
            body=(
                "La profesora habilitó la Asistencia TT en Moodle.\n\n"
                f"Entrá y marcala vos: {COURSE_URL}\n"
            ),
        )
        print("Asistencia habilitada. Mail enviado.")
    elif enabled_now and was_enabled:
        print("Ya estaba habilitada y ya se había avisado. No se manda mail de nuevo.")
    else:
        print("Asistencia TT no está habilitada todavía.")

    write_state(enabled_now)
    return 0


if __name__ == "__main__":
    sys.exit(main())
