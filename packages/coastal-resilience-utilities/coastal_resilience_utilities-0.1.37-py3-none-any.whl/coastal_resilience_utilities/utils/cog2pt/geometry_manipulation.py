import numpy as np

def generate_squircle(X, Y, r, shrink=0.9, num_points=100):
    """
    Generate points of a squircle polygon with a specific border-radius.

    Parameters:
    r (float): Border-radius of the squircle.
    num_points (int): Number of points to generate for the polygon.

    Returns:
    List of tuples: Points of the squircle polygon.
    """
    theta = np.linspace(0, 2 * np.pi, num_points)
    points = []
    r = r * shrink * 0.5

    for angle in theta:
        x = r * np.sign(np.cos(angle)) * np.abs(np.cos(angle))**0.5 + X
        y = r * np.sign(np.sin(angle)) * np.abs(np.sin(angle))**0.5 + Y
        points.append((x, y))

    points.append(points[0])
    return [points]


def generate_beveled_square(X, Y, r, shrink=0.9, bevel_shrink=0.7):
    """
    Generate points of a squircle polygon with a specific border-radius.

    Parameters:
    r (float): Border-radius of the squircle.
    num_points (int): Number of points to generate for the polygon.

    Returns:
    List of tuples: Points of the squircle polygon.
    """
    return [[
        [X - (r * shrink)/2., Y + (r * bevel_shrink)/2.], # Top Left
        [X - (r * bevel_shrink)/2., Y + (r * shrink)/2.],
        [X + (r * bevel_shrink)/2., Y + (r * shrink)/2.], # Top Right
        [X + (r * shrink)/2., Y + (r * bevel_shrink)/2.], 
        [X + (r * shrink)/2., Y - (r * bevel_shrink)/2.], # Bottom Right
        [X + (r * bevel_shrink)/2., Y - (r * shrink)/2.], 
        [X - (r * bevel_shrink)/2., Y - (r * shrink)/2.], 
        [X - (r * shrink)/2., Y - (r * bevel_shrink)/2.], 
        [X - (r * shrink)/2., Y + (r * bevel_shrink)/2.]
    ]]
    
    
def generate_square(X, Y, r, shrink=0.95):
    return [[
        [X - r/2.*shrink, Y + r/2.*shrink],
        [X + r/2.*shrink, Y + r/2.*shrink],
        [X + r/2.*shrink, Y - r/2.*shrink],
        [X - r/2.*shrink, Y - r/2.*shrink],
        [X - r/2.*shrink, Y + r/2.*shrink]
    ]]