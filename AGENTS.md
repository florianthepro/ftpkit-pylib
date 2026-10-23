# AGENTS.md

## 1. Zweck dieser Datei

Diese Datei ist die verbindliche gemeinsame Arbeitsanweisung für alle Agents und alle Repositorys des Systems.

Jeder Agent erhält:

1. diese vollständige `AGENTS.md`
2. genau ein Repository, für das der Agent zuständig ist

Der Name des übergebenen Repositorys bestimmt automatisch die Rolle des Agents.

Es existieren genau diese vier Repositorys:

```text
ftpkit-pylib
ftpkit-shlib
backend
csv-reporting
```

Es existiert kein zusätzliches Repository namens server-manager.

Das Repository backend enthält den zentralen Server Manager und Setup Manager.

Der Agent muss vor jeder Änderung:

den Namen des eigenen Repositorys feststellen
die dazugehörige Rolle aus dieser Datei bestimmen
die gesamte gemeinsame Architektur berücksichtigen
Änderungen nur im fachlich richtigen Repository durchführen
keine Funktionen duplizieren, die in ein anderes Repository gehören
2. Repository- und Agent-Zuordnung
2.1 Repository ftpkit-pylib

Wenn das übergebene Repository ftpkit-pylib heißt, ist der Agent:

ftpkit-pylib-agent


Der Agent ist zuständig für:

generische, wiederverwendbare Python-Funktionen


Der Agent ist nicht zuständig für:

Shell-Installation
Server-Manager-GUI
CSV-Verarbeitung
anwendungsspezifische Backends
Caddy-Sites einzelner Anwendungen
Django-Routen einzelner Anwendungen

2.2 Repository ftpkit-shlib

Wenn das übergebene Repository ftpkit-shlib heißt, ist der Agent:

ftpkit-shlib-agent


Der Agent ist zuständig für:

generische, wiederverwendbare POSIX-Shell-Funktionen


Der Agent ist nicht zuständig für:

Python-Geschäftslogik
Server-Manager-GUI
CSV-Verarbeitung
anwendungsspezifische Regeln
anwendungsspezifische Frontends

2.3 Repository backend

Wenn das übergebene Repository backend heißt, ist der Agent:

backend-agent


Der Agent ist zuständig für:

den zentralen Server Manager
den zentralen Setup Manager
die zentrale Management-Webapp
die Verwaltung aller kompatiblen Webapps


Der Repositoryname bleibt immer:

backend


Die Anwendung im Repository darf in Texten als Server Manager oder Setup Manager bezeichnet werden. Es darf aber kein separates Repository namens server-manager eingeführt oder vorausgesetzt werden.

2.4 Repository csv-reporting

Wenn das übergebene Repository csv-reporting heißt, ist der Agent:

csv-reporting-agent


Der Agent ist zuständig für:

die konkrete CSV-Reporting-Webapp
CSV-Verarbeitung
CSV-Anzeige
CSV-Regeln
CSV-Editor
Import und Export
Integration in den zentralen Backend-Manager


Der Agent ist nicht zuständig für:

die globale Registry
die Verwaltung anderer Apps
allgemeine Systemverwaltung
duplizierte Python- oder Shell-Hilfsfunktionen

3. Verbindliches Hauptprinzip

Es gilt für alle vier Repositorys:

Write one function only once.

Eine Funktion, ein Parser, ein Validator, ein Datenmodell oder ein Systemablauf darf nicht mehrfach implementiert werden.

Vor jeder neuen Funktion muss der Agent prüfen:

Existiert die Funktion bereits im eigenen Repository?
Existiert die Funktion in einem der anderen drei Repositorys?
Ist die Funktion allgemein in Python wiederverwendbar?
Ist die Funktion allgemein in Shell-Skripten wiederverwendbar?
Gehört die Funktion zur zentralen Verwaltung mehrerer Apps?
Ist die Funktion wirklich ausschließlich anwendungsspezifisch?

Die Zuordnung lautet:

Generische Python-Funktion
→ ftpkit-pylib

Generische Shell-Funktion
→ ftpkit-shlib

Verwaltung mehrerer Apps oder des Gesamtsystems
→ backend

CSV-spezifische Fachlogik oder Oberfläche
→ csv-reporting


Fehlt eine benötigte generische Funktion, darf der Agent die Funktion nicht lokal kopieren.

Stattdessen muss der Agent:

die Funktion im zuständigen ftpkit-Repository ergänzen
dort Tests ergänzen
die Bibliotheksversion aktualisieren
das Changelog aktualisieren
die neue Version im abhängigen Repository verwenden
die lokale Duplikation entfernen
4. Gesamtvision

