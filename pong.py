"""
A simple pong game implemented using pygame.
Player 1 uses the w and s keys to move their paddle up and down.
Player 2 uses interacts via a socket connection to move their paddle up and down.
The ball bounces off the top and bottom of the screen and the paddles.
If the ball hits the end of the screen, the other player gets a point.
Paddle 1 is blue and paddle 2 is red.
Paddle 1 is on the left side of the screen and paddle 2 is on the right side.
The ball is green.
The paddle is implemented using a rectangle in class Paddle.
The ball is implemented using a circle in class Ball.
The game logic is implemented in class Pong.
The ball starts in the middle of the screen with a random y position and a random velocity direction
"""

import pygame
import sys
import random
import socket

class Colours:
    """
    A class to store the colours used in the game.
    """
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    PINK = (255, 0, 255)
    GREY = (128, 128, 128)
    LIGHT_GREY = (192, 192, 192)
    PURPLE = (128, 0, 128)


class Score:
    """
    Keeps track of the score for both players.
    Displays score on top left portion of game screen
    Text is rendered in white
    When one player looses the score is reset
    """
    def __init__(self, screen):
        """
        Initialises the score.
        """
        self.screen = screen
        self.score1 = 0
        self.score2 = 0
        self.font = pygame.font.SysFont("monospace", 20)

    def render(self, score1 = 0, score2= 0):
        """
        Renders the score on the screen.
        """
        self.text1 = self.font.render("Player 1 Score: " + str(self.score1), True, Colours.WHITE)
        self.text2 = self.font.render("Player 2 Score: " + str(self.score2), True, Colours.WHITE)
        self.screen.blit(self.text1, (10, 10))
        self.screen.blit(self.text2, (10, 30))

    def reset(self):
        """
        Resets the score to 0.
        """
        self.score1 = 0
        self.score2 = 0
        self.render()

    def update(self, player):
        """
        Updates the score.
        """
        if player == 1:
            self.score1 += 1
        else:
            self.score2 += 1
        self.render()

    def get_score(self, player):
        """
        Returns the score of the specified player.
        """
        if player == 1:
            return self.score1
        else:
            return self.score2

class Paddle:
    """
    A class to represent a paddle.
    The paddle can move up and down vertically, but not off the screen.
    The paddle has a width of 20 and a height of 100.
    """
    def __init__(self, screen, x, y, colour):
        """
        Initialises the paddle.
        """
        self.screen = screen
        self.x = x
        self.y = y
        self.colour = colour
        self.width = Pong.PADDLE_WIDTH
        self.height = Pong.PADDLE_HEIGHT
        self.velocity = 0
        self.acceleration = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def render(self):
        """
        Renders the paddle on the screen.
        """
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.screen, self.colour, self.rect)

    def move(self):
        """
        Moves the paddle vertically at velocity
        If the paddle moves off the screen, it is put back on the screen.
        """
        self.velocity += self.acceleration
        self.y += self.velocity
        if self.y < 0:
            self.y = 0
        elif self.y + self.height > self.screen.get_height():
            self.y = self.screen.get_height() - self.height
        self.render()
    def move_up(self):
        """
        Moves the paddle up.
        """
        self.acceleration = -1

    def move_down(self):
        """
        Moves the paddle down.
        """
        self.acceleration = 1

    def stop(self):
        """
        Stops the paddle.
        """
        self.acceleration = 0

    def get_rect(self):
        """
        Returns the rectangle of the paddle.
        """
        return self.rect

    def get_paddle_bottom(self):
        """
        Returns the bottom of the paddle.
        """
        return self.y + self.height
    
    def get_paddle_top(self):
        """
        Returns the top of the paddle.
        """
        return self.y

    def get_paddle_right(self):
        """
        Returns the right of the paddle.
        """
        return self.x + self.width

    def get_paddle_left(self):
        """
        Returns the left of the paddle.
        """
        return self.x

    def reset(self):
        """
        Resets the paddle in the middle of the screen
        """
        self.y = self.screen.get_height() / 2 - self.height / 2
        self.velocity = 0
        self.acceleration = 0
        self.render()
 


