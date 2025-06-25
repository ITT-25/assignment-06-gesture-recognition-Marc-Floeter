[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/HqZjtAXJ)

# Allgemein
Da alle Anwendungen bzw. Teilaufgaben miteinander verknüpft sind, habe ich mir erlaubt, dass alles in einem Virtual Environment läuft und entsprechend nur eine requirements.txt für alle erstellt.
PS: Da ich am Donnerstag ja leider schon wieder fehlen werde, erkläre ich mich hier nochmal bereit, den Journal Club am 03.07. wie abgesprochen zu übernehmen! Liebe Grüße an alle von der experimentalarchäologischen, mittelalterlichen Klosterbaustelle Campus Galli :) 

# 6.1 und 6.2 
- Geschrieben anhand der Pseudocode-Beschreibung von Wobbrock
- Trainiert auf die 5 Gesten rectangle, circle, check, delete und pigtail. Nach den Anforderungen von 6.2 inzwischen mit 10 Templates jeder Art (lädt Templates aus dem gleichnamigen Ordner zu Programmstart automatisch)
- Nach Anwendungsstart Geste (groß genug, min 64 Punkte) eingeben -> Name erkannter Geste wird angezeigt
- Trainingmodus ein- und ausschalten mit STRG + T. Im Trainingsmodus kann man Gesten und per Tastatur einen Namen eingeben und diese mit STRG + S abspeichern. Sie werden dann als XML-Datei exportiert. Schon gezeichnete Gesten können mit STRG + D verworfen werden.
- Die Maus kann per Zeigefinger in der Kamera gesteuert werden. Ein Mausklick erfolgt durch das Zusammenführen von Zeigefinger und Daumen.
- Obwohl die auf mediapipe_sample.py aufbauende pointing_input.py Finger korrekt erkennt und die Zeigefingerposotion auf die Maus mappt, funktioniert das Dragging in pyglet bei mir nicht.

# 6.3
Aus Zeitgründen leider entfallen

# 6.4
Ein kleines Harry Potter Zaubersprüche-Spiel, wie in der Angabe vorgeschlagen. Nach Start der Anwendung bekommt man die Gesten/Zaubersprüche mit ihren Namen angezeigt. Nach Drücken auf ENTER beginnt die erste Runde. Man muss die korrekte Zauberspruchgeste innerhalb von 10s eingeben, dann bekommt man einen Punkt. Schafft man das nicht (falsche Geste, Zeit abgelaufen) wird ein Fehler vermerkt. Nach 5 korrekten Sprüchen hat man die Lektion abgeschlossen, mit 3 Fehlern hat man nicht bestanden. Die Anwendung inkooperiert den Gesture Recognizer von Aufgabe 1 und 2, ist in der Bedienung also identisch (Trainingsmodus natürlich deaktiviert).