Das System soll mehrere Python-Webapps auf einem Linux-Server sauber, sicher und voneinander getrennt betreiben.

Es muss möglich sein:

verschiedene Apps zu installieren
dieselbe App beliebig oft zu installieren
jede Instanz getrennt zu verwalten
jede Instanz getrennt zu aktualisieren
jede Instanz getrennt zu sichern
jede Instanz getrennt wiederherzustellen
jede Instanz getrennt zu entfernen
Ports, Pfade, Zertifikate und Dienste sauber zu verwalten
zukünftige kompatible Webapps ohne Umbau der Gesamtarchitektur hinzuzufügen

Der zentrale Manager ist die Webapp aus dem Repository backend.

CSV Reporting ist eine verwaltete App und nicht selbst der zentrale Manager.

ftpkit-pylib und ftpkit-shlib bilden die wiederverwendbare technische Grundlage.

5. Verzeichnisstandard

Der alte Basispfad:

/srv/webapps/


wird nicht mehr als neuer Standard verwendet.

Der neue Basispfad lautet:

/sites/


Die Grundstruktur lautet:

/sites/
├── backend/
├── <appname>-<uuid>/
├── <appname>-<uuid>/
└── ...

6. Zentraler Backend-Manager

Der zentrale Manager wird unter folgendem Pfad installiert:

/sites/backend/


Die Struktur lautet:

/sites/backend/
├── data/
├── frontend/
├── backend/
└── srv/

6.1 /sites/backend/data/

Enthält persistente Managerdaten:

globale Registry
registrierte Apps
registrierte Instanzen
Managerkonfiguration
Transaktionsstatus
Sicherungskatalog
nicht geheime Zertifikatsinformationen
App-Manifeste
Instanzmetadaten
Verwaltungszustände
6.2 /sites/backend/frontend/

Enthält:

Setup-GUI
Manager-GUI
Anwendungsübersicht
Instanzübersicht
Portübersicht
Zertifikatsübersicht
Sicherungsübersicht
Änderungspläne
Bestätigungsdialoge
Logs und Statusanzeigen
6.3 /sites/backend/backend/

Enthält:

Python-Backend des Managers
Django-Projekt oder vergleichbare Python-Webstruktur
Management-API
Registry-API
App-Manifest-Verarbeitung
Capability-Prüfung
Installationsplanung
Upgradeplanung
Sicherungssteuerung
Wiederherstellungssteuerung
Rollbacksteuerung
Caddy-Steuerung
systemd-Steuerung
Portverwaltung
Zertifikatsverwaltung
Health Checks
Schnittstellen zu App-Backends

Generische Funktionen werden aus ftpkit-pylib importiert.

6.4 /sites/backend/srv/

Enthält:

virtuelle Python-Umgebung
Unix-Sockets
Runtime-Dateien
generierte Konfigurationen
temporäre Transaktionsdateien
lokale Laufzeitinformationen

Persistente Managerdaten gehören in data, nicht in srv.

7. Struktur jeder App-Instanz

Jede installierte App-Instanz erhält eine UUID.

Der Pfad lautet:

/sites/<appname>-<uuid>/


Beispiel mit ausschließlich synthetischer UUID:

/sites/csv-reporting-550e8400-e29b-41d4-a716-446655440000/


Jede Instanz enthält:

/sites/<appname>-<uuid>/
├── data/
├── frontend/
├── backend/
└── srv/

7.1 data/

Enthält persistente Daten der Instanz:

Anwendungskonfiguration
Regeln
Statusdaten
Cache, wenn dieser persistent sein soll
importierte Daten
Uploads
Migrationsstatus
sonstige fachliche Anwendungsdaten

Die Anwendung muss klar dokumentieren:

welche Daten persistent sind
welche Daten gesichert werden müssen
welche Daten neu erzeugt werden können
welche Daten beim Entfernen standardmäßig erhalten bleiben
7.2 frontend/

Enthält:

HTML
CSS
JavaScript
SVG-Dateien
Icons
weitere statische Assets

Im Frontend dürfen keine Geheimnisse liegen.

7.3 backend/

Enthält:

anwendungsspezifisches Python-Backend
Backend-Einstiegspunkt
Django-Konfiguration
API-Endpunkte
anwendungsspezifische Verarbeitung
App-Manifest
Management-Adapter
Health Check

Generische Python-Funktionen werden aus ftpkit-pylib importiert.

7.4 srv/

Enthält:

virtuelle Python-Umgebung
Unix-Socket
Runtime-Dateien
generierte Laufzeitkonfiguration
temporäre laufzeitbezogene Zustände

