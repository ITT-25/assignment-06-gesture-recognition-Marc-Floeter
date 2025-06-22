# $1 gesture recognizer 
import math

PHI = 0.5 * (-1.0 + math.sqrt(5.0))


class OneDollarRecognizer:

    def __init__(self, bb_size, resample_points):
        self.size = bb_size
        self.n = resample_points
        self.origin = (0, 0)
        self.templates = []
        self.min_angle = math.radians(-45)
        self.max_angle = math.radians(45)
        self.angle_precision = math.radians(2)


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
        I = self.path_length(points) / (n - 1)
        D = 0.0
        new_points = [points[0]]
        i = 1
        
        while i < len(points):
            d = self.distance(points[i - 1], points[i])
            if D + d >= I:
                t = (I - D) / d
                qx = points[i - 1][0] + t * (points[i][0] - points[i - 1][0])
                qy = points[i - 1][1] + t * (points[i][1] - points[i - 1][1])
                q = (qx, qy)
                new_points.append(q)
                points.insert(i, q)
                D = 0.0
            else:
                D += d
                i += 1

        if len(new_points) < n:
            new_points.append(points[-1])

        if len(new_points) < n:
            while len(new_points) < n:
                new_points.append(points[-1])
        elif len(new_points) > n:
            new_points = new_points[:n]
        
        print(len(new_points))
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