class Ball:
    """
    Green ball which moves around the game and bounces off the top and bottom of the screen and other paddles.
    If the ball goes off the right side of the screen without hitting paddle2, player1 gets a point.
    If the ball goes off the left side of the screen without hitting paddle1, player2 gets a point.
    The ball is reset to the middle of the screen with a random y position and a random velocity direction.
    """
    def __init__(self, screen: pygame.Surface, x: int, y: int, radius: int, colour: tuple):
        """
        Initializes the ball.
        """
        self.screen = screen
        self.x = x
        self.y = y
        self.spin = 0 # spin is the angle of the ball, causes ball to curve
        self.radius = radius
        self.colour = colour
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        self.reset()
        self.font = pygame.font.SysFont("monospace", 20)

    def render(self):
        """
        Renders the ball on the screen.
        """
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        pygame.draw.circle(self.screen, self.colour, (self.x, self.y), self.radius)

    def bounce_paddle(self, paddle1: Paddle, paddle2 : Paddle, score: Score):
        """
        Bounces the ball off the paddles.
        If the ball misses paddle1, player two's score is updated
        If the ball misses paddle2, player one's score is updated
        """
        if self.x - self.radius < paddle1.get_paddle_right():
            if self.y > paddle1.get_paddle_top() and self.y < paddle1.get_paddle_bottom():
                self.velocity_x *= -1.1 # Speed up ball a little bit to make it harder
                self.velocity_y += paddle1.velocity / 2 # Add some velocity to the ball to make it harder
                self.spin = paddle1.velocity / 1000 # Add some spin to the ball to make it harder
                #Make a sound effect for bouncing off paddle
                pygame.mixer.Sound.play(pygame.mixer.Sound("/Users/samuelbarrett/Desktop/bounce.wav"))
            else:
                score.update(2) # player 2 gets a point
                self.display_point_lost_message(2, score)
                self.reset()
                paddle1.reset()
                paddle2.reset()
        if self.x + self.radius > paddle2.get_paddle_left():
            if self.y > paddle2.get_paddle_top() and self.y < paddle2.get_paddle_bottom():
                self.velocity_x *= -1.04 # Speed up ball a little bit
                self.velocity_y += paddle2.velocity / 2 # Add some velocity to the ball to make it harder
                self.spin = paddle2.velocity/100 # Make the ball spin a little bit
                # Make a sound effect for bouncing off paddle
                pygame.mixer.Sound.play(pygame.mixer.Sound("/Users/samuelbarrett/Desktop/bounce.wav"))
            else:
                score.update(1) # player 1 gets a point
                self.display_point_lost_message(1, score)
                self.reset()
                paddle1.reset()
                paddle2.reset()

    def display_point_lost_message(self, player_id: int, score: Score):
        """
        Fill screen black and display a message to the player that they won a point.
        Ask the user to continue playing by pressing the y key or ESC to exit
        Prompt the user for the y key "Press y to continue" in a separate text box
        Display an encouraging message to the user
        """
        self.screen.fill(Colours.PURPLE)
        if player_id == 1:
            self.text = self.font.render("Player 2 won a point", True, Colours.WHITE)
        else:
            self.text = self.font.render("Player 1 won a point", True, Colours.WHITE)
        self.screen.blit(self.text, (self.screen.get_width() / 2 - self.text.get_width() / 2, self.screen.get_height() / 2 - self.text.get_height() / 2))
        self.text = self.font.render("Press y to continue", True, Colours.WHITE)
        self.screen.blit(self.text, (self.screen.get_width() / 2 - self.text.get_width() / 2, self.screen.get_height() / 2 + self.text.get_height() / 2))
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        self.reset()
                        return
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()


    def bounce_top(self):
        """
        Bounces the ball off the top of the screen.
        """
        if self.y < self.radius:
            self.velocity_y *= -1
            self.spin *= -1
            # Play a sound effect for bouncing off the top of the screen
            pygame.mixer.Sound.play(pygame.mixer.Sound("/Users/samuelbarrett/Desktop/bounce.wav"))
        

    def bounce_bottom(self):
        """
        Bounces the ball off the bottom of the screen.
        """
        if self.y > self.screen.get_height() - self.radius:
            self.velocity_y *= -1
            self.spin *= -1
            # Play a sound effect for bouncing off the bottom of the screen
            pygame.mixer.Sound.play(pygame.mixer.Sound("/Users/samuelbarrett/Desktop/bounce.wav"))


    def move(self, paddle1: Paddle, paddle2: Paddle, score: Score, gravitational_force:float = 0.0):
        """
        Moves the ball.
        Ball accelerates downward due to gravitational force
        """
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += gravitational_force - self.spin
        self.bounce_paddle(paddle1, paddle2, score)
        self.bounce_top()
        self.bounce_bottom()
        self.render()

    def reset(self):
        """
        Resets the ball to the middle of the screen.
        """
        self.x = self.screen.get_width() / 2
        self.y = self.screen.get_height() / 2
        self.spin = 0
        self.velocity_x = random.randint(6, 8)*self.randint_sign()
        self.velocity_y = random.randint(2, 3)*self.randint_sign()

    def randint_sign(self):
        """
        Returns a random sign.
        """
        return random.randint(0, 1) * 2 - 1


