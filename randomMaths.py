import math

a1 = 0.0
a2 = 0.0
b1 = 2.0
b2 = 2.0
c1 = 3.0
c2 = 0.0
p1 = 0.5
p2 = 1.0

def areaOfTriangle(x1, x2, x3, y1, y2, y3):
    return 0.5*abs((x1*(y2-y3)) + (x2*(y3-y1)) + (x3*(y1-y2)))

print("Area of ABC: " +str(areaOfTriangle(a1,b1,c1,a2,b2,c2)))

def isPtInsideTriangle(ax, bx, cx, ay, by, cy, px, py):
    area_abc = areaOfTriangle(ax,bx,cx,ay,by,cy)
    area_pab = areaOfTriangle(px,ax,bx,py,ay,by)
    area_pbc = areaOfTriangle(px,bx,cx,py,by,cy)
    area_pca = areaOfTriangle(px,cx,ax,py,cy,ay)

    return area_abc == area_pab + area_pbc + area_pca

if isPtInsideTriangle(a1,b1,c1,a2,b2,c2,p1,p2):
    print("point P is INSIDE triangle ABC")
else:
    print("point P IS NOT inside triangle ABC")