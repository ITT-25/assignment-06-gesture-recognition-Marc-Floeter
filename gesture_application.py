import pyglet
import random
import threading
from pyglet.window import mouse
from recognizer import OneDollarRecognizer
from pointing_input import HandDetection

# Spieleinstellungen
ROUND_TIME = 10.0
WIN_SCORE = 5
MAX_FAILURES = 3

# Gesture Recognizer
GESTURES = {
    "Lumos": "lumos",
    "Expelliarmus": "expelliarmus",
    "Alohomora": "alohomora",
    "Wingardium Leviosa": "leviosa"
}
SUBJECT = "Spieler"
TEMPLATES_PATH = "spells"
RESAMPLE_POINTS = 64
BB_SIZE = 250

# Hand Detection 
SHOW_CAM = False
DRAWING_THRESHOLD = 30 # Max Abstand Zeigefinger zu Daumen zum Auslösen des Malens in px
DEBUG = False # Anzeige von Prints, Landmarks etc.
NUM_HANDS = 1
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE = 0.7

# GUI
window = pyglet.window.Window(800, 600, "Hogwarts Zaubertraining")
batch = pyglet.graphics.Batch()

status_label = pyglet.text.Label("", x=10, y=window.height - 30, font_size=16)
gesture_label = pyglet.text.Label("", x=10, y=window.height - 60, font_size=16)
score_label = pyglet.text.Label("", x=10, y=window.height - 90, font_size=16)
timer_label = pyglet.text.Label("", x=window.width - 150, y=window.height - 30, font_size=16)

gesture_overview = pyglet.image.load("spell_overview.png")
gesture_overview_sprite = pyglet.sprite.Sprite(gesture_overview, x=0, y=0)

points = [] # Liste der Punkte der gezeichneten Geste/Zauberspruch
drawn_lines = [] # Bisher gezeichneter Pfad der Geste/Zauberspruch

# Zaubererkennung
recognizer = OneDollarRecognizer(BB_SIZE, RESAMPLE_POINTS, TEMPLATES_PATH, SUBJECT)
enough_points = False
hand_detector = HandDetection(NUM_HANDS, DETECTION_CONFIDENCE, TRACKING_CONFIDENCE, DRAWING_THRESHOLD, SHOW_CAM, DEBUG)
threading.Thread(target=hand_detector.run, daemon=True).start()

# Spielvariablen
score = 0
failures = 0
current_target = None
time_left = ROUND_TIME
hand_was_drawing = False
game_over = False
startscreen = True


########################################################################################################

# Neues Spiel starten (Spielvariablen zurücksetzen)
def new_game():
    global score, failures, game_over, startscreen

    score = 0
    failures = 0
    game_over = False
    startscreen = True


# Neue Runde (Random Zauber auswählen, der nachzuzueichnen ist, Timer setzen)
def new_round():
    global current_target, time_left

    current_target = random.choice(list(GESTURES.keys()))
    gesture_label.text = f"Wirke: {current_target}"
    time_left = ROUND_TIME


# Punkte, gezeichnete Linien und Punktezählung zurücksetzen
def reset_drawing():
    global enough_points
    
    enough_points = False
    points.clear()
    drawn_lines.clear()


# Beim Mausklick ersten Punkt der Geste setzen
@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT and not startscreen:
        points.clear()
        points.append((x, y))


# Bei Maus Drag immer wieder Linien zwischen bisherigem Pfad und neuster Position der Maus setzen
@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if buttons & mouse.LEFT and not startscreen:
        create_line(x, y)


# Auswertung der Geste nach Loslassen der linken Maustaste
@window.event
def on_mouse_release(x, y, button, modifiers):
    global score, failures, enough_points, game_over

    if button == mouse.LEFT and not startscreen and not game_over:
        create_line(x, y) # Linie bis zum letzten Punkt fortsetzen
        if len(points) >= recognizer.n: # Prüfen, ob Geste aus genügend Punkten bestand (groß/lang genug ist)
            enough_points = True
            name, confidence_score = recognizer.recognize(points)
            if name == GESTURES[current_target]: # Falls gerade gewollte Geste gemalt -> Score erhöhen
                score += 1
                status_label.text = "Richtig!"
            else: # Falls faksche Geste erkannt -> Fehler erhöhen
                failures += 1
                status_label.text = f"Falsch, das war ziemlich sicher ({confidence_score}) {name}!"
            update_game_state() # Spielzustand anpassen
        else: # Falls zu wenige Punkte erkannt
            status_label.text = "Schwinge den Zauberstab etwas ausgiebiger!"
        reset_drawing()


# Linien, aus denen die Gesten bestehen, erstellen
def create_line(x, y):
    if points:
        x1, y1 = points[-1]
        line = pyglet.shapes.Line(x1, y1, x, y, thickness=2, color=(255, 255, 255), batch=batch)
        drawn_lines.append(line) # Linie abspeichern
    points.append((x, y)) # Endpunkt abspeichern (für Gestenerkennung)


# Tastendruck Verarbeitung
@window.event
def on_key_press(symbol, modifiers):
    global startscreen, score, failures, game_over

    if startscreen and symbol == pyglet.window.key.ENTER:
        startscreen = False
        new_round()
    elif game_over and symbol == pyglet.window.key.ENTER:
        new_game()


@window.event
def on_draw():
    window.clear()
    if startscreen:
        gesture_overview_sprite.draw()
    else:
        batch.draw()
        gesture_label.draw()
        status_label.draw()
        score_label.draw()
        timer_label.draw()
        if game_over:
            pyglet.text.Label("Spiel beendet - drücke ENTER für Neustart", x=window.width // 2 - 180, y=window.height // 2, font_size=18).draw()


# Nach Auswertung Spielzustände anpassen (Nächste Runde, falls nicht Score hoch genug / Fehler zu viele)
def update_game_state():
    global game_over

    score_label.text = f"Punkte: {score} | Fehler: {failures}"
    if score >= WIN_SCORE:
        status_label.text = "Lektion bestanden!"
        game_over = True
    elif failures >= MAX_FAILURES:
        status_label.text = "Verzeihung, zu viele Fehler. Das musst du noch üben!"
        game_over = True
    else:
        new_round()
        reset_drawing()


def update_timer(dt):
    global time_left, failures

    if not startscreen and not game_over:
        time_left -= dt
        timer_label.text = f"Zeit: {time_left:.1f}s"
        if time_left <= 0:
            failures += 1
            status_label.text = "Zeit abgelaufen!"
            update_game_state()


pyglet.clock.schedule_interval(update_timer, 0.1)

pyglet.app.run()
