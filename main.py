import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circle vs AABB vs OBB (SAT)")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

# 색상
GRAY = (150, 150, 150)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 플레이어
player_pos = [100, 100]
player_size = (80, 60)

# 회전 오브젝트
fixed_center = [WIDTH // 2, HEIGHT // 2]
fixed_size = (80, 60)
angle = 0
rotation_speed = 0.5

speed = 5

# -------------------------
# OBB 점 계산
# -------------------------
def get_obb_points(center, size, angle_deg):
    cx, cy = center
    w, h = size
    rad = math.radians(angle_deg)

    pts = [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]
    result = []
    for x,y in pts:
        rx = x*math.cos(rad) - y*math.sin(rad)
        ry = x*math.sin(rad) + y*math.cos(rad)
        result.append((cx+rx, cy+ry))
    return result

# -------------------------
# SAT
# -------------------------
def get_axes(points):
    axes = []
    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i+1)%len(points)]
        edge = (p2[0]-p1[0], p2[1]-p1[1])
        normal = (-edge[1], edge[0])
        length = math.hypot(*normal)
        axes.append((normal[0]/length, normal[1]/length))
    return axes

def project(points, axis):
    dots = [p[0]*axis[0] + p[1]*axis[1] for p in points]
    return min(dots), max(dots)

def overlap(a, b):
    return not (a[1] < b[0] or b[1] < a[0])

def sat_collision(p1, p2):
    for axis in get_axes(p1) + get_axes(p2):
        if not overlap(project(p1, axis), project(p2, axis)):
            return False
    return True

# -------------------------
# 루프
# -------------------------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_pos[0] -= speed
    if keys[pygame.K_RIGHT]:
        player_pos[0] += speed
    if keys[pygame.K_UP]:
        player_pos[1] -= speed
    if keys[pygame.K_DOWN]:
        player_pos[1] += speed

    # 회전 속도 (Z)
    rotation_speed = 2.0 if keys[pygame.K_z] else 0.5
    angle += rotation_speed

    # 중심 계산
    player_center = (player_pos[0]+player_size[0]/2,
                     player_pos[1]+player_size[1]/2)

    # OBB
    player_obb = get_obb_points(player_center, player_size, 0)
    fixed_obb = get_obb_points(fixed_center, fixed_size, angle)

    # -------------------------
    # 1. Circle Collision
    # -------------------------
    pr = player_size[0]//2
    fr = fixed_size[0]//2

    dx = player_center[0] - fixed_center[0]
    dy = player_center[1] - fixed_center[1]
    dist = math.hypot(dx, dy)

    circle_hit = dist < (pr + fr)

    # -------------------------
    # 2. AABB Collision
    # -------------------------
    player_rect = pygame.Rect(player_pos[0], player_pos[1], *player_size)

    xs = [p[0] for p in fixed_obb]
    ys = [p[1] for p in fixed_obb]
    fixed_rect = pygame.Rect(min(xs), min(ys), max(xs)-min(xs), max(ys)-min(ys))

    aabb_hit = player_rect.colliderect(fixed_rect)

    # -------------------------
    # 3. OBB (SAT)
    # -------------------------
    obb_hit = sat_collision(player_obb, fixed_obb)

    screen.fill(WHITE)

    # -------------------------
    # 오브젝트
    # -------------------------
    pygame.draw.polygon(screen, GRAY, player_obb)
    pygame.draw.polygon(screen, GRAY, fixed_obb)

    # -------------------------
    # Circle (파랑)
    # -------------------------
    pygame.draw.circle(screen, BLUE, player_center, pr, 2)
    pygame.draw.circle(screen, BLUE, fixed_center, fr, 2)

    # -------------------------
    # AABB (빨강)
    # -------------------------
    pygame.draw.rect(screen, RED, player_rect, 2)
    pygame.draw.rect(screen, RED, fixed_rect, 2)

    # -------------------------
    # OBB (초록)
    # -------------------------
    pygame.draw.polygon(screen, GREEN, player_obb, 2)
    pygame.draw.polygon(screen, GREEN, fixed_obb, 2)

    # -------------------------
    # 텍스트 UI
    # -------------------------
    circle_text = f"Circle: {'HIT' if circle_hit else 'NO'}"
    aabb_text   = f"AABB: {'HIT' if aabb_hit else 'NO'}"
    obb_text    = f"OBB: {'HIT' if obb_hit else 'NO'}"

    screen.blit(font.render(circle_text, True, BLUE), (10, 10))
    screen.blit(font.render(aabb_text, True, RED), (10, 35))
    screen.blit(font.render(obb_text, True, GREEN), (10, 60))

    pygame.display.flip()
    clock.tick(60)