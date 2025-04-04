import pymunk

# Create a space
space = pymunk.Space()

# Create a 2x2 box
mass = 1.0
width, height = 2, 2
moment = pymunk.moment_for_box(mass, (width, height))
body = pymunk.Body()
shape = pymunk.Poly.create_box(body, (width, height))
shape.density = 1.0

# Add the body and shape to the space
space.add(body, shape)

# # Run a single timestep
# dt = 0.01  # Time step duration
# space.step(dt)

# Print the mass of the box
print("Mass of the box:", body.mass)