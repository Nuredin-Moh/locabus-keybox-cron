# Locabus Keybox Refresh

Cron GitHub Actions qui régénère le code keybox (algoPIN hourly igloohome) **peu avant l'heure de prise** de chaque réservation Locabus, pour qu'il soit toujours valide le jour J (règle des 24h d'activation igloohome).

- Toutes les ~15 min, appelle `POST https://locabus.ch/wp-json/locabus/v1/keybox/refresh-imminent` avec un secret (`X-Locabus-Token`, stocké en GitHub Secret `LOCABUS_KEYBOX_TOKEN`).
- Le serveur (mu-plugin `locabus-keybox-refresh.php`) balaie les réservations dont la prise est imminente (−30 min … +3 h, Europe/Zurich), régénère le code et le renvoie au client. Idempotent.
