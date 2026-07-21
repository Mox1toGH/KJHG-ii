import math

def point_in_polygon(lat, lng, polygon_points):
    """
    Ray-casting algorithm to determine if a point is inside a polygon.
    polygon_points is a list of [longitude, latitude].
    """
    x, y = float(lng), float(lat)
    inside = False
    n = len(polygon_points)
    if n < 3:
        return False
        
    p1x, p1y = float(polygon_points[0][0]), float(polygon_points[0][1])
    for i in range(n + 1):
        p2x, p2y = float(polygon_points[i % n][0]), float(polygon_points[i % n][1])
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def distance_to_segment(lat, lon, lat1, lon1, lat2, lon2):
    """
    Approximate distance in meters from (lat, lon) to segment (lat1, lon1)-(lat2, lon2)
    using equirectangular approximation (fine for small activity zones).
    """
    lat_mid = math.radians((lat1 + lat2) / 2.0)
    
    # Convert degrees to meters
    dx1 = (lon1 - lon) * math.cos(lat_mid) * 111320.0
    dy1 = (lat1 - lat) * 110574.0
    dx2 = (lon2 - lon) * math.cos(lat_mid) * 111320.0
    dy2 = (lat2 - lat) * 110574.0

    px = dx2 - dx1
    py = dy2 - dy1
    norm = px*px + py*py
    
    if norm == 0:
        return math.hypot(dx1, dy1)
    
    u = -(dx1*px + dy1*py) / norm
    if u < 0:
        return math.hypot(dx1, dy1)
    elif u > 1:
        return math.hypot(dx2, dy2)
    else:
        ix = dx1 + u*px
        iy = dy1 + u*py
        return math.hypot(ix, iy)

def distance_to_polygon(lat, lng, polygon_points):
    """
    Returns the minimum distance in meters from the point to the polygon boundary.
    polygon_points is a list of [longitude, latitude].
    """
    min_dist = float('inf')
    n = len(polygon_points)
    if n < 3:
        return min_dist
        
    for i in range(n):
        lon1, lat1 = float(polygon_points[i][0]), float(polygon_points[i][1])
        lon2, lat2 = float(polygon_points[(i + 1) % n][0]), float(polygon_points[(i + 1) % n][1])
        dist = distance_to_segment(float(lat), float(lng), lat1, lon1, lat2, lon2)
        if dist < min_dist:
            min_dist = dist
    return min_dist

def point_fully_inside_polygon(lat, lng, accuracy_m, polygon_points):
    """
    Returns True only when the entire accuracy-radius circle around (lat, lng)
    is contained within the polygon.  Two conditions must both hold:
      1. The central point is inside the polygon.
      2. The distance from the central point to the nearest polygon edge
         is greater than the accuracy radius (so no part of the circle
         can spill outside the boundary).

    This prevents false-positive On-Entry triggers caused by a noisy GPS
    reading whose uncertainty bubble straddles a zone boundary.
    """
    if not point_in_polygon(lat, lng, polygon_points):
        return False
    # Treat accuracy=0 (or unknown) as an exact point — still inside.
    if accuracy_m <= 0:
        return True
    dist_to_boundary = distance_to_polygon(lat, lng, polygon_points)
    return dist_to_boundary >= accuracy_m

