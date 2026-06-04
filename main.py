import pygame
import sys
import random
import copy
import cv2
import mediapipe as md
import my_db


pygame.init()

username = ""
WIDTH = 600
HEIGHT = 800
game_font = pygame.font.SysFont(None, 40)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Tetris")

clock = pygame.time.Clock()
block_velocity = 1

ROWS = 20
COLS = 10
cell_size = 40

fall_interval = 0.5
fall_timer = 0.0
move_interval = 0.3
move_timer = 0.0
rotate_interval = 0.3
rotate_timer = 0.0
score = 0
level = 1
lines_removed = 0
game_over = False
score_submitted = False

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

grid = [[0] * COLS for _ in range(ROWS)]

I_block = [[[3, 0], [4, 0], [5, 0], [6, 0]], (0, 255, 255), 1]
short_I_block = [[[4, 0], [5, 0], [6, 0]], (141, 149, 252), 1]
L_block = [[[3, 0], [3, 1], [4, 1], [5, 1]], (255, 165, 0), 1]
J_block = [[[4, 1], [5, 1], [6, 1], [6, 0]], (0, 0, 255), 2]
S_block = [[[3, 1], [4, 1], [4, 0], [5, 0]], (0, 128, 0), 1]
Z_block = [[[4, 0], [5, 0], [5, 1], [6, 1]], (255, 0, 0), 2]
O_block = [[[4, 0], [5, 0], [5, 1], [4, 1]], (255, 255, 0), None]
T_block = [[[4, 0], [3, 1], [4, 1], [5, 1]], (128, 0, 128), 2]
dummy = [[[3, 0], [4, 0], [5, 0], [6, 0], [7, 0]], (0, 255, 255), 1]
blocks = [short_I_block, I_block, L_block, J_block, S_block, Z_block, O_block, T_block]
# blocks = [short_I_block]

def is_highscore(score, my_db):
    result = my_db.cursor.execute("SELECT score FROM leaderboard ORDER BY score ASC LIMIT 1").fetchone()
    my_db.conn.commit()
    min_score = result[0] if result is not None else 0

    if score > min_score and score > 0:
        return True
    else:
        return False

def spawn_block():
    b = copy.deepcopy(random.choice(blocks))
    return b

current_block = spawn_block()
block_active = True
fall_timer=0

for cell in current_block[0]:
    grid[cell[1]][cell[0]] = current_block[1]

running = True

while running:
    text_surface1 = game_font.render(f"Score: {score}", True, GREEN)
    text_rect1 = text_surface1.get_rect(center=(500, 30))
    text_surface2 = game_font.render(f"Level: {level}", True, GREEN)
    text_rect2 = text_surface2.get_rect(center=(500, 90))
    text_surface3 = game_font.render(f"Lines: {lines_removed}", True, GREEN)
    text_rect3 = text_surface3.get_rect(center=(500, 150))
    dt = clock.tick(60)/1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_over:      
                hs_screen = is_highscore(score, my_db)
                if hs_screen and not score_submitted:
                    if event.key == pygame.K_BACKSPACE:
                                    username = username[:-1]

                                # Enter key
                    elif event.key == pygame.K_RETURN:
                        print("Username entered:", username)
                        my_db.cursor.execute("INSERT INTO leaderboard (username, score) VALUES (?, ?);", (username, score))
                        my_db.conn.commit()

                        my_db.cursor.execute("""
                                            DELETE FROM leaderboard
                                            WHERE id NOT IN (
                                                SELECT id
                                                FROM leaderboard
                                                ORDER BY score DESC
                                                LIMIT 5
                                            )
                                            """)
                        my_db.conn.commit()
                        res = my_db.cursor.execute("SELECT username, score FROM leaderboard")
                        print(res.fetchall())
                        score_submitted = True

                    # Any other character
                    else:
                        username += event.unicode

                elif not hs_screen:
                    score_submitted = True 

                if score_submitted and event.key == pygame.K_r:
                    grid = [[0] * COLS for _ in range(ROWS)]
                    score = 0
                    level = 1
                    lines_removed = 0
                    fall_interval = 0.5
                    fall_timer = 0.0
                    current_block = spawn_block()
                    block_active = True
                    username = ""
                    score_submitted=False
                    game_over = False
                    for cell in current_block[0]:
                        grid[cell[1]][cell[0]] = current_block[1]

