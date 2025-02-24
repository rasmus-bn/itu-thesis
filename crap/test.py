import pygame
import pymunk

# Initialize Pygame and Pymunk
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
SPACE = pymunk.Space()
SPACE.gravity = (0, 1000)  # Set gravity

# Create a Ball

balls = []

BALL_RADIUS = 20

# ball 1
ball_body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, BALL_RADIUS))
ball_body.position = (400, 100)
ball_shape = pymunk.Circle(ball_body, BALL_RADIUS)
balls.append({"body": ball_body, "shape": ball_shape})

# ball 2
ball_body = pymunk.Body(0.5, pymunk.moment_for_circle(0.5, 0, BALL_RADIUS))
ball_body.position = (400, 400)
ball_shape = pymunk.Circle(ball_body, BALL_RADIUS)
balls.append({"body": ball_body, "shape": ball_shape})

for ball in balls:
    SPACE.add(ball["body"], ball["shape"])

# Main Loop
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Apply an upward force to ball 2
    balls[1]["body"].apply_force_at_local_point((0, -500), (0, 0))

    # Physics Step
    SPACE.step(1 / 60.0)

    # Draw Everything
    WINDOW.fill((0, 0, 0))

    for ball in balls:
        pygame.draw.circle(
            WINDOW,
            (0, 255, 0),
            (int(ball["body"].position.x), int(ball["body"].position.y)),
            BALL_RADIUS,
        )

    pygame.display.update()
    CLOCK.tick(60)

pygame.quit()