Persistente fachliche Daten gehören nicht in srv.

8. UUID-Regeln

Jede App-Instanz besitzt eine UUID.

Die UUID wird bei der Installation einmal erzeugt und danach nicht geändert.

Die UUID ist die technische Identität der Instanz.

Nicht eindeutig sind:

Appname
Anzeigename
Repositoryname
Domain
IP-Adresse
Port
URL-Pfad
systemd-Dienstname ohne Registry-Zuordnung

Instanzen dürfen niemals nur anhand des sichtbaren Appnamens verändert oder gelöscht werden.

Der Instanzordner folgt:

<normalisierter-appname>-<uuid>


Der Appname dient nur der Lesbarkeit.

Die Registry verbindet die UUID mit allen weiteren Informationen.

9. Globale Registry

Die globale Registry wird vom Repository backend verwaltet.

Die Registry enthält mindestens:

Anwendungskennung
Instanz-UUID
Anzeigename
Version
Protokollversion
Installationspfad
Datenpfad
Frontendpfad
Backendpfad
Runtimepfad
Sicherungspfad
Dienstname
Dienstbenutzer
Bind-IP
Backend-Port oder Unix-Socket
öffentlicher Port
Domain oder IP
URL-Pfad
vollständige öffentliche URL
HTTP- oder HTTPS-Modus
Zertifikatstyp
nicht geheime Zertifikatsmetadaten
Management-Endpunkt
Health-Endpunkt
unterstützte Fähigkeiten
Installationszeit
letzte Aktualisierung
Eigentümer registrierter Ports und Ressourcen

Die Registry muss:

atomisch geschrieben werden
versioniert sein
migrationsfähig sein
gegen parallele Schreibzugriffe geschützt sein
vor Beschädigung gesichert werden
keine Passwörter oder privaten Schlüssel enthalten

Modelle und generische Registry-Hilfen gehören in ftpkit-pylib.

Die zentrale Registry-Geschäftslogik gehört in backend.

10. App-Manifest

Jede kompatible App stellt ein versioniertes Manifest bereit.

Das Manifest beschreibt mindestens:

Anwendungskennung
Anzeigename
App-Version
Manifestversion
Management-Protokollversion
Backendtyp
Startkommando
Health Check
benötigte Verzeichnisse
persistente Verzeichnisse
benötigte Dienste
Datenbankanforderungen
Netzwerkfähigkeiten
unterstützte URL-Pfade
TLS-Fähigkeiten
Sicherungsumfang
Wiederherstellungsumfang
Upgradefähigkeit
Import- und Exportfähigkeit
Management-Fähigkeiten

Mögliche Fähigkeiten:

status
start
stop
restart
health
logs
backup
restore
upgrade
configure
remove
import
export


Der Manager darf nur Fähigkeiten verwenden, die von der App deklariert werden.

11. Management-Schnittstelle

Kompatible Apps besitzen eine versionierte Management-Schnittstelle.

Die Schnittstelle erlaubt dem zentralen Backend-Manager:

Status abzufragen
Health Checks auszuführen
App-Versionen abzufragen
Konfigurationsschema abzurufen
unterstützte Fähigkeiten abzufragen
Backupumfang zu bestimmen
Wiederherstellung vorzubereiten
Upgradeanforderungen zu prüfen
anwendungsspezifische Validierungen auszuführen

Systemweite Änderungen werden nicht direkt von App-Backends ausgeführt.

Dazu gehören:

Benutzer erstellen
Dienste installieren
Caddy verändern
Ports übernehmen
Zertifikate installieren
Datenbanken löschen
Instanzordner löschen
Pakete installieren

Diese Aktionen werden vom zentralen Backend-Manager geplant und über validierte Systemfunktionen ausgeführt.

12. Rechte und Isolation

Jede App und jede Instanz wird bezüglich ihrer Rechte getrennt betrachtet.

Grundregeln:

keine App läuft als root
keine App erhält pauschale Schreibrechte auf /sites
keine App darf in die Verzeichnisse anderer Instanzen schreiben
Dienstbenutzer werden nur erstellt, wenn sie benötigt werden
jede notwendige Dienstidentität wird getrennt behandelt
der Backend-Manager erhält einen eigenen Dienstbenutzer
privilegierte Aktionen werden klar begrenzt
es gibt keine freie Root-Shell über die GUI
Benutzereingaben werden nicht direkt als Shell-Kommandos verwendet
private Schlüssel erhalten restriktive Rechte
Caddy erhält nur notwendige Leserechte
Backends verwenden bevorzugt Unix-Sockets oder interne Ports
PostgreSQL wird nicht öffentlich freigegeben

