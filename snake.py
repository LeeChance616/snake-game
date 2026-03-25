import pygame
import random
import sys

# Initialize pygame
pygame.init()

#screen settings
WIDTH = 600
HEIGHT = 600
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

#colors
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GRAY = (40, 40, 40)

#Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

def random_food_position(snake):
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in snake.body:
            return pos 

class Snake:
    def __init__(self, x, y, color):
        self.body = [(x, y), (x - 1, y), (x - 2, y)]
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.color = color
        self.grow = 0

    def set_direction(self, new_direction):
        #prevent reversing into self
        if (new_direction[0] == self.direction[0] and new_direction[1] == -self.direction[1]):
            return
        self.next_direction = new_direction

    def move(self):
        self.direction = self.next_direction
        head_x, head_y = self.body[0]
        dx, dy = self.next_direction
        new_head = (head_x + dx, head_y +dy)

        self.body.insert(0, new_head)

        if self.grow > 0:
            self.grow -= 1
        else:
            self.body.pop()

    def check_wall_collision(self):
        head_x, head_y = self.body[0]
        return not (0 <= head_x < GRID_WIDTH and 0 <= head_y < GRID_HEIGHT)

    def check_self_collision(self):
        return self.body[0] in self.body[1:]

    def eat_food(self, food_pos):
        if self.body[0] == food_pos:
            self.grow += 1
            return True
        return False

    def draw(self, surface):
        for i, segment in enumerate(self.body):
            x, y = segment
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, WHITE if i == 0 else self.color, rect)

def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

def draw_food(food_pos):
    x, y = food_pos
    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, RED, rect)

def draw_score(score):
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def draw_game_over(score):
    overlay = font.render(f"Game over. Score: {score}", True, WHITE)
    restart = font.render("Press R to restart", True, WHITE)
    screen.blit(overlay, (WIDTH // 2 - 140, HEIGHT // 2 - 20))
    screen.blit(restart, (WIDTH // 2 - 120, HEIGHT // 2 + 20))

def reset_game():
    snake = Snake(10, 10, GREEN)
    food = random_food_position(snake)
    score = 0
    game_over = False
    return snake, food, score, game_over
    
def main():
    snake, food, score, game_over = reset_game()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.set_direction(UP)
                elif event.key == pygame.K_DOWN:
                    snake.set_direction(DOWN)
                elif event.key == pygame.K_LEFT:
                    snake.set_direction(LEFT)
                elif event.key == pygame.K_RIGHT:
                    snake.set_direction(RIGHT)
                elif event.key == pygame.K_r and game_over:
                    snake, food, score, game_over = reset_game()
        if not game_over:
            snake.move()
            if snake.check_wall_collision() or snake.check_self_collision():
                game_over = True
            
            if snake.eat_food(food):
                score += 1
                food = random_food_position(snake)

        screen.fill(BLACK)
        draw_grid()
        draw_food(food)
        snake.draw(screen)
        draw_score(score)

        if game_over:
            draw_game_over(score)

        pygame.display.flip()
        clock.tick(10)

if __name__ == "__main__":
    main()