# restart screen
    if game_over:
        hs_screen = is_highscore(score, my_db)
        if hs_screen and not score_submitted:
            screen.fill((30, 30, 30))

            # Draw dark rounded panel in center
            panel_w, panel_h = 340, 280
            panel_x = WIDTH // 2 - panel_w // 2
            panel_y = HEIGHT // 2 - panel_h // 2
            pygame.draw.rect(screen, (20, 20, 20), (panel_x, panel_y, panel_w, panel_h), border_radius=12)
            pygame.draw.rect(screen, (80, 80, 80), (panel_x, panel_y, panel_w, panel_h), 2, border_radius=12)

            # "NEW HIGH SCORE!" title
            title_font = pygame.font.SysFont("Arial", 28, bold=True)
            title_surf = title_font.render("NEW HIGH SCORE!", True, (255, 255, 255))
            screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, panel_y + 40)))

            # Score number (big, gold)
            score_font = pygame.font.SysFont("Arial", 52, bold=True)
            score_surf = score_font.render(f"{score:,}", True, (255, 215, 0))
            screen.blit(score_surf, score_surf.get_rect(center=(WIDTH // 2, panel_y + 100)))

            # "ENTER YOUR NAME:" label
            label_font = pygame.font.SysFont("Arial", 18, bold=True)
            label_surf = label_font.render("ENTER YOUR NAME:", True, (180, 180, 180))
            screen.blit(label_surf, label_surf.get_rect(center=(WIDTH // 2, panel_y + 155)))

            # Textbox rectangle
            box_w, box_h = 220, 36
            box_x = WIDTH // 2 - box_w // 2
            box_y = panel_y + 175
            pygame.draw.rect(screen, (10, 10, 10), (box_x, box_y, box_w, box_h), border_radius=4)
            pygame.draw.rect(screen, (150, 150, 150), (box_x, box_y, box_w, box_h), 2, border_radius=4)

            # Typed username text inside box
            name_font = pygame.font.SysFont("Arial", 22)
            name_surf = name_font.render(username, True, (255, 255, 255))
            screen.blit(name_surf, (box_x + 8, box_y + 7))

            # Blinking cursor (simple — uses time, no sprites)
            if pygame.time.get_ticks() % 1000 < 500:
                cursor_x = box_x + 8 + name_surf.get_width()
                pygame.draw.line(screen, (255, 255, 255), (cursor_x, box_y + 6), (cursor_x, box_y + box_h - 6), 2)

            # "Press ENTER to confirm" hint
            hint_font = pygame.font.SysFont("Arial", 15)
            hint_surf = hint_font.render("Press ENTER to confirm", True, (120, 120, 120))
            screen.blit(hint_surf, hint_surf.get_rect(center=(WIDTH // 2, panel_y + 240)))

            pygame.display.flip()
            continue
        else:
            screen.fill((0, 0, 0))
            x = WIDTH//2
            y = HEIGHT//2-200
            font = pygame.font.Font(None, 36)
            over_font = pygame.font.SysFont(None, 64)
            sub_font  = pygame.font.SysFont(None, 36)
            over_surf = over_font.render("GAME OVER", True, (255, 50, 50))
            score_surf = sub_font.render(f"Score: {score}", True, WHITE)
            restart_surf = sub_font.render("Press R to restart", True, (180, 180, 180))
            screen.blit(over_surf,    over_surf.get_rect(center=(WIDTH//2, 60)))
            screen.blit(score_surf,   score_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 300)))
            screen.blit(restart_surf, restart_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 350)))

            col1_width = 200
            col2_width = 100
            total_width = (col1_width+col2_width) 
            row_height = 50

            # Header cells
            pygame.draw.rect(screen, (200, 200, 200), (x-total_width//2, y-row_height, col1_width+col2_width, row_height), 2)
            
            pygame.draw.rect(screen, (200, 200, 200),
                            (x-total_width//2, y, col1_width, row_height), 2)

            pygame.draw.rect(screen, (200, 200, 200),
                            (x-total_width//2 + col1_width, y, col2_width, row_height), 2)

            # Data cells
            def create_data_cell(x, y, row_num):
                pygame.draw.rect(screen, (200, 200, 200),
                                (x-total_width//2, y + row_num*row_height, col1_width, row_height), 2)

                pygame.draw.rect(screen, (200, 200, 200),
                            (x + col1_width - total_width//2, y + row_num*row_height,
                            col2_width, row_height), 2)
            create_data_cell(x, y, 1)
            create_data_cell(x, y, 2)
            create_data_cell(x, y, 3)
            create_data_cell(x, y, 4)
            create_data_cell(x, y, 5)

            # Header text
            screen.blit(
                font.render("High Score", True, (255, 255, 255)),
                ((x-total_width//2) + 90, y-38)
            )
            screen.blit(
                font.render("Username", True, (255, 255, 255)),
                (x + 20-total_width//2, y + 10)
            )

            screen.blit(
                font.render("Score", True, (255, 255, 255)),
                (x + col1_width + 20-total_width//2, y + 10)
            )

            # Row text
            def display_leaders(x, y, row_num, result):
                if row_num-1 >= len(result):
                    return
                username = result[row_num-1][0]
                score = result[row_num-1][1]
                screen.blit(
                    font.render(username, True, (255, 255, 255)),
                    (x + 20-total_width//2, y + row_num*row_height + 10)
                )

                screen.blit(
                    font.render(str(score), True, (255, 255, 255)),
                    (x + col1_width + 20-total_width//2, y + row_num*row_height + 10)
                )

            result = my_db.cursor.execute("SELECT username, score FROM leaderboard ORDER BY score DESC").fetchall()
            display_leaders(x, y, 1, result)
            display_leaders(x, y, 2, result)
            display_leaders(x, y, 3, result)
            display_leaders(x, y, 4, result)
            display_leaders(x, y, 5, result)

            pygame.display.flip()
            # pygame.display.update()
            continue

    keys = pygame.key.get_pressed()

    def get_bounds():
        min_col = min(c[0] for c in current_block[0])
        max_col = max(c[0] for c in current_block[0])
        max_row = max(c[1] for c in current_block[0])
        return min_col, max_col, max_row
    
    def block_removal(a):
        line_cnt = 0
        for i, row in enumerate(a):
            if not 0 in row:
                a[i] = [0]*len(row)
                line_cnt+=1
                non_zero_rows = [idx for idx, row in enumerate(a[:i+1]) if any(row)]
                for idx in reversed(non_zero_rows):
                    a[idx], a[idx+1] = a[idx+1], a[idx]
        return a, line_cnt
    
    def rotate_block(block):
        pivot = block[0][block[2]]
        new_positions = []
        for cell in block[0]:
            if cell!=pivot:
                relative = [cell[0] - pivot[0], cell[1] - pivot[1]]
                rotated = [relative[1], -relative[0]]
                new_positions.append([rotated[0] + pivot[0], rotated[1] + pivot[1]])
            else:
                new_positions.append([cell[0], cell[1]])
        return new_positions
    
    def bring_down(grid, block):
        while True:
            max_row = max(cell[1] for cell in block[0])

            if max_row >= len(grid) - 1:
                for cell in block[0]:
                    grid[cell[1]][cell[0]] = block[1]  # restore on bottom wall hit
                break

            for cell in block[0]:
                grid[cell[1]][cell[0]] = 0

            if any(grid[cell[1]+1][cell[0]] != 0 for cell in block[0]):
                for cell in block[0]:
                    grid[cell[1]][cell[0]] = block[1]
                break

            for cell in block[0]:
                cell[1] += 1
            for cell in block[0]:
                grid[cell[1]][cell[0]] = block[1]  # ← fixed

        return grid

    move_timer+=dt
    if move_timer >= move_interval:

        min_col, max_col, max_row = get_bounds()

        if keys[pygame.K_LEFT] and min_col > 0 and max_row < ROWS-1:
            move_timer = 0
            for cell in current_block[0]:
                grid[cell[1]][cell[0]] = 0

            collision = any(grid[cell[1]][cell[0]-1] != 0 for cell in current_block[0]) 

            if collision:
                for cell in current_block[0]:
                    grid[cell[1]][cell[0]] = current_block[1]
            else:
                for cell in current_block[0]:
                    cell[0] -= 1
                for cell in current_block[0]:
                    grid[cell[1]][cell[0]] = current_block[1]

        elif keys[pygame.K_RIGHT] and max_col < COLS - 1 and max_row < ROWS-1:
            move_timer = 0
            for cell in current_block[0]:
                grid[cell[1]][cell[0]] = 0

            collision = any(grid[cell[1]][cell[0]+1] != 0 for cell in current_block[0]) 

            if collision:
                for cell in current_block[0]:
                    grid[cell[1]][cell[0]] = current_block[1]
            else:
                for cell in current_block[0]:
                    cell[0] += 1
                for cell in current_block[0]:
                    grid[cell[1]][cell[0]] = current_block[1]

        # if keys[pygame.K_SPACE] and max_row < ROWS-1:
        #     grid = bring_down(grid, current_block)

        if keys[pygame.K_DOWN]:
            fall_interval = 0.05
        else:
            fall_interval = max(0.05, 0.8 - ((level - 1) * 0.007))



    if block_active:
        fall_timer+=dt

        if fall_timer >= fall_interval:

            min_col, max_col, max_row = get_bounds()

            if max_row < ROWS-1:
                fall_timer = 0
                for cell in current_block[0]:
                    grid[cell[1]][cell[0]] = 0

                collision = any(grid[cell[1]+1][cell[0]] != 0 for cell in current_block[0]) 

                if collision:
                    for cell in current_block[0]:
                        grid[cell[1]][cell[0]] = current_block[1]
                        block_active = False
                else:
                    for cell in current_block[0]:
                        cell[1]+=1

                    for cell in current_block[0]:
                        grid[cell[1]][cell[0]] = current_block[1]


            else:
                block_active = False

        rotate_timer+=dt
        if rotate_timer >= rotate_interval:
            if keys[pygame.K_r]:
                if current_block[2]!=None:
                    rotate_timer = 0

                    new_positions = rotate_block(current_block)

                    out_of_bounds = any(cell[0] < 0 or cell[0] >= COLS or cell[1] < 0 or cell[1] >= ROWS for cell in new_positions) 

                    for cell in current_block[0]:
                        grid[cell[1]][cell[0]] = 0

                    if out_of_bounds:
                        overlaps_settled = False
                    else:
                        overlaps_settled = any(grid[cell[1]][cell[0]]!=0 for cell in new_positions)

                    if out_of_bounds or overlaps_settled:
                        for cell in current_block[0]:
                            grid[cell[1]][cell[0]] = current_block[1]
                    else:
                        current_block[0] = new_positions
                        for cell in current_block[0]:
                            grid[cell[1]][cell[0]] = current_block[1]
                else: pass
    if not block_active:
        grid, line_cnt = block_removal(grid)
        if line_cnt == 1:
            score+=100*level
        elif line_cnt == 2:
            score+=300*level
        elif line_cnt == 3:
            score+=500*level
        elif line_cnt == 4:
            score+=800*level
        lines_removed+=line_cnt
        if lines_removed%10 == 0 and lines_removed!= 0:
            level+=1
        current_block = spawn_block()
        block_active = True

    
        if any(grid[cell[1]][cell[0]] != 0 for cell in current_block[0]):
            game_over = True
        else:
            for cell in current_block[0]:
                grid[cell[1]][cell[0]] = current_block[1]
            block_active = True
            fall_timer = 0

    # --- Draw ---
    screen.fill((0, 0, 0))

    screen.blit(text_surface1, text_rect1)
    screen.blit(text_surface2, text_rect2)
    screen.blit(text_surface3, text_rect3)

    for row in range(ROWS):
        for col in range(COLS):
            x = col * cell_size  # col → x (horizontal)
            y = row * cell_size  # row → y (vertical)
            rect = pygame.Rect(x, y, cell_size, cell_size)
            if grid[row][col] != 0:
                pygame.draw.rect(screen, grid[row][col], rect)
            pygame.draw.rect(screen, (80, 80, 80), rect, 1)

    pygame.display.update()

pygame.quit()
sys.exit()


