import pygame
import pymunk
import pymunk.pygame_util
import random


def create_cube(space):
    mass = 1
    size = 40
    moment = pymunk.moment_for_box(mass, (size, size))
    body = pymunk.Body(mass, moment, body_type=pymunk.Body.DYNAMIC)
    body.position = (400, 300)
    shape = pymunk.Poly.create_box(body, (size, size))
    shape.friction = 1.0  # Increase friction to simulate ground friction
    body.velocity_func = (
        pymunk.Body.update_velocity
    )  # Ensure default velocity update function is used
    body.linear_damping = 0.9  # Set linear damping to a reasonable value
    body.angular_damping = 0.9  # Set angular damping to slow down rotation
    space.add(body, shape)
    return body


def create_crate(space, position):
    mass = 2
    size = 40
    moment = pymunk.moment_for_box(mass, (size, size))
    body = pymunk.Body(mass, moment, body_type=pymunk.Body.DYNAMIC)
    body.position = position
    shape = pymunk.Poly.create_box(body, (size, size))
    shape.friction = 1.0  # Friction to simulate ground friction
    space.add(body, shape)
    return body


def apply_force(body):
    force = pymunk.Vec2d(2000, 0).rotated(
        body.angle
    )  # Apply force in the direction the cube is facing
    body.apply_force_at_world_point(
        force, body.position
    )  # Apply force in world coordinates


def draw_direction(screen, body):
    start_pos = (int(body.position.x), int(body.position.y))
    end_pos = (
        int(body.position.x + 30 * body.rotation_vector.x),
        int(body.position.y + 30 * body.rotation_vector.y),
    )
    pygame.draw.line(screen, (255, 0, 0), start_pos, end_pos, 3)


def draw_crates(screen, crates):
    for crate in crates:
        pos = crate.position
        size = 20
        angle = crate.angle
        points = [
            (
                pos.x + size * pymunk.Vec2d(1, 1).rotated(angle).x,
                pos.y + size * pymunk.Vec2d(1, 1).rotated(angle).y,
            ),
            (
                pos.x + size * pymunk.Vec2d(1, -1).rotated(angle).x,
                pos.y + size * pymunk.Vec2d(1, -1).rotated(angle).y,
            ),
            (
                pos.x + size * pymunk.Vec2d(-1, -1).rotated(angle).x,
                pos.y + size * pymunk.Vec2d(-1, -1).rotated(angle).y,
            ),
            (
                pos.x + size * pymunk.Vec2d(-1, 1).rotated(angle).x,
                pos.y + size * pymunk.Vec2d(-1, 1).rotated(angle).y,
            ),
        ]
        pygame.draw.polygon(screen, (139, 69, 19), points)


def point_to_cursor(body, mouse_pos):
    direction = pymunk.Vec2d(
        mouse_pos[0] - body.position.x, mouse_pos[1] - body.position.y
    )
    body.angle = direction.angle  # Update body's angle to point towards cursor


def draw_cube(screen, body):
    pos = body.position
    size = 20
    angle = body.angle
    points = [
        (
            pos.x + size * pymunk.Vec2d(1, 1).rotated(angle).x,
            pos.y + size * pymunk.Vec2d(1, 1).rotated(angle).y,
        ),
        (
            pos.x + size * pymunk.Vec2d(1, -1).rotated(angle).x,
            pos.y + size * pymunk.Vec2d(1, -1).rotated(angle).y,
        ),
        (
            pos.x + size * pymunk.Vec2d(-1, -1).rotated(angle).x,
            pos.y + size * pymunk.Vec2d(-1, -1).rotated(angle).y,
        ),
        (
            pos.x + size * pymunk.Vec2d(-1, 1).rotated(angle).x,
            pos.y + size * pymunk.Vec2d(-1, 1).rotated(angle).y,
        ),
    ]
    pygame.draw.polygon(screen, (0, 0, 255), points)  # Change color to blue


def stick_crate_to_player(arbiter, space, data):
    player_shape, crate_shape = arbiter.shapes
    if player_shape.body == data["player_body"]:
        joint = pymunk.PivotJoint(
            player_shape.body, crate_shape.body, crate_shape.body.position
        )
        space.add(joint)
    return True


def apply_random_force(crate):
    amount = 1000
    force = pymunk.Vec2d(
        random.uniform(-amount, amount), random.uniform(-amount, amount)
    )
    crate.apply_force_at_world_point(force, crate.position)


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    space = pymunk.Space()
    space.gravity = (0, 0)  # No gravity for top-down
    space.damping = 0.4  # Global damping to slow down all bodies

    cube_body = create_cube(space)
    crates = [
        create_crate(space, (random.randint(100, 700), random.randint(100, 500)))
        for _ in range(5)
    ]

    handler = space.add_collision_handler(0, 0)
    handler.data["player_body"] = cube_body
    handler.post_solve = stick_crate_to_player

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        point_to_cursor(cube_body, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            apply_force(cube_body)  # Apply force in the current direction

        for crate in crates:
            apply_random_force(crate)  # Apply random force to each crate

        screen.fill((0, 0, 0))
        space.step(1 / 60.0)
        draw_cube(screen, cube_body)
        draw_direction(screen, cube_body)
        draw_crates(screen, crates)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
