import pygame
import neat
import time
import os
import random   # For randomly placing the height of the tubes
pygame.font.init()

# Set up window size
WIN_WIDTH = 500
WIN_HEIGHT = 800

# Load Images (scale2x to increase size 2 times)
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'bird1.png'))),
             pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'bird2.png'))),
             pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'bird3.png')))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'pipe.png')))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'base.png')))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'bg.png')))

STAT_FONT = pygame.font.SysFont('comicsans', 50)

# Represents the bird object moving - Bird Class
class Bird:
    """
    Bird class representing the flappy bird
    """
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25   # How much the bird will tilt
    ROT_VEL = 20    # How much will the bird rotate on each frame or every time that we move the bird
    ANIMATION_TIME = 5  # How long we will show each bird animation - decides faster or slower the bird is

    def __init__(self, x, y):
        """
        Initialize the object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """
        self.x = x  # x position
        self.y = y  # y position
        self.tilt = 0   # How much the image is actually titled so we know how to draw it on screen
        self.tick_count = 0    # Figure out the physics of the bird when it moves and jumps
        self.vel = 0    # Velocity, 0 initially
        self.height = self.y
        self.img_count = 0    # Keep track of which image of bird are we using
        self.img = self.IMGS[0]    # Reference bird images list - bird1.png

    def jump(self):
        """
        make the bird jump
        :return: None
        """
        # Negative velocity because (0,0) is the top left of the screen in pygame, and therefore
        # we need neg vel for upward movement and vice versa for downwards, right is pos and left is neg
        self.vel = -10.5
        self.tick_count = 0    # 0 because we need to know when we need to be changing directions and velocity (physics)
        self.height = self.y

    def move(self):
        """
        make the bird move
        :return: None
        """
        self.tick_count += 1    # A frame went by, so keeping track of how many times we move since last jump

        # Displacement = how many pixels we moved up or down this frame
        # Tells us based on current vel how much we are moving up or down, tick_count represents time since last jump
        # Tick count resets every jump
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2

        # Fail safe - make sure we don't have velocity moving way too up or way too down
        if d >= 16:
            d = 16

        # If we are moving upwards, let's move up a little bit more. Makes the bird jump nicely
        if d < 0:
            d -= 2

        # Add movement to bird vertical position
        self.y = self.y + d

        # tilting the bird upward
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION

        # tilting the bird downward
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        """
        draw the bird
        :param win: pygame window or surface
        :return: None
        """
        # win = window that we are drawing the bird onto
        self.img_count += 1

        # Checking what image we should show, based on the current image count
        # # This we we get the winds flapping up and flapping down without looking like it's skipping the frame
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # When the bird is tilted 90 degrees going downward, we don't want it to be flapping it's wings
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        # We need to rotate the image around the center based on it's current tilt
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        """
        gets the mask for the current image of the bird
        :return: None
        """
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200

    # The bird doesn't move but all the other objects in the environment do, therefore, we need velocity
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)    # For pipes going from top to bottom, we flip
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False    # If the bird has already passed across the pipe
        self.set_height()

    def set_height(self):
        # Get a random number for where the top of our pipe should be
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        # Move pipe to the left based on velocity
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()

        # Create a mask for the top and bottom pipe
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        # Calculate offset: how far along are the masks from each other
        top_offset = (self.x - bird.x, self.top - round(bird.y))    # Offset from the bird to top mask
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))    # Offset from the bird to bottom mask

        # Point of collision, first point of overlap
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False


class Base:
    VEL = 5    # Same as pipe
    WIDTH = BASE_IMG.get_width()    # How wide one of these image are
    IMG = BASE_IMG

    def __init__(self, y):
        # Since the x is going to be moving to the left, so we don't need to define that
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # Cycle images repeatedly to keep consistent flow of movement
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, bird, pipes, base, score):
    win.blit(BG_IMG, (0,0))

    # Draw all pipes
    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render('Score: ' + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    # Draw base
    base.draw(win)

    # Draw bird
    bird.draw(win)

    pygame.display.update()


def main():
    # Initialize bird, base, and pipe object with starting position
    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    score = 0  # player score

    # Create clock object to set consistent frame rate
    clock = pygame.time.Clock()

    run = True

    # Main game loop
    while run:
        # At most 30 ticks every seconds
        clock.tick(30)

        # Basic pygame event loop, keeps track of whenever something happens, user clicks mouse etc.
        for event in pygame.event.get():
            # if user clicks the cross ui
            if event.type == pygame.QUIT:
                # loop breaks
                run = False

        rem = []    # Pipes to remove list
        add_pipe = False
        # Move pipes
        for pipe in pipes:
            # Check for collision with the pipes
            if pipe.collide(bird):
                pass

            # Check the position of the pipe, if the pipe is completely off the screen, we remove the pipe
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)    # Append to this list, equivalent to removing it

            # Check if bird has passed the pipe, set add_pipe flag to be true
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))

        # Remove the pipe that went off the screen
        for r in rem:
            pipes.remove(r)

        # Check if bird has hit the ground
        if bird.y + bird.img.get_height() >= 750:
            pass

        # Move base
        base.move()

        # call draw_window to create one
        draw_window(win, bird, pipes, base, score)

    pygame.quit()
    quit()


main()