CSV Reporting benötigt nicht automatisch einen eigenen interaktiven Benutzer.

Der Backend-Manager benötigt einen eigenen Dienstbenutzer und einen kontrollierten Mechanismus für notwendige Systemänderungen.

13. Automatische Installation des Backend-Managers

Wenn ein App-Setup oder eine Funktion aus ftpkit-shlib ausgeführt wird, muss zuerst geprüft werden, ob der zentrale Backend-Manager vorhanden und funktionsfähig ist.

Prüfreihenfolge:

Existiert /sites/backend/?
Existiert die globale Registry?
Ist der Backend-Manager registriert?
Existiert der Managerdienst?
Ist der Managerdienst aktiv?
Antwortet der Manager-Health-Endpunkt?
Ist die Management-Protokollversion kompatibel?

Wenn der Backend-Manager fehlt:

Betriebssystem und Voraussetzungen prüfen
Repository backend aus der festgelegten Quelle laden
Version und Integrität prüfen
/sites/backend/ erstellen
Managerdateien installieren
virtuelle Python-Umgebung erstellen
Manager-Dienstbenutzer erstellen
systemd-Dienst installieren
Bootstrap-HTTPS starten
Registry initialisieren
Manager registrieren
Health Check ausführen
ursprüngliche App-Installation an den Manager übergeben

Wenn die Managerinstallation fehlschlägt, darf keine halb verwaltete App-Installation zurückbleiben.

14. Bootstrap-Setup

Der Shell-Aufruf soll möglichst klein bleiben.

Beispiel:

curl -fsSL <setup-url> | sudo sh


Das Terminal soll nur notwendige Informationen anzeigen:

Setup Manager

Setup-Assistent:
https://<lan-ip>:<freier-port>

Abbruch: Strg+C
Log: <logpfad>


Die Setup-GUI wird direkt über IP und Port aufgerufen:

https://10.0.0.10:8765


Es ist kein zusätzlicher Pfad wie /setup notwendig.

Der Bootstrap-Modus:

wählt automatisch einen freien Port
verwendet selbstsigniertes HTTPS
bindet standardmäßig an eine geeignete LAN-IP
ist zeitlich begrenzt
verwendet eine kurzlebige Sitzung
erlaubt keine freie Shell
bereinigt temporäre Dateien
überführt die Installation in den dauerhaft geschützten Backend-Manager
15. Backend-Manager-GUI

Die Manager-GUI verwaltet eigene und andere kompatible Apps.

15.1 Anwendungen und Instanzen

Die GUI ermöglicht:

kompatible Apps auflisten
Instanzen auflisten
neue Instanz installieren
bestehende Instanz sicher aktualisieren
Instanz neu aufbauen
Instanz starten
Instanz stoppen
Instanz neu starten
Status anzeigen
Version anzeigen
URL anzeigen
Logs anzeigen
Sicherung erstellen
Sicherung wiederherstellen
Instanz entfernen
15.2 Netzwerk

Die GUI ermöglicht:

Bind-IP auswählen
internen Backend-Port auswählen
öffentlichen Port auswählen
Unix-Socket konfigurieren
Domain oder IP konfigurieren
HTTP oder HTTPS auswählen
URL-Pfad konfigurieren
bestehenden Reverse Proxy verwenden
Caddy verwenden
verfügbare Ports anzeigen
Portkonflikte anzeigen
eigenen Port beim Upgrade wiederverwenden
15.3 URL-Pfade

Unterstützt werden:

/

/csv-reporting

/<anderer-validierter-pfad>


Der Pfad ist pro Instanz konfigurierbar.

Vor Anwendung wird die vollständige Ergebnis-URL angezeigt.

15.4 Zertifikate

Die GUI unterstützt:

Caddy interne CA
automatisch verwaltetes öffentliches Zertifikat
vorhandenes Serverzertifikat
privaten Schlüssel
optionale CA-Kette
HTTPS hinter bestehendem Reverse Proxy
Zertifikatsname
Ablaufdatum
Fingerabdruck
Root-CA für Clients
Zertifikatsaustausch
Zertifikatsinformationen

Private Schlüssel werden niemals über die GUI zurückgegeben oder angezeigt.

Caddys interne CA wird nicht entfernt, wenn eine einzelne App gelöscht wird.

16. Systemänderungspläne

Vor jeder relevanten Systemänderung wird ein verständlicher Plan erzeugt.

Der Plan enthält:

