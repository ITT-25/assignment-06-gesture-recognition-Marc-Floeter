# gesture input program for first task

import pyglet
from pyglet import shapes
from pyglet.window import mouse
from recognizer import OneDollarRecognizer
from pointing_input import HandDetection
import threading

# Gesture Recognizer Konstanten
SUBJECT = "1"
TRAINING_MODE = False # Abspeichern von Gesten möglich machen (Per STRG + T in der Anwendung umschaltbar)
TEMPLATES_PATH = "templates"
RESAMPLE_POINTS = 64
BB_SIZE = 250

# Hand Detection Konstanten
SHOW_CAM = True
DRAWING_THRESHOLD = 30 # Max Abstand Zeigefinger zu Daumen zum Auslösen des Malens in px
DEBUG = False # Anzeige von Prints, Landmarks etc.
NUM_HANDS = 1
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE = 0.7

# GUI
window = pyglet.window.Window(800, 600, "Gesture Recognizer")
status_label = pyglet.text.Label("Statuslabel", font_size=16, x=10, y=window.height - 30)
batch = pyglet.graphics.Batch()
template_name = "" # Name der zu speichernden Gesten-Template
template_name_input_label = pyglet.text.Label("Template name:", font_size=16, x=10, y=window.height - 60)

points = [] # Liste der Punkte der gezeichneten Geste
drawn_lines = [] # Bisher gezeichneter Pfad der Geste

recognizer = OneDollarRecognizer(bb_size=BB_SIZE, resample_points=RESAMPLE_POINTS, templates_path=TEMPLATES_PATH, subject=SUBJECT)
enough_points = False
hand_detector = HandDetection(NUM_HANDS, DETECTION_CONFIDENCE, TRACKING_CONFIDENCE, DRAWING_THRESHOLD, SHOW_CAM, DEBUG)
threading.Thread(target=hand_detector.run, daemon=True).start()


###################################################################################################################################

# Beim Mausklick ersten Punkt der Geste setzen
@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        points.clear()
        points.append((x, y))


# Bei Maus Drag immer wieder Linien zwischen bisherigem Pfad und neuster Position der Maus setzen
@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if buttons & mouse.LEFT:
        create_line(x, y)


# Auswertung der Geste nach Loslassen der linken Maustaste
@window.event
def on_mouse_release(x, y, button, modifiers):
    global enough_points

    if button == mouse.LEFT:
        create_line(x, y) # Linie bis zum letzten Punkt fortsetzen
        if len(points) >= recognizer.n: # Prüfen, ob Geste aus genügend Punkten bestand (groß/lang genug ist)
            enough_points = True
            if not TRAINING_MODE:
                name, score = recognizer.recognize(points) # Geste Erkennen lassen 
                if name is None:
                    status_label.text = "Keine Templates zum Einordnen vorhanden"
                else:
                    status_label.text = f"Erkannt: {name} ({score:.2f})"
                reset()
        else: # Falls zu wenige Punkte erkannt
            status_label.text = "Zu wenig Punkte erkannt"
            reset()

# Linien, aus denen die Gesten bestehen, erstellen
def create_line(x, y):
    if points:
        x1, y1 = points[-1]
        x2, y2 = x, y
        line = shapes.Line(x1, y1, x2, y2, thickness=2, color=(255, 255, 255), batch=batch)
        drawn_lines.append(line)
        points.append((x, y))


# Eingabe des Namens der zu speichernden Gesten-Template
@window.event
def on_text(text):
    global template_name

    if text.isalpha():
        template_name += text
        template_name_input_label.text = f"Template name: {template_name}"


# Tastendrucke verarbeiten
@window.event
def on_key_press(symbol, modifiers):
    global template_name, TRAINING_MODE

    # Backspace, um Eingaben aus Template-Name zu löschen
    if symbol == pyglet.window.key.BACKSPACE and template_name:
        template_name = template_name[:-1]
        template_name_input_label.text = f"Template name: {template_name}"

    # Gesten-Template mit STRG + S speichern (Falls Trainingsmodus aktiv, genügend Punkte und ein Name eingegeben)
    elif symbol == pyglet.window.key.S and (modifiers & pyglet.window.key.MOD_CTRL):
        if TRAINING_MODE:
            if enough_points:
                if template_name:
                    recognizer.add_template(template_name, list(points))
                    recognizer.save_templates_to_xml(TEMPLATES_PATH)
                    status_label.text = f"Template für '{template_name}' gespeichert"
                    reset()
                else: status_label.text = "Zuerst Template Name eingeben!"
            else:
                status_label.text = "Zu wenig Punkte!"
        else: status_label.text = "Aktiviere vor dem Zeichnen mit STRG + T den Training Modus, um Gezeichnetes als Template zu speichern"
    
    # Bereits gemalte Geste verwerfen mit STRG + G
    elif symbol == pyglet.window.key.D and (modifiers & pyglet.window.key.MOD_CTRL):
        if TRAINING_MODE:
            status_label.text = "Punkte verworfen"
            reset()
    
    # Mit STRG + T den Trainingsmodus an- oder ausschalten
    elif symbol == pyglet.window.key.T and (modifiers & pyglet.window.key.MOD_CTRL):
        TRAINING_MODE = not TRAINING_MODE
        template_name = ""
        template_name_input_label.text = f"Template name: {template_name}"
        status_label.text = "Trainingsmodus: " + ("AN" if TRAINING_MODE else "AUS")


# Geste Zurücksetzen
def reset():
    global enough_points

    enough_points = False
    points.clear()
    drawn_lines.clear()


@window.event
def on_draw():
    window.clear()
    status_label.draw()
    batch.draw()

    if TRAINING_MODE:
        template_name_input_label.draw()


pyglet.app.run()
