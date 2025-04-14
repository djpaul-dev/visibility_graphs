import math
import random
import copy
import matplotlib.pyplot as plt
import sys # For recursion depth

# Increase recursion depth for point_in_polygon if needed for complex shapes
# sys.setrecursionlimit(2000) # Adjust if you encounter recursion errors

# --- Geometric Helper Functions (orientation, on_segment, do_intersect - slightly refined) ---

# Epsilon for floating point comparisons
EPSILON = 1e-9

def orientation(p, q, r):
    # Robust orientation check
    if not all(isinstance(pt, (list, tuple)) and len(pt) == 2 for pt in [p, q, r]):
         raise ValueError(f"Invalid point format provided to orientation: p={p}, q={q}, r={r}")
    try:
        val = (q[1] - p[1]) * (r[0] - q[0]) - \
              (q[0] - p[0]) * (r[1] - q[1])
    except TypeError as e:
        print(f"TypeError during orientation calculation. Points: p={p}, q={q}, r={r}")
        raise e

    if abs(val) < EPSILON: return 0  # Collinear
    return 1 if val > 0 else 2  # Clockwise or Counterclockwise

def on_segment(p, q, r):
    # Check if q lies on segment pr (assuming they are collinear)
     return (abs(orientation(p, q, r)) < EPSILON and # Ensure collinear first
            q[0] <= max(p[0], r[0]) + EPSILON and q[0] >= min(p[0], r[0]) - EPSILON and
            q[1] <= max(p[1], r[1]) + EPSILON and q[1] >= min(p[1], r[1]) - EPSILON)

def do_intersect(p1, q1, p2, q2):
    """Check if line segment 'p1q1' and 'p2q2' intersect.
       Handles collinear cases and touching endpoints more carefully."""
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case: Segments cross each other
    if o1 != 0 and o2 != 0 and o3 != 0 and o4 != 0:
        if o1 != o2 and o3 != o4:
            return True

    # Special Cases (Collinearity)
    # Check if endpoints coincide - NOT considered intersection for visibility/self-intersection
    if p1 == p2 or p1 == q2 or q1 == p2 or q1 == q2:
         return False

    # Check collinear cases where one endpoint of a segment lies on the other segment
    # Important: Check orientation first for collinearity!
    if o1 == 0 and on_segment(p1, p2, q1): return True # p1-q1-p2 collinear and p2 on segment p1q1
    if o2 == 0 and on_segment(p1, q2, q1): return True # p1-q1-q2 collinear and q2 on segment p1q1
    if o3 == 0 and on_segment(p2, p1, q2): return True # p2-q2-p1 collinear and p1 on segment p2q2
    if o4 == 0 and on_segment(p2, q1, q2): return True # p2-q2-q1 collinear and q1 on segment p2q2

    return False

def is_self_intersecting(vertices):
    """Check if the polygon defined by vertices self-intersects."""
    n = len(vertices)
    if n < 4: return False

    for i in range(n):
        p1 = vertices[i]
        q1 = vertices[(i + 1) % n]
        # Check against non-adjacent edges
        for j in range(i + 2, n):
            # Skip the edge connecting last to first if i=0, j=n-1 (adjacent through vertex 0)
            if i == 0 and j == n - 1: continue

            p2 = vertices[j]
            q2 = vertices[(j + 1) % n]

            if do_intersect(p1, q1, p2, q2):
                # print(f"Self intersection: {i}-{i+1} intersects {j}-{j+1}")
                return True
    return False