Aktion
betroffene App
betroffene Instanz-UUID
betroffene Dateien
betroffene Verzeichnisse
betroffene Dienste
betroffene Ports
betroffene Benutzer und Gruppen
Proxyänderungen
Zertifikatsänderungen
Datenbankänderungen
erwartete Downtime
Sicherung
Rollback-Strategie
Risikostufe

Diese Änderungen erfordern eine ausdrückliche Bestätigung:

Paketinstallation
Paketentfernung
Benutzererstellung
Benutzerentfernung
Änderung an Caddy
Änderung an Apache
Änderung an Nginx
Portübernahme
Dienstinstallation
Dienstentfernung
Zertifikatsinstallation
Zertifikatsentfernung
Datenbankerstellung
Datenbanklöschung
rekursives Löschen
Änderung gemeinsamer Backend-Dateien

Es dürfen keine zusätzlichen systemverändernden Funktionen ohne Plan und Bestätigung eingeführt werden.

17. Installationsablauf

Eine Installation wird als Transaktion durchgeführt.

Ablauf:

Systemzustand erfassen
Backend-Manager prüfen oder installieren
Registry prüfen
App-Manifest laden
Eingaben validieren
Konflikte ermitteln
Ports prüfen
Dienste prüfen
Webserver prüfen
Änderungsplan erzeugen
Bestätigung einholen
Sicherung anlegen
UUID erzeugen
Instanzverzeichnisse erstellen
App installieren
Python-Umgebung erstellen
Konfiguration generieren
Datenbank vorbereiten
Dienst installieren
Proxy konfigurieren
Anwendung starten
Health Checks durchführen
Registry atomisch aktualisieren
Ergebnis anzeigen

Bei einem Fehler wird zurückgerollt.

Es darf keine halb installierte, unregistrierte Instanz zurückbleiben.

18. Upgrade und Neuaufbau

Ein Upgrade funktioniert möglichst wie eine saubere Neuinstallation.

Ablauf:

Instanz über UUID identifizieren
aktuellen Zustand erfassen
vollständige Sicherung erstellen
Änderungsplan anzeigen
Bestätigung einholen
Dienst stoppen
bisherigen App-Code ersetzen
virtuelle Python-Umgebung neu erstellen
neue Abhängigkeiten installieren
persistente Daten übernehmen
Konfiguration migrieren
Datenbankmigration ausführen
Proxykonfiguration aktualisieren
Dienst starten
Health Checks durchführen
Registry aktualisieren
Sicherungspfad anzeigen

Bei einem Fehler:

neue Version stoppen
vorherige Dateien wiederherstellen
vorherige Konfiguration wiederherstellen
vorherigen Dienstzustand wiederherstellen
vorherige Proxykonfiguration wiederherstellen
vorherige Registry wiederherstellen
vorherige Version prüfen
19. Portregeln

Ein belegter Port darf den Ablauf nicht einfach abbrechen.

Der Manager zeigt:

Port
Status
Prozess
Dienst
registrierte Instanz
Eigentümer
wiederverwendbar oder fremd

Beispiel:

80     apache2              belegt
443    apache2              belegt
8080   anderer Dienst       belegt
8443   eigene Instanz       wiederverwendbar
8444   frei
8445   frei


Ein Port derselben Instanz darf beim Upgrade wiederverwendet werden.

Ein fremder Port darf nicht ohne bestätigte Systemänderung übernommen werden.

Bei ungültiger oder belegter Auswahl wird erneut gefragt. Der gesamte Ablauf wird deshalb nicht abgebrochen.

20. Caddy und vorhandene Webserver

Caddy ist der bevorzugte Reverse Proxy für neue kompatible Installationen.

Vorhandene Webserver werden erkannt:

Caddy
Apache
Nginx
unbekannte Listener

Fremde Webserver werden nicht automatisch gestoppt.

Der Manager kann anbieten:

Anwendung auf separatem Port
Integration hinter bestehendem Proxy
neue Caddy-Site
vorhandene eigene Caddy-Site ersetzen
bestätigte Übernahme von Port 80 oder 443

Caddy-Konfigurationen werden vor Aktivierung validiert.

Bei ungültiger Konfiguration wird die vorherige Konfiguration wiederhergestellt.

21. Entfernen einer Instanz

Entfernen wird in getrennte Optionen aufgeteilt:

Anwendung entfernen
systemd-Dienst entfernen
Proxy-Site entfernen
Konfiguration entfernen
Statusdaten entfernen
Datenbank entfernen
Sicherungen entfernen

Standardmäßig bleiben erhalten:

persistente Daten
Datenbank
Sicherungen
gemeinsame interne CA
andere Instanzen
gemeinsam verwendete Bibliotheken
Backend-Manager

Eine Instanz wird ausschließlich über ihre UUID entfernt.