class Pong:
    """
    The main class of the game.
    Keys w and s are used to move player 1's paddle up and down the screen
    Keys up and down are used to move player 2's paddle up and down the screen
    The class get's events from the keyboard and mouse
    The class updates the score of a player if they gain a point
    The class render's the score on the top of the screen
    The paddle on the left is blue and the paddle on the right is red
    The ball is green
    """

    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 800
    BALL_RADIUS = 10
    PADDLE_WIDTH = 20
    PADDLE_HEIGHT = 200

    def __init__(self):
        """
        Initialises the game.
        Create an icon surface with the game's icon
        Create a screen with the game's title and icon
        """

        self.icon = pygame.image.load("/Users/samuelbarrett/Documents/Python Game/pong-icon.png")
        pygame.display.set_icon(self.icon)
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 20)
        self.score = Score(self.screen)
        self.ball = Ball(self.screen, self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2, self.BALL_RADIUS, Colours.GREEN)
        self.paddle1 = Paddle(self.screen, 0, self.SCREEN_HEIGHT / 2, Colours.BLUE)
        self.paddle2 = Paddle(self.screen, self.SCREEN_WIDTH - self.PADDLE_WIDTH, self.SCREEN_HEIGHT / 2, Colours.RED)
        self.running = True
        self.start_screen()

    def start_screen(self):
        """
        Display the start screen. Display game icon and title.
        """
        self.screen.fill(Colours.PURPLE)

        font = pygame.font.SysFont("monospace", 50)
        self.text = font.render("Welcome to Pong", True, Colours.WHITE)
        self.screen.blit(self.text, (self.screen.get_width() / 2 - self.text.get_width() / 2, self.screen.get_height() / 2 - self.text.get_height() / 2))
        font = pygame.font.SysFont("monospace", 20)
        self.text = font.render("Press space to start", True, Colours.WHITE)
        self.screen.blit(self.text, (self.screen.get_width() / 2 - self.text.get_width() / 2, self.screen.get_height() / 2 + self.text.get_height() / 2 + 50))
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

    def get_events(self):
        """
        Gets events from the keyboard and mouse.
        Holding a key down will make the paddle move up and down and accelerate
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.paddle1.move_up()
                elif event.key == pygame.K_s:
                    self.paddle1.move_down()
                elif event.key == pygame.K_UP:
                    self.paddle2.move_up()
                elif event.key == pygame.K_DOWN:
                    self.paddle2.move_down()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w or event.key == pygame.K_s:
                    self.paddle1.stop()
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    self.paddle2.stop()

    def update(self):
        """
        Updates the game.
        """
        self.paddle1.move()
        self.paddle2.move()
        self.paddle1.velocity /= 1.1
        self.paddle2.velocity /= 1.1
        self.ball.move(self.paddle1, self.paddle2, self.score)
        if self.score.score1 >= 10:
            text = "Player 1 wins! Final score: " + str(self.score.score1) + " - " + str(self.score.score2)
            self.reset(text)
        if self.score.score2 >= 10:
            text = "Player 2 wins! Final Score: " + str(self.score.score1) + " - " + str(self.score.score2)
            self.reset(text)

    def reset(self, text):
        """
        Player wins the game, display message for 3 seconds and reset the game
        """
        self.screen.fill(Colours.PURPLE)
        text = self.font.render(text, True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (self.screen.get_width() / 2, self.screen.get_height() / 2)
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.delay(3000)
        self.score.reset()
        self.paddle1.reset()
        self.paddle2.reset()
        self.ball.reset()


    def render(self):
        """
        Renders the game.
        """
        self.screen.fill(Colours.PURPLE)
        self.paddle1.render()
        self.paddle2.render()
        self.ball.render()
        self.score.render()
        pygame.display.flip()

    def run(self):
        """
        Runs the game.
        """
        while self.running:
            self.get_events()
            self.update()
            self.render()
            self.clock.tick(60)

    def quit(self):
        """
        Quits the game.
        """
        pygame.quit()
        sys.exit()

class Socket:
    """
    Socket class connects via webserver to control game logic
    """
    def __init__(self):
        """
        Initialises the socket.
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        """Connect the socket"""
        self.s.connect(('localhost', 8888))

    def get_events(self):
        """
        Get events from the socket.
        """
        while True:
            data = self.s.recv(1024)
            if not data:
                break
            if data == "w":
                self.paddle1.move_up()
            elif data == "s":
                self.paddle1.move_down()
            elif data == "up":
                self.paddle2.move_up()
            elif data == "down":
                self.paddle2.move_down()
            elif data == "space":
                self.ball.reset()
            elif data == "quit":
                self.quit()

    def quit(self):
        """
        Quit the socket.
        """
        self.s.close()



def main():
    """
    Runs the game.
    """
    pygame.init()
    pong = Pong()
    pong.run()
    pong.quit()


if __name__ == "__main__":
    main()