# --- NEW: Point-in-Polygon Test (Ray Casting) ---
def point_in_polygon(point, vertices):
    """
    Checks if a point is inside a polygon using the Ray Casting algorithm.
    Handles points on the boundary.
    Returns:
        True if the point is inside or on the boundary.
        False otherwise.
    """
    n = len(vertices)
    if n < 3: return False
    x, y = point
    inside = False

    p1x, p1y = vertices[0]
    for i in range(n + 1):
        p2x, p2y = vertices[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    # Check if point is on the edge boundary
                    if abs(orientation( (p1x, p1y), (p2x, p2y), (x,y) )) < EPSILON \
                       and on_segment((p1x,p1y), (x,y), (p2x,p2y)):
                        return True # Point lies on the edge

                    # Calculate intersection x-coordinate of the ray
                    if abs(p1y - p2y) > EPSILON: # Avoid division by zero for horizontal segments
                         xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x

                    if abs(p1y - p2y) < EPSILON or x < xinters - EPSILON: # Check if ray crosses edge
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


# --- NEW: Visibility Check between Vertices ---
def is_visible(vertices, idx1, idx2):
    """
    Checks if vertex idx1 can 'see' vertex idx2 within the polygon.
    Line segment ViVj must not intersect any *other* edge and must be inside.
    """
    n = len(vertices)
    p1 = vertices[idx1]
    p2 = vertices[idx2]

    # 1. Check for intersection with other edges
    for i in range(n):
        q1 = vertices[i]
        q2 = vertices[(i + 1) % n]

        # Skip edges adjacent to p1 or p2
        if i == idx1 or (i + 1) % n == idx1 or i == idx2 or (i + 1) % n == idx2:
            continue

        if do_intersect(p1, p2, q1, q2):
            # print(f"Visibility fail: Segment {idx1}-{idx2} intersects edge {i}-{i+1}")
            return False

    # 2. Check if the midpoint of the segment is inside the polygon
    #    This helps detect cases where the segment goes outside in concave areas
    #    even if it doesn't intersect other edges.
    mid_x = (p1[0] + p2[0]) / 2.0
    mid_y = (p1[1] + p2[1]) / 2.0
    if not point_in_polygon((mid_x, mid_y), vertices):
         # print(f"Visibility fail: Midpoint of {idx1}-{idx2} is outside")
         return False

    # If no intersections and midpoint is inside, they are visible
    return True

# --- NEW: Check for "Non-Star" property based on user definition ---
def is_non_star_polygon(vertices):
    """
    Checks if there is NO single vertex from which all other vertices are visible.
    Returns True if it IS a "non-star" polygon (no such vertex exists).
    Returns False if it is NOT a "non-star" polygon (at least one vertex sees all others).
    """
    n = len(vertices)
    if n < 4: return True # Triangles trivially satisfy this, no other vertex to see.

    # Iterate through each vertex as a potential viewpoint
    for i in range(n):
        can_see_all = True # Assume this vertex can see all others initially
        # Check visibility to all other vertices
        for j in range(n):
            if i == j: continue # Don't check visibility to self

            if not is_visible(vertices, i, j):
                can_see_all = False # Found one vertex it cannot see
                break # No need to check others for this viewpoint i

        # If, after checking all j, can_see_all is STILL true,
        # then we found a vertex i that sees all others. The polygon is NOT non-star.
        if can_see_all:
            # print(f"Polygon is NOT non-star: Vertex {i} sees all others.")
            return False

    # If we looped through all i and never found a vertex that sees all others,
    # then the polygon IS non-star.
    # print("Polygon IS non-star.")
    return True

# --- Polygon Generation Functions ---

def get_regular_polygon(n_sides, center=(0, 0), radius=1.0):
    """Generates vertices for a regular polygon (counter-clockwise)."""
    vertices = []
    angle_start = math.pi / 2 # Start at top
    angle_step = 2 * math.pi / n_sides
    for i in range(n_sides):
        angle = angle_start - i * angle_step # Subtract for CCW order
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        vertices.append((x, y))
    # Ensure CCW order (useful for some geometry algos, though not strictly needed here)
    signed_area = 0.5 * sum(vertices[i][0] * vertices[(i + 1) % n_sides][1] - vertices[(i + 1) % n_sides][0] * vertices[i][1] for i in range(n_sides))
    if signed_area < 0: vertices.reverse()
    return vertices


def perturb_polygon(vertices, max_perturbation):
    """Randomly perturbs the vertices of a polygon."""
    new_vertices = []
    for v in vertices:
        dx = random.uniform(-max_perturbation, max_perturbation)
        dy = random.uniform(-max_perturbation, max_perturbation)
        new_vertices.append((v[0] + dx, v[1] + dy))
    return new_vertices

def generate_irregular_polygons(n_sides, num_to_generate,
                                max_perturbation_factor=0.2,
                                initial_radius=5.0, center=(0, 0),
                                non_star_mode=True): # <-- Parameter name updated
    """
    Generates a list of valid irregular polygons.

    Args:
        n_sides (int): Number of sides for the polygons.
        num_to_generate (int): How many valid polygons to generate.
        max_perturbation_factor (float): Max perturbation relative to radius.
        initial_radius (float): Radius of the starting regular polygon.
        center (tuple): Center coordinates (x, y) for the starting polygon.
        non_star_mode (bool): If True, ensures NO vertex can see all others.

    Returns:
        list: A list where each element is a list of (x, y) vertex tuples
              representing a valid irregular polygon.
    """
    if n_sides < 3: raise ValueError("Number of sides must be at least 3.")

    valid_polygons = []
    # Increase attempts significantly for non-star mode, it's a tough constraint
    max_attempts = num_to_generate * (300 if non_star_mode else 50)

    max_perturbation = initial_radius * max_perturbation_factor
    attempts = 0

    # Perturbing the original regular polygon each time might be more robust
    # for finding diverse shapes meeting the non-star constraint.
    base_vertices = get_regular_polygon(n_sides, center, initial_radius)

    while len(valid_polygons) < num_to_generate and attempts < max_attempts:
        attempts += 1
        # Create candidate by perturbing the base regular polygon
        candidate_vertices = perturb_polygon(copy.deepcopy(base_vertices), max_perturbation)

        # --- Validation ---
        is_valid = True

        # 1. Check for self-intersection (essential)
        if is_self_intersecting(candidate_vertices):
            is_valid = False
            # print(f"Attempt {attempts}: Candidate failed self-intersection check.")

        # 2. Check for non-star property (if requested)
        if is_valid and non_star_mode:
            if not is_non_star_polygon(candidate_vertices):
                is_valid = False
                # print(f"Attempt {attempts}: Candidate failed non-star shape check (found vertex seeing all others).")

        # Optional: Add other checks like minimum area here if needed

        if is_valid:
            valid_polygons.append(candidate_vertices)
            # print(f"Generated polygon {len(valid_polygons)}/{num_to_generate}")

    if attempts >= max_attempts and len(valid_polygons) < num_to_generate:
        print(f"\nWarning: Reached max attempts ({max_attempts}). Generated {len(valid_polygons)} polygons.")
        if non_star_mode:
             print("Non-star mode is restrictive. Consider increasing max_attempts or max_perturbation_factor, or decreasing num_to_generate.")

    return valid_polygons

# --- Plotting Function ---

def plot_polygon(vertices, title="Polygon"):
    """Plots a single polygon."""
    if not vertices: return
    n = len(vertices)
    verts_to_plot = vertices + [vertices[0]]
    x, y = zip(*verts_to_plot)
    plt.figure()
    plt.plot(x, y, marker='o', linestyle='-')
    plt.fill(x, y, alpha=0.3)
    plt.title(title)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.axis('equal')
    plt.grid(True)
    plt.show()

# --- Main Execution ---

if __name__ == "__main__":
    NUM_SIDES = 6          # Example: Hexagons
    NUM_POLYGONS_TO_GENERATE = 100
    # Needs larger perturbation to create shapes where visibility is blocked
    MAX_PERTURB_FACTOR = 0.6
    INITIAL_RADIUS = 10.0
    CENTER = (0, 0)

    # Plot the starting regular polygon
    regular_poly = get_regular_polygon(NUM_SIDES, CENTER, INITIAL_RADIUS)
    plot_polygon(regular_poly, f"Starting Regular {NUM_SIDES}-gon")

    # --- Generate WITH non-star constraint (User Definition) ---
    print(f"\nGenerating {NUM_POLYGONS_TO_GENERATE} irregular {NUM_SIDES}-sided polygons (non-star mode: no vertex sees all others)...")
    irregular_polygons_nonstar = generate_irregular_polygons(
        n_sides=NUM_SIDES,
        num_to_generate=NUM_POLYGONS_TO_GENERATE,
        max_perturbation_factor=MAX_PERTURB_FACTOR,
        initial_radius=INITIAL_RADIUS,
        center=CENTER,
        non_star_mode=True # <<< Use the non-star mode
    )
    print(f"\nGenerated {len(irregular_polygons_nonstar)} valid non-star polygons.")

    # Plot the generated non-star polygons
    for i, poly_verts in enumerate(irregular_polygons_nonstar):
        plot_polygon(poly_verts, f"Irregular Polygon {i+1} ({NUM_SIDES}-sides) [Non-Star Mode]")


    # --- (Optional) Generate WITHOUT non-star constraint for comparison ---
    print(f"\nGenerating {NUM_POLYGONS_TO_GENERATE} irregular {NUM_SIDES}-sided polygons (any shape)...")
    irregular_polygons_any = generate_irregular_polygons(
        n_sides=NUM_SIDES,
        num_to_generate=NUM_POLYGONS_TO_GENERATE,
        max_perturbation_factor=MAX_PERTURB_FACTOR, # Use same factor
        initial_radius=INITIAL_RADIUS,
        center=CENTER,
        non_star_mode=False # <<< Allow any shape
    )
    print(f"\nGenerated {len(irregular_polygons_any)} valid polygons (any shape).")

    # Plot the generated polygons (any shape)
    for i, poly_verts in enumerate(irregular_polygons_any):
        plot_polygon(poly_verts, f"Irregular Polygon {i+1} ({NUM_SIDES}-sides) [Any Shape Mode]")


    print("\nDone.")