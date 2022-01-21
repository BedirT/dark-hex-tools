def onSegment(p:tuple, q:tuple, r:tuple) -> bool:
     
    if ((q[0] <= max(p[0], r[0])) &
        (q[0] >= min(p[0], r[0])) &
        (q[1] <= max(p[1], r[1])) &
        (q[1] >= min(p[1], r[1]))):
        return True
         
    return False

def orientation(p:tuple, q:tuple, r:tuple) -> int:
     
    val = (((q[1] - p[1]) *
            (r[0] - q[0])) -
           ((q[0] - p[0]) *
            (r[1] - q[1])))
            
    if val == 0:
        return 0
    if val > 0:
        return 1 # Collinear
    else:
        return 2 # Clock or counterclock
 
def doIntersect(p1, q1, p2, q2):
     
    # Find the four orientations needed for 
    # general and special cases
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)
 
    # General case
    if (o1 != o2) and (o3 != o4):
        return True
     
    # Special Cases
    if  ((o1 == 0) and (onSegment(p1, p2, q1))) or \
        ((o2 == 0) and (onSegment(p1, q2, q1))) or \
        ((o3 == 0) and (onSegment(p2, p1, q2))) or \
        ((o4 == 0) and (onSegment(p2, q1, q2))):
        return True
    return False
 
# Returns true if the point p lies 
# inside the polygon[] with n vertices
def is_inside_polygon(points:list, p:tuple) -> bool:
    n = len(points)
    if n < 3:
        return False
    extreme = (10000, p[1])
    count = i = 0
     
    while True:
        next = (i + 1) % n
         
        if (doIntersect(points[i],
                        points[next],
                        p, extreme)):
            if orientation(points[i], p,
                           points[next]) == 0:
                return onSegment(points[i], p,
                                 points[next])
                                  
            count += 1
             
        i = next
         
        if (i == 0):
            break
         
    # Return true if count is odd, false otherwise
    return (count % 2 == 1)

def is_inside_rectangle(x, y, w, h, p):
    if (p[0] >= x) and (p[0] <= x + w) and (p[1] >= y) and (p[1] <= y + h):
        return True
    return False