Vor dem Löschen werden Pfade erneut gegen die Registry und erlaubte Basispfade geprüft.

22. Verantwortung von ftpkit-pylib

ftpkit-pylib enthält generische Python-Funktionen für:

UUID-Erzeugung
UUID-Validierung
atomisches Schreiben
atomisches JSON
Dateisperren
Registry-Datenmodelle
Registry-Migrationen
App-Manifeste
Capability-Modelle
Management-Protokoll-Modelle
IP-Validierung
Domainvalidierung
Portvalidierung
URL-Pfadvalidierung
sichere Pfade
Zertifikatsmetadaten
Fingerabdrücke
Sicherungsmetadaten
Änderungspläne
Risikomodelle
Bestätigungsnachweise
strukturierte Ergebnisse
strukturierte Fehler

ftpkit-pylib führt standardmäßig keine destruktiven Systemaktionen aus.

Planung, Modellierung, Validierung und Ausführung werden getrennt.

ftpkit-pylib besitzt keine Abhängigkeit von:

backend
csv-reporting
23. Verantwortung von ftpkit-shlib

ftpkit-shlib enthält generische POSIX-Shell-Funktionen für:

Betriebssystemerkennung
Paketmanagererkennung
Paketprüfung
Paketinstallation
Benutzer
Gruppen
Verzeichnisse
Rechte
Ports
Listener
Prozesse
Webservererkennung
systemd
Caddy-Validierung
Sicherung
Wiederherstellung
Rollback
atomare Dateiersetzung
Logging
Terminalausgabe
Cleanup
Signalbehandlung
Zertifikatsdateiprüfung
Bootstrap des Backend-Managers

Die Bibliothek verwendet möglichst POSIX sh.

Nicht ohne klare Notwendigkeit verwenden:

Bash-Arrays
[[ ... ]]
Prozesssubstitution
Bash-spezifische Syntax

Alle Variablen werden sicher gequotet.

Benutzereingaben werden nicht mit eval ausgeführt.

24. Verantwortung von backend

Das Repository backend enthält den zentralen Server Manager.

backend ist verantwortlich für:

globale Registry
Setup-GUI
Manager-GUI
App-Übersicht
Instanzübersicht
Installation
Upgrade
Neuaufbau
Sicherung
Wiederherstellung
Rollback
Entfernen
Portverwaltung
Caddy-Verwaltung
Zertifikatsverwaltung
Dienstverwaltung
Health Checks
App-Manifeste
Capability-Prüfung
Management-API
Autorisierung
Bestätigung von Systemänderungen

backend enthält keine CSV-spezifische Geschäftslogik.

backend darf nicht von csv-reporting abhängen.

25. Verantwortung von csv-reporting

CSV Reporting enthält:

CSV-Abruf
CSV-Parsing
CSV-Cache
Ansichten index, map, raw und edit
Filter
Regeln
Spaltenauswahl
Spaltenumbenennung
Links
Downloadfilter
Import
Export
Autosave
Health Check
App-Manifest
Backend-Manager-Adapter

CSV Reporting darf keine globale App-Verwaltung implementieren.

26. CSV-Reporting-Editor

Der Editor ist standardmäßig immer aktiviert.

Das Setup fragt nicht mehr:

Regel-Editor true/false


Im Backend existiert genau eine klar benannte Defaultvariable, über die ein Administrator den Editor bewusst manuell deaktivieren kann.

Der Editor enthält nur notwendige Bereiche:

Allgemein
Spalten
Links
Downloadfilter
Regeln
Import
Export
Autosave-Status

Die Bereiche werden kompakt gewechselt.

Keine langen verschachtelten Ausklappmenüs.

Overlays:

liegen vollständig im Viewport
sind responsiv
besitzen klare Eingabefelder
erzeugen keine horizontale Seitenverschiebung
verwenden dieselbe Designsprache wie die restliche App
27. Automatisches Speichern

Änderungen im Editor werden automatisch gespeichert.

Anforderungen:

kurze Verzögerung nach Eingabe
mehrere schnelle Änderungen zusammenfassen
parallele Speicherungen serialisieren
Konfigurationsvergleich verhindert unnötige Schreibvorgänge
Backend validiert erneut
Backend schreibt atomisch
importierte Konfiguration nach Bestätigung speichern
Fehler sichtbar anzeigen

Zustände:

Änderungen
Speichert
Gespeichert
Speichern fehlgeschlagen


Es gibt keine unnötige manuelle Speichern-Schaltfläche.

28. CSV-Reporting-Import

Das neue Format ist versioniert und enthält mindestens:

format
version
title
heading
show_columns
column_renames
rules
enable_links
column_links
download_filters


Unterstützte Importformen:

aktuelles Format
Objekt unter config
altes JSON-Format
leere PHP-Arrays als JSON-Listen
bekannte alte Regelformate
bekannte alternative Feldnamen
alte deaktivierte Regeln

Importierte Werte werden validiert, normalisiert und erst danach gespeichert.

Fehlerhafte Regeln dürfen nicht stillschweigend verworfen werden.

29. Alte Regelmigration

Das alte Escapeformat muss vollständig unterstützt werden:

$$$$$&$$$$$  -> &
$$$$$=$$$$$  -> =
$$$$$≠$$$$$  -> ≠
$$$$$$$$$$   -> $$$$$


!... kennzeichnet eine deaktivierte Regel.

Bei alten deaktivierten Regeln können conditions leer sein. Die ursprünglichen Bedingungen können nur noch codiert in description stehen.

Importablauf:

Format erkennen
Escapeformat korrekt decodieren
aktive Regeln erkennen
deaktivierte Regeln erkennen
Bedingungen rekonstruieren
deaktivierte Regeln deaktiviert lassen
rekonstruierte Bedingungen in stash_conditions speichern
lesbare Beschreibung erzeugen
Escape-Dollarfolgen nicht in der GUI anzeigen
Aktivieren vollständig ermöglichen
nicht rekonstruierbare Regeln melden
Importstatistik anzeigen

Die Importstatistik enthält:

aktive Regeln
deaktivierte Regeln
fehlerhafte Regeln
insgesamt gespeicherte Regeln

30. Generische Inhalte

Öffentliche Repositorys dürfen keine Rückschlüsse auf ein konkretes Einsatzsystem enthalten.

Nicht enthalten:

konkrete Ticketsystemnamen
konkrete Kunden
interne IP-Adressen
interne URLs
reale CSV-Quellen
reale Spalten
reale Filter
reale Titel
reale Überschriften
echte Zertifikate
private Schlüssel
Passwörter
Tokens

Generische Standardtexte verwenden beispielsweise:

CSV Reporting


Beispiele verwenden ausschließlich eindeutig synthetische Werte.

31. Dokumentation

Jedes Repository enthält:

AGENTS.md
README.md
CHANGELOG.md
LICENSE


Anwendungsrepositorys enthalten zusätzlich:

structure.md

README.md

Kurz und nutzerorientiert:

Zweck
Installation
Verwendung
wichtigste Konfiguration
Verweise auf weitere Dokumentation
structure.md

Technisch und konkret:

öffentliche Repositorydateien
lokal erzeugte Dateien
generierte Dateien
persistente Daten
Secrets
/sites/-Struktur
UUID-Pfade
Registry
Backend-Manager
App-Backend
Frontend
Runtime
systemd
Caddy
Sicherung
Upgrade
Rollback
Entfernen
Schnittstellen zu ftpkit-pylib
Schnittstellen zu ftpkit-shlib
Schnittstellen zu backend
32. Sicherheitsregeln

Verbindlich für alle Repositorys:

keine App läuft als root
keine freie Shell in einer Weboberfläche
keine unvalidierten Systemkommandos
keine Secrets in Logs
keine privaten Schlüssel in API-Antworten
CSRF-Schutz für schreibende Browseraktionen
authentifizierte Management-Schnittstellen
Capability-Prüfung
atomische Registry
atomische Konfigurationsänderungen
sichere Dateirechte
Pfad-Traversal verhindern
rekursives Löschen nur innerhalb validierter erlaubter Pfade
PostgreSQL nicht öffentlich freigeben
Backends bevorzugt über Unix-Sockets
Bootstrap-Zugriff zeitlich begrenzen
Systemänderungen planen und bestätigen
vor destruktiven Änderungen sichern
Rollback implementieren und testen
fremde Dienste nicht ungefragt verändern
fremde Ports nicht ungefragt übernehmen
33. Vorgehen für jeden Agent

Vor jeder Änderung:

Repositoryname feststellen.
eigene Rolle aus Abschnitt 2 bestimmen.
diese Datei vollständig lesen.
vorhandenen Repositoryzustand untersuchen.
README, Changelog und structure.md lesen.
bestehende Implementierungen suchen.
generischen und projektspezifischen Anteil trennen.
zuständiges Repository bestimmen.
unerlaubte Duplikation vermeiden.
Sicherheitsfolgen bewerten.
Migrationsfolgen bewerten.
Tests festlegen.
Änderung implementieren.
passende Tests ausführen.
Dokumentation aktualisieren.
Changelog aktualisieren.
repositoryweit nach Betriebsdaten und Secrets suchen.
Ergebnis auf Abhängigkeiten zu den anderen Repositorys prüfen.

