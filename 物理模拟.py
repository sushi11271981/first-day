import math
import random
from typing import List, Tuple

import pygame


class Particle:
    """A simple particle affected by gravity, wall collisions, and neighbor repulsion."""

    def __init__(self, position: pygame.math.Vector2, radius: float, color: Tuple[int, int, int]):
        self.position = pygame.math.Vector2(position)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.radius = radius
        self.color = color

    def apply_gravity(self, gravity: float) -> None:
        """Apply gravity to the particle by increasing its vertical acceleration."""
        self.acceleration.y += gravity

    def apply_repulsion(self, neighbors: List["Particle"], repulsion_strength: float, threshold: float) -> None:
        """Apply a simple repulsion force so particles do not overlap."""
        for other in neighbors:
            if other is self:
                continue
            offset = self.position - other.position
            distance = offset.length() or 1.0
            min_distance = self.radius + other.radius
            if distance < min_distance * threshold:
                direction = offset.normalize()
                force = (min_distance * threshold - distance) * repulsion_strength
                # We directly modify velocity to keep the update simple (Euler integration).
                self.velocity += direction * force

    def update(self, damping: float) -> None:
        """Integrate acceleration and velocity (Euler integration)."""
        self.velocity += self.acceleration
        self.position += self.velocity
        self.velocity *= damping
        self.acceleration.update(0, 0)

    def bounce_within(self, polygon: List[pygame.math.Vector2], restitution: float, floor_y: float) -> None:
        """Bounce against polygonal container walls and stop at the bottom of the screen."""
        # Simple axis-aligned bounding box derived from polygon to quickly detect escapes.
        xs = [p.x for p in polygon]
        ys = [p.y for p in polygon]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # Screen bottom collision.
        if self.position.y + self.radius > floor_y:
            self.position.y = floor_y - self.radius
            self.velocity.y = -self.velocity.y * restitution

        # Vertical walls (approximation using bounding box, fine for convex cup geometry).
        if self.position.x - self.radius < min_x:
            self.position.x = min_x + self.radius
            self.velocity.x = -self.velocity.x * restitution
        if self.position.x + self.radius > max_x:
            self.position.x = max_x - self.radius
            self.velocity.x = -self.velocity.x * restitution

        # Top boundary ensures particles enter the cup rather than escape upward.
        if self.position.y - self.radius < min_y:
            self.position.y = min_y + self.radius
            self.velocity.y = -self.velocity.y * restitution

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, self.color, self.position, int(self.radius))


class Flask:
    """A simple rotating rectangular container representing a flask."""

    def __init__(self, center: Tuple[float, float], width: float, height: float, color: Tuple[int, int, int]):
        self.center = pygame.math.Vector2(center)
        self.width = width
        self.height = height
        self.color = color
        self.angle = 0.0
        self.max_angle = math.radians(135)
        self.rotation_speed = math.radians(0.5)

    def update(self) -> None:
        """Slowly rotate the flask until it reaches the target angle."""
        if self.angle < self.max_angle:
            self.angle = min(self.angle + self.rotation_speed, self.max_angle)

    def get_corners(self) -> List[pygame.math.Vector2]:
        """Return the four transformed corners of the flask."""
        half_w = self.width / 2
        half_h = self.height / 2
        corners = [
            pygame.math.Vector2(-half_w, -half_h),
            pygame.math.Vector2(half_w, -half_h),
            pygame.math.Vector2(half_w, half_h),
            pygame.math.Vector2(-half_w, half_h),
        ]
        rotation = pygame.math.Vector2(1, 0).rotate_rad(self.angle)
        sin_a = rotation.y
        cos_a = rotation.x
        transformed = []
        for corner in corners:
            # Rotate around the flask center using a rotation matrix.
            x = corner.x * cos_a - corner.y * sin_a
            y = corner.x * sin_a + corner.y * cos_a
            transformed.append(pygame.math.Vector2(x, y) + self.center)
        return transformed

    def draw(self, surface: pygame.Surface) -> None:
        corners = self.get_corners()
        pygame.draw.polygon(surface, self.color, corners, width=3)


class Simulation:
    """Manage particles and flask, creating an animation of fluid-like motion."""

    def __init__(self, particle_count: int = 120):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Simple Fluid Simulation")
        self.clock = pygame.time.Clock()

        self.background_color = (20, 20, 20)
        self.particle_color = (120, 180, 255)
        self.flask_color = (200, 200, 200)

        self.flask = Flask(center=(400, 350), width=200, height=300, color=self.flask_color)

        self.particles: List[Particle] = []
        self.create_particles(particle_count)

        self.gravity = 0.5
        self.damping = 0.99
        self.restitution = 0.7
        self.repulsion_strength = 0.05
        self.repulsion_threshold = 1.2
        self.floor_y = 580

    def create_particles(self, count: int) -> None:
        """Generate particles above the flask so they fall into it."""
        for _ in range(count):
            x = random.uniform(self.flask.center.x - 50, self.flask.center.x + 50)
            y = random.uniform(self.flask.center.y - self.flask.height / 2 - 100, self.flask.center.y - self.flask.height / 2 - 20)
            radius = random.uniform(4, 6)
            particle = Particle(position=pygame.math.Vector2(x, y), radius=radius, color=self.particle_color)
            self.particles.append(particle)

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def update(self) -> None:
        corners = self.flask.get_corners()
        for particle in self.particles:
            particle.apply_gravity(self.gravity)
            particle.apply_repulsion(self.particles, self.repulsion_strength, self.repulsion_threshold)
            particle.update(self.damping)
            particle.bounce_within(corners, self.restitution, self.floor_y)
        self.flask.update()

    def draw(self) -> None:
        self.screen.fill(self.background_color)
        # Draw container first so particles appear inside it.
        self.flask.draw(self.screen)
        for particle in self.particles:
            particle.draw(self.screen)
        pygame.display.flip()

    def run(self) -> None:
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)


def main() -> None:
    simulation = Simulation(particle_count=150)
    simulation.run()


if __name__ == "__main__":
    main()
