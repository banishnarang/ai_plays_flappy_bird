import pygame
import neat
import time
import os
import random   # For randomly placing the height of the tubes
import pickle
pygame.font.init()

# Set up window size
WIN_WIDTH = 500
WIN_HEIGHT = 800

# Generation count
gen = 0

# Load Images (scale2x to increase size 2 times)
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'bird1.png'))),
             pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'bird2.png'))),
             pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'bird3.png')))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'pipe.png')))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'base.png')))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('images', 'bg.png')))

STAT_FONT = pygame.font.SysFont('comicsans', 50)
END_FONT = pygame.font.SysFont('comicsans', 70)
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

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
    """
    represents a pipe object
    """
    GAP = 200

    # The bird doesn't move but all the other objects in the environment do, therefore, we need velocity
    VEL = 5

    def __init__(self, x):
        """
        initialize pipe object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)    # For pipes going from top to bottom, we flip
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False    # If the bird has already passed across the pipe
        self.set_height()

    def set_height(self):
        """
        set the height of the pipe, from the top of the screen
        :return: None
        """
        # Get a random number for where the top of our pipe should be
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        move pipe based on vel
        :return: None
        """
        # Move pipe to the left based on velocity
        self.x -= self.VEL

    def draw(self, win):
        """
       draw both the top and bottom of the pipe
       :param win: pygame window/surface
       :return: None
       """
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
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
    """
    Represnts the moving floor of the game
    """
    VEL = 5    # Same as pipe
    WIDTH = BASE_IMG.get_width()    # How wide one of these image are
    IMG = BASE_IMG

    def __init__(self, y):
        """
       Initialize the object
       :param y: int
       :return: None
       """
        # Since the x is going to be moving to the left, so we don't need to define that
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        move floor so it looks like its scrolling
        :return: None
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # Cycle images repeatedly to keep consistent flow of movement
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
       Draw the floor. This is two images that move together.
       :param win: the pygame surface/window
       :return: None
       """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    """
   draws the windows for the main game loop
   :param win: pygame window surface
   :param bird: a Bird object
   :param pipes: List of pipes
   :param score: score of the game (int)
   :param gen: current generation
   :param pipe_ind: index of closest pipe
   :return: None
   """
    win.blit(BG_IMG, (0,0))

    # Draw all pipes
    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render('Score: ' + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render('Gen: ' + str(gen), 1, (255, 255, 255))
    win.blit(text, (10, 10))

    # Draw base
    base.draw(win)

    # Draw bird
    for bird in birds:
        # draw lines from bird to pipe
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255, 0, 0),
                                 (bird.x + bird.img.get_width() / 2, bird.y + bird.img.get_height() / 2),
                                 (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width() / 2, pipes[pipe_ind].height),
                                 5)
                pygame.draw.line(win, (255, 0, 0),
                                 (bird.x + bird.img.get_width() / 2, bird.y + bird.img.get_height() / 2), (
                                 pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width() / 2,
                                 pipes[pipe_ind].bottom), 5)
            except:
                pass
        # draw bird
        bird.draw(win)

    pygame.display.update()


def main(genomes, config):
    """
   runs the simulation of the current population of
   birds and sets their fitness based on the distance they
   reach in the game.
   """
    global gen, WIN
    win = WIN
    gen += 1

    nets = []   # To keep track of NN
    ge = []    # To keep track of genome
    birds = []

    for _, g in genomes:
        # Setting up a NN for our genome
        net = neat.nn.FeedForwardNetwork.create(g, config)
        
        # Append it to the list
        nets.append(net)
        
        # Append a bird object as well
        birds.append(Bird(230, 350))
        
        # Set the initial fitness to 0
        g.fitness = 0
        
        # Append the actual genome to the list in the same position as the bird object
        ge.append(g)

    # Initialize bird, base, and pipe object with starting position
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

                # Quit
                pygame.quit()
                quit()

        # Setting the pipe index to be 0
        pipe_ind = 0
        if len(birds) > 0:
            # Since there will be 2 pipes on the screen at a time, we check which pipe is passed and set the index
            # to the one that is yet to be passed by incrementing the index to the next one.
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1

        # if no birds left
        else:
            # quit the generation
            run = False
            break

        # Move the birds based on NN
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1    # encourages bird to stay alive by enhancing the fitness by 0.1 every 30s it's alive

            # activate a NN with our input
            # inputs are y pos of bird, distance between bird and top pipe, distance between bird and bottom pipe
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height),
                                       abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                bird.jump()

        rem = []    # Pipes to remove list
        add_pipe = False
        # Move pipes
        for pipe in pipes:
            for x, bird in enumerate(birds):
                # Check for collision with the pipes
                if pipe.collide(bird):
                    # decrease the fitness by 1 on collision
                    ge[x].fitness -= 1

                    # remove the bird, net and genome
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                # Check if bird has passed the pipe, set add_pipe flag to be true
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            # Check the position of the pipe, if the pipe is completely off the screen, we remove the pipe
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)  # Append to this list, equivalent to removing it

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                # Increase the fitness by 5 when it passes each pipe
                g.fitness += 5
            pipes.append(Pipe(600))

        # Remove the pipe that went off the screen
        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            # Check if bird has hit the ground or the top
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                # Remove it from the list
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        # Move base
        base.move()

        # call draw_window to create one
        draw_window(WIN, birds, pipes, base, score, gen-1, pipe_ind)

        # break if score gets large enough
        '''
        if score > 20:
            pickle.dump(nets[0], open('best.pickle', 'wb'))
            break
        '''


def run(config_path):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    # Define all sub headings used in the config file
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    # Create a population based on config
    p = neat.Population(config)

    # Add Stats reporter to our program, to get detailed statistics
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Set the fitness function that we are going to run for 50 generations
    winner = p.run(main, 50)

    # Show final stats
    print('\nBest Genome: \n{!s}'.format(winner))




if __name__=="__main__":
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.

    # Path to directory we are currently in
    local_dir = os.path.dirname(__file__)

    # Join the local directory to name of the configuration file
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)


