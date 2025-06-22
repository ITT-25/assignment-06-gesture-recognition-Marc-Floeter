# $1 gesture recognizer 
import math, os
import xml.etree.ElementTree as ET
from datetime import datetime

PHI = 0.5 * (-1.0 + math.sqrt(5.0))


class OneDollarRecognizer:

    def __init__(self, bb_size, resample_points, templates_path, subject):
        self.size = bb_size
        self.n = resample_points
        self.origin = (0, 0)
        self.templates = []
        self.min_angle = math.radians(-45)
        self.max_angle = math.radians(45)
        self.angle_precision = math.radians(2)
        self.subject = subject

        self.load_templates_from_xml(templates_path)


    def add_template(self, name, points):
        normalized = self.normalize(points)
        self.templates.append((name, normalized))


    def recognize(self, points):
        candidate = self.normalize(points)
        max_possible_distance = 0.5 * math.sqrt(self.size ** 2 + self.size ** 2)
        current_min_distance = max_possible_distance
        best_template = None

        for name, template_points in self.templates:
            d = self.distance_at_best_angle(candidate, template_points, self.min_angle, self.max_angle, self.angle_precision)
            if d < current_min_distance:
                current_min_distance = d
                best_template = name
        score = 1 - current_min_distance / max_possible_distance

        return best_template, score


# NORMALISIERUNG DER GESTENPUNKTE #############################################################

    def normalize(self, points):
        points = self.resample(points, self.n)
        radians = self.indicative_angle(points)
        points = self.rotate_by(points, -radians)
        points = self.scale_to(points, self.size)
        points = self.translate_to(points, self.origin)

        return points


    def resample(self, points, n):
        path_len = self.path_length(points)
        if path_len == 0:
            print("WARNUNG: Pfadlänge = 0 – Punkte vermutlich identisch.")
            return [points[0]] * n

        I = path_len / (n - 1)
        D = 0.0
        new_points = [points[0]]
        curr_point = points[0]

        i = 1
        while i < len(points):
            next_point = points[i]
            d = self.distance(curr_point, next_point)

            if d == 0.0:
                i += 1
                continue

            if D + d >= I:
                t = (I - D) / d
                qx = curr_point[0] + t * (next_point[0] - curr_point[0])
                qy = curr_point[1] + t * (next_point[1] - curr_point[1])
                q = (qx, qy)
                new_points.append(q)
                curr_point = q
                D = 0.0
            else:
                D += d
                curr_point = next_point
                i += 1

        while len(new_points) < n:
            new_points.append(points[-1])

        return new_points
    

    def path_length(self, A):
        d = 0

        for i in range(1, len(A)):
            d += self.distance(A[i - 1], A[i])

        return d


    def indicative_angle(self, points):
        c = self.centroid(points)
        return math.atan2(c[1] - points[0][1], c[0] - points[0][0])


    def rotate_by(self, points, omega):
        c = self.centroid(points)
        new_points = []

        for x, y in points:
            qx = (x - c[0]) * math.cos(omega) - (y - c[1]) * math.sin(omega) + c[0]
            qy = (x - c[0]) * math.sin(omega) + (y - c[1]) * math.cos(omega) + c[1]
            new_points.append((qx, qy))

        return new_points


    def scale_to(self, points, size):
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        width = max_x - min_x
        height = max_y - min_y
        new_points = [((p[0] - min_x) * size / width,
                       (p[1] - min_y) * size / height)
                      for p in points]
        
        return new_points


    def translate_to(self, points, k):
        c = self.centroid(points)
        dx = k[0] - c[0]
        dy = k[1] - c[1]
        return [(p[0] + dx, p[1] + dy) for p in points]


    def centroid(self, points):
        x = sum(p[0] for p in points) / len(points)
        y = sum(p[1] for p in points) / len(points)
        return (x, y)

#############################################################################################

    def distance_at_best_angle(self, points, T, theta_a, theta_b, theta_delta):
        x1 = PHI * theta_a + (1 - PHI) * theta_b
        x2 = (1 - PHI) * theta_a + PHI * theta_b
        f1 = self.distance_at_angle(points, T, x1)
        f2 = self.distance_at_angle(points, T, x2)

        while abs(theta_b - theta_a) > theta_delta:
            if f1 < f2:
                theta_b = x2
                x2 = x1
                f2 = f1
                x1 = PHI * theta_a + (1 - PHI) * theta_b
                f1 = self.distance_at_angle(points, T, x1)
            else:
                theta_a = x1
                x1 = x2
                f1 = f2
                x2 = (1 - PHI) * theta_a + PHI * theta_b
                f2 = self.distance_at_angle(points, T, x2)

        return min(f1, f2)


    def distance_at_angle(self, points, T, theta):
        new_points = self.rotate_by(points, theta)
        d = self.path_distance(new_points, T)

        return d


    def path_distance(self, A, B):
        d = 0

        for i in range(len(A)):
            d += self.distance(A[i], B[i])

        return d / len(A)


    def distance(self, p1, p2):
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


# XML EXPORT UND IMPORT VON TEMPLATES ####################################################
   
    def save_templates_to_xml(self, directory):
        os.makedirs(directory, exist_ok=True)
        name_counts = {}

        for name, points in self.templates:
            count = name_counts.get(name, 0) + 1
            name_counts[name] = count
            number_str = f"{count:02}"
            filename = f"{name}{number_str}.xml"
            path = os.path.join(directory, filename)

            gesture = ET.Element("Gesture", {
                "Name": name,
                "Subject": self.subject,
                "Speed": "unknown",
                "Number": str(count),
                "NumPts": str(len(points)),
                "Milliseconds": "0",
                "AppName": "GestureRecognizer",
                "AppVer": "1.0",
                "Date": datetime.now().strftime("%A, %B %d, %Y"),
                "TimeOfDay": datetime.now().strftime("%I:%M:%S %p")
            })

            for x, y in points:
                ET.SubElement(gesture, "Point", X=str(x), Y=str(y), T="0")

            tree = ET.ElementTree(gesture)
            tree.write(path, encoding="utf-8", xml_declaration=True)


    def load_templates_from_xml(self, directory):
        print("Starte Import...")
        if not os.path.exists(directory):
            print(f"Ordner {directory} nicht gefunden. Keine Templates geladen")
            return

        for filename in os.listdir(directory):
            if filename.endswith(".xml"):
                path = os.path.join(directory, filename)
                print(f"Versuche Datei zu laden: {filename}")
                try:
                    tree = ET.parse(path)
                    root = tree.getroot()

                    name = root.attrib.get("Name", "unknown")
                    points = []
                    for pt in root.findall("Point"):
                        x = float(pt.attrib["X"])
                        y = float(pt.attrib["Y"])
                        points.append((x, y))

                    if len(points) < 2:
                        print(f"Datei {filename} enthält zu wenige Punkte, wird übersprungen.")
                        continue

                    if self.path_length(points) == 0:
                        print(f"Datei {filename} enthält nur identische Punkte – wird übersprungen.")
                        continue

                    self.add_template(name, list(points))
                    print(f"Template {filename} erfolgreich hinzugefügt.")

                except Exception as e:
                    print(f"Fehler beim Laden von {filename}: {e}")