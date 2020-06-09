import pygame
import neat
import time
import os
import random   # For randomly placing the height of the tubes

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


def draw_window(win, bird):
    win.blit(BG_IMG, (0,0))
    bird.draw(win)
    pygame.display.update()


def main():
    # Initialize bird object with starting position
    bird = Bird(200, 200)
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

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

        # call move
        bird.move()

        # call draw_window to create one
        draw_window(win, bird)

    pygame.quit()
    quit()


main()



