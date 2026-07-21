#!/usr/bin/env python3
# Verifie le niveau de batterie de la/les keybox igloohome (Locabus) et alerte Senjur par email si faible.
# Autonome (GitHub Actions), independant de tout ordinateur.
import os, json, base64, urllib.request, urllib.parse, urllib.error

CID   = os.environ["IGLOO_CID"]
SEC   = os.environ["IGLOO_SECRET"]
BREVO = os.environ["BREVO_API_KEY"]
ALERT_TO   = os.environ.get("ALERT_EMAIL", "locab.u.s96@gmail.com")   # boite que Senjur lit
SENDER     = os.environ.get("SENDER_EMAIL", "contact@locabus.ch")
THRESHOLD  = int(os.environ.get("BATTERY_THRESHOLD", "25"))

def igloo_token():
    data = urllib.parse.urlencode({"grant_type": "client_credentials",
                                   "scope": "igloohomeapi/get-devices"}).encode()
    req = urllib.request.Request("https://auth.igloohome.co/oauth2/token", data=data)
    req.add_header("Authorization", "Basic " + base64.b64encode(f"{CID}:{SEC}".encode()).decode())
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    return json.load(urllib.request.urlopen(req, timeout=30))["access_token"]

def get_devices(tok):
    r = urllib.request.Request("https://api.igloodeveloper.co/igloohome/devices")
    r.add_header("Authorization", "Bearer " + tok)
    return json.load(urllib.request.urlopen(r, timeout=30)).get("payload", [])

def send_mail(subject, html):
    body = json.dumps({
        "sender": {"name": "Locabus", "email": SENDER},
        "to": [{"email": ALERT_TO}],
        "subject": subject,
        "htmlContent": html,
    }).encode()
    req = urllib.request.Request("https://api.brevo.com/v3/smtp/email", data=body)
    req.add_header("api-key", BREVO); req.add_header("Content-Type", "application/json")
    return urllib.request.urlopen(req, timeout=30).status

tok = igloo_token()
devs = get_devices(tok)
low = [d for d in devs if isinstance(d.get("batteryLevel"), int) and d["batteryLevel"] <= THRESHOLD]
for d in devs:
    print(f"{d.get('deviceName')} ({d.get('deviceId')}) : batterie {d.get('batteryLevel')}%")

if low:
    lignes = "".join(
        f"<li><b>{d.get('deviceName','Keybox')}</b> : {d['batteryLevel']}% de batterie</li>"
        for d in low)
    html = (f"<p>Bonjour,</p><p>La batterie de votre boite a cles Locabus est faible "
            f"(seuil {THRESHOLD}%). Pensez a la recharger prochainement pour eviter "
            f"que les codes clients ne fonctionnent plus :</p><ul>{lignes}</ul>"
            f"<p>Pour recharger : ouvrez la boite avec votre cle physique et branchez le cable, "
            f"ou remplacez les piles selon le modele.</p><p>Locabus</p>")
    st = send_mail("[Locabus] Batterie keybox faible - a recharger", html)
    print("ALERTE envoyee (HTTP %s) pour %d device(s) sous %d%%" % (st, len(low), THRESHOLD))
else:
    print("Batterie OK, aucune alerte.")
