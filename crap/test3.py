import pygame
import pymunk
import pymunk.pygame_util
import math

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Initialize Pymunk Space
space = pymunk.Space()
space.gravity = (0, 981)  # Gravity similar to Earth (px/s^2)


# Helper function to create a static floor
def create_floor(space):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Segment(body, (50, HEIGHT - 50), (WIDTH - 50, HEIGHT - 50), 5)
    shape.friction = 1.0
    space.add(body, shape)


# Helper function to create a rotated square
def create_rotated_square(space, angle_degrees=30):
    body = pymunk.Body(1, pymunk.moment_for_box(1, (50, 50)))  # Mass, moment of inertia
    body.position = (WIDTH // 2, HEIGHT // 3)  # Initial position
    body.angle = math.radians(angle_degrees)  # Rotate the body by 30 degrees

    shape = pymunk.Poly.create_box(body, (50, 50))  # Create a square
    shape.friction = 0.5
    space.add(body, shape)
    return body


# Create objects
create_floor(space)
falling_square = create_rotated_square(space, angle_degrees=30)

# Initialize Pymunk's Pygame draw utility
draw_options = pymunk.pygame_util.DrawOptions(screen)

# Main game loop
running = True
while running:
    screen.fill((255, 255, 255))  # Clear screen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    space.step(1 / 60.0)  # Step the physics simulation
    space.debug_draw(draw_options)  # Draw objects

    pygame.display.flip()
    clock.tick(60)  # Limit to 60 FPS

pygame.quit()
