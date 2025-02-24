from panda3d.core import (
    LPoint3f,
    CardMaker,
    AmbientLight,
    DirectionalLight,
    Geom,
    GeomNode,
    GeomVertexFormat,
    GeomVertexData,
    GeomVertexWriter,
    GeomTriangles,
)
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
import math
import Box2D  # The main library

# Box2D Imports
from Box2D.b2 import world, polygonShape, circleShape

# Simulation Constants
WORLD_SCALE = 10  # Scale factor between Box2D and Panda3D
TIME_STEP = 1.0 / 60
VELOCITY_ITERATIONS = 6
POSITION_ITERATIONS = 2


class SwarmSimulation(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Setup Box2D world
        self.world = world(gravity=(0, 0), doSleep=True)

        # Create ground
        ground_body = self.world.CreateStaticBody(
            position=(0, -2), shapes=polygonShape(box=(5, 0.5))
        )

        # Create an agent (Circle)
        self.agent_body = self.world.CreateDynamicBody(
            position=(0, 2),
            linearDamping=0.5,  # Smooth movement
            angularDamping=0.1,  # Prevent excessive spinning
        )
        self.agent_body.CreateFixture(
            shape=circleShape(radius=0.3), density=1.0, friction=0.3
        )

        # Panda3D visualization setup
        self.agent_node = self.create_circle(
            0.3 * WORLD_SCALE
        )  # Scale up for visibility
        self.agent_node.reparentTo(self.render)

        # Add lighting
        ambient_light = AmbientLight("ambientLight")
        ambient_light.setColor((0.5, 0.5, 0.5, 1))
        directional_light = DirectionalLight("directionalLight")
        directional_light.setDirection(LPoint3f(0, 0, -1))
        directional_light.setColor((0.7, 0.7, 0.7, 1))
        self.render.setLight(self.render.attachNewNode(ambient_light))
        self.render.setLight(self.render.attachNewNode(directional_light))

        # Set camera position
        self.camera.setPos(0, -10, 5)
        self.camera.lookAt(0, 0, 0)

        # Movement controls
        self.accept("arrow_up", self.apply_force, [(0, 10)])
        self.accept("arrow_down", self.apply_force, [(0, -10)])
        self.accept("arrow_left", self.apply_force, [(-10, 0)])
        self.accept("arrow_right", self.apply_force, [(10, 0)])

        # Simulation update task
        self.taskMgr.add(self.update, "update")

    def create_circle(self, radius):
        """Creates a simple circle visual for Panda3D"""
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData("circle", format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, "vertex")

        # Create circle vertices
        segments = 32
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            vertex.addData3(x, 0, y)

        # Create circle geometry
        tris = GeomTriangles(Geom.UHStatic)
        for i in range(1, segments - 1):
            tris.addVertices(0, i, i + 1)

        geom = Geom(vdata)
        geom.addPrimitive(tris)
        node = GeomNode("circle")
        node.addGeom(geom)
        return self.render.attachNewNode(node)

    def apply_force(self, force):
        """Apply force to the Box2D agent"""
        self.agent_body.ApplyForceToCenter(force, wake=True)

    def update(self, task):
        """Update simulation and visualization"""
        self.world.Step(TIME_STEP, VELOCITY_ITERATIONS, POSITION_ITERATIONS)

        # Update agent position in Panda3D
        pos = self.agent_body.position
        self.agent_node.setPos(LPoint3f(pos.x * WORLD_SCALE, 0, pos.y * WORLD_SCALE))

        return Task.cont


# Run the simulation
sim = SwarmSimulation()
sim.run()
