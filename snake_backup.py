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

game_started = False

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

def load_high_score():
    try:
        with open("highscore.txt", "r") as file:
            return int(file.read())
    except:
        return 0
    
def save_high_score(high_score):
    with open("highscore.txt", "w") as file:
        file.write(str(high_score))

high_score = load_high_score()
game_started = False

def reset_game():
    snake = snake(10, 10, GREEN)
    enemy = snake(20, 20, (200, 120, 0))
    food = random_food_position(snake, enemy)
    score = 0
    game_over = False
    return snake, enemy, food, score, game_over

def draw_start_screen():
    title = font.render("Snake Game", True, WHITE)
    start_text = font.render("Press Space to Start", True, WHITE)
    controls_text = font.render("Use Arrow Keys to Move", True, WHITE)
    reset_text = font.render("Use H to reset high score", True, WHITE)

    screen.blit(title, (WIDTH // 2 - 90, HEIGHT // 2 - 60))
    screen.blit(start_text, (WIDTH // 2 - 140, HEIGHT // 2))
    screen.blit(controls_text, (WIDTH // 2 - 150, HEIGHT // 2 + 40))
    screen.blit(reset_text, (WIDTH //2 - 150, HEIGHT // 2 + 80))


def random_food_position(player_snake, enemy_snake):
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in player_snake.body and pos not in enemy_snake.body:
            return pos

def is_safe_direction(snake, direction, other_snake=None):
    head_x, head_y = snake.body[0]
    dx, dy = direction
    new_head = (head_x + dx, head_y + dy)

    #avoid walls
    if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
        return False
    
    #avoid own body
    if new_head in snake.body:
        return False
    
    #avoid other snake if provided
    if other_snake is not None and new_head in other_snake.body:
        return False
    
    return True

def random_enemy_direction(enemy, player, food):
    directions = [UP, DOWN, LEFT, RIGHT]
    safe_directions = []

    for direction in directions:
        #dont reverse
        if direction[0] == enemy.direction[0] and direction[1] == -enemy.direction[1]:
            continue

        if is_safe_direction(enemy, direction, player):
            safe_directions.append(direction)

    if not safe_directions:
        return
    
    def distance_to_food(direction):
        head_x, head_y = enemy.body[0]
        dx, dy = direction
        new_head = (head_x + dx, head_y + dy)
        return abs(new_head[0] - food[0]) + abs(new_head[1] - food[1])
    
    current_distance = abs(enemy.body[0][0] - food[0]) + abs(enemy.body[0][1] - food[1])
    #only keep moves that improve or maintain distance
    improving_moves = [d for d in safe_directions if distance_to_food(d) <= current_distance]
    #prefer moves that actually help toward food
    candidate_moves = improving_moves if improving_moves else safe_directions

    candidate_moves.sort(key=distance_to_food)

    best_distance = distance_to_food(candidate_moves[0])
    best_options = [d for d in candidate_moves if distance_to_food(d) == best_distance]

    #prefer current distance if it is still one of the best
    if enemy.direction in best_options:
        enemy.set_direction(enemy.direction)
    else:
        enemy.set_direction(random.choice(best_options))


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

def draw_score(score, high_score):
    score_text = font.render(f"Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (10, 45))

def draw_game_over(score):
    overlay = font.render(f"Game over. Score: {score}", True, WHITE)
    restart = font.render("Press R to restart", True, WHITE)
    screen.blit(overlay, (WIDTH // 2 - 140, HEIGHT // 2 - 20))
    screen.blit(restart, (WIDTH // 2 - 120, HEIGHT // 2 + 20))

def reset_game():
    snake = Snake(10, 10, GREEN)
    enemy = Snake(20, 20, (200, 120, 0))
    food = random_food_position(snake, enemy)
    score = 0
    game_over = False
    return snake, enemy, food, score, game_over
    
def main():
    global high_score
    enemy_turn_timer = 0
    snake, enemy, food, score, game_over = reset_game()
    game_started = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    high_score = 0
                    save_high_score(high_score)

                elif not game_started:
                    if event.key == pygame.K_SPACE:
                        game_started = True
                
                elif game_over:
                    if event.key == pygame.K_r:
                        snake, enemy, food, score, game_over = reset_game()
                        game_started = False

                else:
                    if  event.key == pygame.K_UP:
                        snake.set_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        snake.set_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        snake.set_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        snake.set_direction(RIGHT)
                    
        if game_started and not game_over:
            snake.move()

            enemy_turn_timer += 1

            if enemy_turn_timer % 5 == 0:
                random_enemy_direction(enemy, snake, food)
            
            enemy.move()

            if enemy.check_wall_collision() or enemy.check_self_collision():
                enemy.grow = 0

            if snake.body[0] == enemy.body[0]:
                game_over = True
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)

            if snake.check_wall_collision() or snake.check_self_collision():
                game_over = True
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
            
            if snake.eat_food(food):
                score += 1
                food = random_food_position(snake, enemy)

            if enemy.eat_food(food):
                food = random_food_position(snake, enemy)

        screen.fill(BLACK)
        draw_grid()
        
        if not game_started:
            draw_start_screen()
        else:
            draw_food(food)
            snake.draw(screen)
            enemy.draw(screen)
            draw_score(score, high_score)

        if game_over:
            draw_game_over(score)

        pygame.display.flip()
        clock.tick(10)

if __name__ == "__main__":
    main()