Wenn eine Änderung eigentlich in ein anderes Repository gehört, darf der Agent keine lokale Ersatzimplementierung erstellen.

Der Agent muss stattdessen klar festhalten:

benötigte Änderung
zuständiges Repository
benötigte Version
notwendige Anpassung im aktuellen Repository

34. Verbotene Vorgehensweisen

Nicht zulässig:

generische Funktionen in mehreren Backends kopieren
Shell-Helfer in jedem Setup neu implementieren
ein fünftes Repository für den Server Manager einführen
server-manager als Repositorynamen verwenden
/srv/webapps als neuen Standard weiterverwenden
Apps nur anhand ihres Namens identifizieren
alle Apps unter demselben Benutzer ausführen
Managerlogik in CSV Reporting implementieren
CSV-Logik im Backend-Manager implementieren
ftpkit-pylib von Apps abhängig machen
ftpkit-shlib von einer konkreten App abhängig machen
fremde Webserver ungefragt stoppen
belegte Ports ohne Dialog übernehmen
bei belegtem Port den gesamten Ablauf sofort abbrechen
Upgrades ohne Sicherung durchführen
Registry nicht atomisch bearbeiten
Daten bei Fehlern teilweise ersetzen
fehlerhafte Imports stillschweigend speichern
alte Regeln stillschweigend verwerfen
private Schlüssel anzeigen
Systemänderungen ohne Plan und Bestätigung ausführen
konkrete Betriebsdaten in öffentliche Repositorys übernehmen
35. Abhängigkeitsrichtung

Die erlaubte Abhängigkeitsrichtung lautet:

ftpkit-pylib
    ↑
    ├── backend
    └── csv-reporting

ftpkit-shlib
    ↑
    ├── backend-Bootstrap
    └── csv-reporting-Bootstrap

backend
    ↑
    └── csv-reporting kommuniziert über die Management-Schnittstelle


Verboten:

ftpkit-pylib → backend
ftpkit-pylib → csv-reporting
ftpkit-shlib → csv-reporting
backend → csv-reporting-Geschäftslogik

36. Tests und Freigabekriterien

Passend zum Repository müssen vor Veröffentlichung erfolgreich sein:

Python-Syntax
Python-Unit-Tests
Python-Paket-Build
Python-Paket-Import
Shell-Syntax
ShellCheck
JavaScript-Syntax
Browser-Tests
API-Tests
Importtests
Migrationstests
Autosave-Tests
Registry-Tests
UUID-Tests
Mehrfachinstallations-Tests
Portkonflikt-Tests
Upgrade-Tests
Rollback-Tests
Sicherungstests
Wiederherstellungstests
Deinstallationstests
Caddy-Validierung
systemd-Prüfung
ZIP-Integrität


Zusätzlich repositoryweit prüfen:

keine internen IP-Adressen
keine realen Domains
keine realen CSV-Quellen
keine Kunden- oder Systemnamen
keine Passwörter
keine Tokens
keine privaten Schlüssel
keine temporären Dateien
keine __pycache__-Verzeichnisse
keine duplizierte generische Logik
keine falsche Abhängigkeitsrichtung

37. Endgültiges Zielbild

Das fertige System besitzt:

genau vier Repositorys
genau vier klar zugeordnete Agents
backend als zentralen Server Manager
ftpkit-pylib als generische Python-Bibliothek
ftpkit-shlib als generische Shell-Bibliothek
csv-reporting als konkrete verwaltete App
/sites/ als neuen Basispfad
/sites/backend/ als Managerinstallation
/sites/<appname>-<uuid>/ für App-Instanzen
pro Instanz data, frontend, backend und srv
UUID-basierte Mehrfachinstallationen
getrennte Rechte pro App und Instanz
globale Registry
App-Manifeste
versionierte Management-Schnittstelle
automatische Installation des Backend-Managers
integrierte HTTPS-Setup-GUI
freie IP-, Port- und Pfadwahl
Caddy- und Zertifikatsverwaltung
sichere Systemänderungspläne
Bestätigung vor Systemänderungen
Sicherung und Rollback
keine duplizierte Logik
generisches CSV Reporting
vollständige alte Regelmigration
zuverlässigen Import
zuverlässiges Autosave
einfache Erweiterbarkeit um zukünftige kompatible Webapps

Diese `AGENTS.md` ist der gemeinsame verbindliche Ausgangspunkt. Der jeweilige Repositoryname bestimmt die Rolle und Zuständigkeit des Agents.
