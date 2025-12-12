import pygame
import random
import time
class WumpusAgent:
    def __init__(self):
        self.kb = set()
        self.reset_state()
    def reset_state(self):
        self.agent_x = 3
        self.agent_y = 0
        self.direction = 0
        self.has_gold = False
        self.arrows = 1
        self.kb.clear()
        self.kb.add(('V', 3, 0))
        self.kb.add(('OK', 3, 0))
        self.kb.add(('~P', 3, 0))
        self.kb.add(('~W', 3, 0))
    def get_cell_info(self, r, c):
        info = {}
        info['Visited'] = ('V', r, c) in self.kb
        info['Safe'] = ('OK', r, c) in self.kb
        info['NoPit'] = ('~P', r, c) in self.kb
        info['NoWumpus'] = ('~W', r, c) in self.kb
        info['Breeze'] = ('B', r, c) in self.kb
        info['Stench'] = ('S', r, c) in self.kb
        return info
    def get_neighbors(self, r, c):
        adj = [(r, c + 1), (r + 1, c), (r, c - 1), (r - 1, c)]
        valid_neighbors = []
        for ax, ay in adj:
            if 0 <= ax < 4 and 0 <= ay < 4:
                valid_neighbors.append((ax, ay))
        return valid_neighbors
    def tell_kb(self, percepts, r, c):
        self.agent_x, self.agent_y = r, c
        self.kb.add(('V', r, c))
        if 'Breeze' in percepts:
            self.kb.add(('B', r, c))
            self.kb.discard(('~B', r, c))
        else:
            self.kb.add(('~B', r, c))
            self.kb.discard(('B', r, c))
        if 'Stench' in percepts:
            self.kb.add(('S', r, c))
            self.kb.discard(('~S', r, c))
        else:
            self.kb.add(('~S', r, c))
            self.kb.discard(('S', r, c))
        if 'Glitter' in percepts:
            self.kb.add(('G', r, c))
    def infer_safety(self):
        new_facts = set()
        for r in range(4):
            for c in range(4):
                if ('V', r, c) in self.kb:
                    neighbors = self.get_neighbors(r, c)
                    if ('~B', r, c) in self.kb:
                        for nr, nc in neighbors:
                            new_facts.add(('~P', nr, nc))
                    if ('~S', r, c) in self.kb:
                        for nr, nc in neighbors:
                            new_facts.add(('~W', nr, nc))
        self.kb.update(new_facts)
        for r in range(4):
            for c in range(4):
                if ('~P', r, c) in self.kb and ('~W', r, c) in self.kb:
                    self.kb.add(('OK', r, c))
    def find_safe_unvisited(self):
        neighbors = self.get_neighbors(self.agent_x, self.agent_y)
        for r, c in neighbors:
            is_ok = ('OK', r, c) in self.kb
            is_unvisited = ('V', r, c) not in self.kb
            if is_ok and is_unvisited:
                return r, c
        if self.has_gold:
             if self.agent_x == 3 and self.agent_y == 0:
                 return None
             safe_visited_neighbors = [(r, c) for r, c in neighbors if ('OK', r, c) in self.kb and ('V', r, c) in self.kb]
             if safe_visited_neighbors:
                 best_neighbor = min(safe_visited_neighbors, key=lambda pos: abs(pos[0]-3) + abs(pos[1]-0))
                 return best_neighbor
        return None
    def choose_action(self, percepts):
        if 'Glitter' in percepts:
            self.has_gold = True
            return 'Grab'
        if self.has_gold and self.agent_x == 3 and self.agent_y == 0:
            return 'Climb'
        target_pos = self.find_safe_unvisited()
        if target_pos:
            tr, tc = target_pos
            current_dir = self.direction
            dr = tr - self.agent_x
            dc = tc - self.agent_y
            target_dir = -1
            if (dr, dc) == (-1, 0): target_dir = 3
            elif (dr, dc) == (1, 0): target_dir = 1
            elif (dr, dc) == (0, 1): target_dir = 0
            elif (dr, dc) == (0, -1): target_dir = 2
            if target_dir == -1: return 'TurnLeft'
            diff = (target_dir - current_dir) % 4
            if diff == 0:
                return 'MoveForward'
            elif diff == 1:
                return 'TurnLeft'
            elif diff == 3:
                return 'TurnRight'
            else:
                return 'TurnLeft'
        neighbors = self.get_neighbors(self.agent_x, self.agent_y)
        if neighbors:
            def get_risk(r, c):
                if ('OK', r, c) in self.kb:
                    return 0
                elif ('~P', r, c) in self.kb and ('~W', r, c) in self.kb:
                    return 1
                elif ('~P', r, c) in self.kb or ('~W', r, c) in self.kb:
                    return 2
                else:
                    return 3
            tr, tc = min(neighbors, key=lambda pos: get_risk(pos[0], pos[1]))
            dr = tr - self.agent_x
            dc = tc - self.agent_y
            if (dr, dc) == (-1, 0):
                target_dir = 3
            elif (dr, dc) == (1, 0):
                target_dir = 1
            elif (dr, dc) == (0, 1):
                target_dir = 0
            elif (dr, dc) == (0, -1):
                target_dir = 2
            else:
                return 'TurnLeft'
            diff = (target_dir - self.direction) % 4
            if diff == 0:
                return 'MoveForward'
            elif diff == 1:
                return 'TurnLeft'
            elif diff == 3:
                return 'TurnRight'
            else:
                return 'TurnLeft'
        return 'TurnLeft'
class WumpusWorld:
    """
    Manages the state of the Wumpus World including grid, agent, hazards, and scoring.
    """
    def __init__(self):
        self.agent = WumpusAgent()
        self.reset_game_state()
        self._setup_world()
    def reset_game_state(self):
        """Resets all world variables to their initial values."""
        self.grid = [[[] for _ in range(4)] for _ in range(4)]
        self.agent_x = 3
        self.agent_y = 0
        self.direction = 0
        self.arrows = 1
        self.score = 0
        self.alive = True
        self.has_gold = False
        self.wumpus_alive = True
        self.scream_triggered = False
        self.won = False
    def _setup_world(self):
        """
        Randomly sets up hazards and gold on the grid.
        Called after initial world construction or on reset.
        """
        self.reset_game_state()
        self.agent.reset_state()
        positions = [(x, y) for x in range(4) for y in range(4) if (x, y) != (3, 0)]
        pits = []
        for pos in positions:
            if random.random() < 0.2:
                self.grid[pos[0]][pos[1]].append('P')
                pits.append(pos)
        remaining = [pos for pos in positions if pos not in pits]
        if remaining:
            wumpus_pos = random.choice(remaining)
            self.grid[wumpus_pos[0]][wumpus_pos[1]].append('W')
            remaining.remove(wumpus_pos)
        if remaining:
            gold_pos = random.choice(remaining)
            self.grid[gold_pos[0]][gold_pos[1]].append('G')
    def get_percepts(self, x, y):
        """Returns a set of percepts based on current position."""
        percepts = set()
        if 'G' in self.grid[x][y] and not self.has_gold:
            percepts.add('Glitter')
        adj = [(x, y+1), (x+1, y), (x, y-1), (x-1, y)]
        adj_objects = set()
        for ax, ay in adj:
            if 0 <= ax < 4 and 0 <= ay < 4:
                adj_objects.update(self.grid[ax][ay])
        if 'P' in adj_objects:
            percepts.add('Breeze')
        if 'W' in adj_objects and self.wumpus_alive:
            percepts.add('Stench')
        return percepts
    def process_action(self, action):
        """Processes the given action, updates the world state, returns percepts and message."""
        if not self.alive:
            return set(), "Game Over"
        current_percepts = self.get_percepts(self.agent_x, self.agent_y)
        message = f"Agent performed: {action}"
        self.scream_triggered = False
        if action == 'Shoot':
            if self.arrows <= 0:
                message = "No arrows left, shot missed."
            else:
                self.score -= 10
                self.arrows -= 1
                dx_dy = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                dx, dy = dx_dy[self.direction]
                sx, sy = self.agent_x, self.agent_y
                hit = False
                for _ in range(4):
                    sx += dx
                    sy += dy
                    if not (0 <= sx < 4 and 0 <= sy < 4): break
                    if 'W' in self.grid[sx][sy]:
                        self.grid[sx][sy].remove('W')
                        self.wumpus_alive = False
                        self.scream_triggered = True
                        message = "Killed Wumpus! (Scream)"
                        hit = True
                        break
                if not hit: message = "Shot missed."
        elif action == 'Climb':
            if self.agent_x == 3 and self.agent_y == 0:
                if self.has_gold: self.score += 1000
                if self.has_gold: self.won = True
                message = f"Climbed out! Score: {self.score}"
                self.alive = False
            else: message = "Can't climb here."
        elif action == 'Grab':
            if 'G' in self.grid[self.agent_x][self.agent_y] and not self.has_gold:
                self.grid[self.agent_x][self.agent_y].remove('G')
                self.has_gold = True
                message = "Grabbed Gold"
            else: message = "Nothing to Grab."
        elif action == 'MoveForward':
            dx_dy = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            dx, dy = dx_dy[self.direction]
            nx, ny = self.agent_x + dx, self.agent_y + dy
            if not (0 <= nx < 4 and 0 <= ny < 4):
                current_percepts.add('Bump')
                message = "Bumped into wall."
            else:
                self.agent_x, self.agent_y = nx, ny
                self.agent.agent_x, self.agent.agent_y = nx, ny
                cell_content = self.grid[nx][ny]
                if 'P' in cell_content:
                    self.alive = False
                    self.score -= 1000
                    message = "Fell into Pit! (Death)"
                elif 'W' in cell_content and self.wumpus_alive:
                    self.alive = False
                    self.score -= 1000
                    message = "Eaten by Wumpus! (Death)"
        elif action == 'TurnLeft':
            self.direction = (self.direction + 1) % 4
            self.agent.direction = self.direction
        elif action == 'TurnRight':
            self.direction = (self.direction - 1) % 4
            self.agent.direction = self.direction
        if action not in ('Climb'):
            self.score -= 1
        new_percepts = self.get_percepts(self.agent_x, self.agent_y)
        if self.scream_triggered:
            new_percepts.add('Scream')
        return new_percepts, message
class WumpusGUI:
    """
    Pygame-based GUI for visualization and control.
    """
    def __init__(self, world):
        self.world = world
        pygame.init()
        self.WIDTH, self.HEIGHT = 1000, 650
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Wumpus World Logical Agent")
        self.CELL_SIZE = 100
        self.GRID_X, self.GRID_Y = 50, 50
        self.side_x = 550
        self.side_y = 50
        self.font_xsmall = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.DARK_GRAY = (80, 80, 80)
        self.UNKNOWN_GRAY = (200, 200, 200)
        self.SAFE_GREEN = (150, 255, 150)
        self.VISITED_BLUE = (200, 220, 255)
        self.AGENT_YELLOW = (255, 255, 100)
        self.DANGER_RED = (255, 100, 100)
        self.GOLD_ORANGE = (255, 215, 0)
        self.buttons = {}
        button_y = 450
        button_x = self.side_x
        manual_actions = [
            ("Move Forward", "MoveForward"),
            ("Turn Left", "TurnLeft"),
            ("Turn Right", "TurnRight"),
            ("Grab Gold", "Grab"),
            ("Shoot Arrow", "Shoot"),
            ("Climb Out", "Climb")
        ]
        for text, action in manual_actions:
            self.buttons[action] = pygame.Rect(button_x, button_y, 150, 30)
            button_y += 35
        button_y += 20
        self.buttons["toggle_autoplay"] = pygame.Rect(button_x, button_y, 150, 30)
        button_y += 35
        self.buttons["reset"] = pygame.Rect(button_x, button_y, 150, 30)
        self.is_auto_playing = False
        self.autoplay_delay = 500
        self.AGENT_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.AGENT_EVENT, self.autoplay_delay)
        self.log_lines = []
        self.reset_game()
        self.running = True
    def draw(self):
        """Draws the grid and side panel."""
        self.screen.fill(self.WHITE)
        r_agent, c_agent = self.world.agent_x, self.world.agent_y
        percepts = self.world.get_percepts(r_agent, c_agent)
        for r in range(4):
            for c in range(4):
                x = self.GRID_X + c * self.CELL_SIZE
                y = self.GRID_Y + r * self.CELL_SIZE
                rect = pygame.Rect(x, y, self.CELL_SIZE, self.CELL_SIZE)
                kb_info = self.world.agent.get_cell_info(r, c)
                bg_color = self.UNKNOWN_GRAY
                if kb_info['Visited']:
                    bg_color = self.VISITED_BLUE
                if kb_info['Safe']:
                    bg_color = self.SAFE_GREEN
                if r == r_agent and c == c_agent:
                    bg_color = self.AGENT_YELLOW
                pygame.draw.rect(self.screen, self.BLACK, rect, 2)
                inner_rect = pygame.Rect(x + 2, y + 2, self.CELL_SIZE - 4, self.CELL_SIZE - 4)
                pygame.draw.rect(self.screen, bg_color, inner_rect)
                percept_icons = []
                if r == r_agent and c == c_agent:
                    if 'P' in self.world.grid[r][c]: percept_icons.append('P')
                    if 'W' in self.world.grid[r][c] and self.world.wumpus_alive: percept_icons.append('W')
                    if 'G' in self.world.grid[r][c]: percept_icons.append('G')
                    if 'Breeze' in percepts: percept_icons.append('B')
                    if 'Stench' in percepts: percept_icons.append('S')
                percept_text = ' '.join(percept_icons)
                if percept_text:
                    text_surf = self.font_medium.render(percept_text, True, self.DARK_GRAY)
                    self.screen.blit(text_surf, (x + 5, y + 5))
                kb_symbols = []
                if kb_info['NoWumpus']: kb_symbols.append(self.font_xsmall.render('~W', True, self.SAFE_GREEN))
                if kb_info['NoPit']: kb_symbols.append(self.font_xsmall.render('~P', True, self.SAFE_GREEN))
                if kb_info['Stench'] and not kb_info['NoWumpus']:
                    unvisited_neighbors = [pos for pos in self.world.agent.get_neighbors(r, c) if ('V', pos[0], pos[1]) not in self.world.agent.kb]
                    if any(('~W', nr, nc) not in self.world.agent.kb for nr, nc in unvisited_neighbors):
                        kb_symbols.append(self.font_xsmall.render('W?', True, self.GOLD_ORANGE))
                if kb_info['Breeze'] and not kb_info['NoPit']:
                    unvisited_neighbors = [pos for pos in self.world.agent.get_neighbors(r, c) if ('V', pos[0], pos[1]) not in self.world.agent.kb]
                    if any(('~P', nr, nc) not in self.world.agent.kb for nr, nc in unvisited_neighbors):
                        kb_symbols.append(self.font_xsmall.render('P?', True, self.GOLD_ORANGE))
                symbol_x = x + 5
                symbol_y = y + self.CELL_SIZE - 20
                for sym_surf in kb_symbols:
                    self.screen.blit(sym_surf, (symbol_x, symbol_y))
                    symbol_x += sym_surf.get_width() + 5
                if r == r_agent and c == c_agent:
                    self.draw_agent_arrow(x, y, self.world.direction)
                    if self.world.has_gold:
                         gold_icon = self.font_medium.render('🏆', True, self.GOLD_ORANGE)
                         self.screen.blit(gold_icon, (x + 5, y + self.CELL_SIZE - 40))
        if self.world.won:
            game_over_text = self.font_large.render("You Win! Press R to Restart", True, self.SAFE_GREEN)
            self.screen.blit(game_over_text, (self.WIDTH // 2 - game_over_text.get_width() // 2, self.HEIGHT // 2))
        elif not self.world.alive:
            game_over_text = self.font_large.render("Game Over! Press R to Restart", True, self.DANGER_RED)
            self.screen.blit(game_over_text, (self.WIDTH // 2 - game_over_text.get_width() // 2, self.HEIGHT // 2))
        y = self.side_y
        self._draw_text(f"--- AGENT STATUS ---", self.font_medium, self.side_x, y)
        y += 30
        status = 'Alive' if self.world.alive else 'Dead / Exited'
        status_color = self.SAFE_GREEN if self.world.alive else self.DANGER_RED
        self._draw_text(f"Status: {status}", self.font_small, self.side_x, y, color=status_color)
        y += 25
        score_text = f"Score: {self.world.score}"
        self._draw_text(score_text, self.font_small, self.side_x, y)
        y += 25
        wumpus_status = 'Alive' if self.world.wumpus_alive else 'Killed (💀)'
        wumpus_color = self.DANGER_RED if self.world.wumpus_alive else self.SAFE_GREEN
        self._draw_text(f"Wumpus: {wumpus_status}", self.font_small, self.side_x, y, color=wumpus_color)
        y += 25
        gold_status = 'Yes (🏆)' if self.world.has_gold else 'No'
        self._draw_text(f"Gold: {gold_status}", self.font_small, self.side_x, y)
        y += 25
        arrows_text = f"Arrows: {self.world.arrows}"
        self._draw_text(arrows_text, self.font_small, self.side_x, y)
        y += 40
        self._draw_text(f"--- CURRENT PERCEPTS ({r_agent}, {c_agent}) ---", self.font_medium, self.side_x, y)
        y += 30
        percepts = self.world.get_percepts(r_agent, c_agent)
        if self.world.scream_triggered: percepts.add('Scream')
        percept_str = ', '.join(sorted(percepts)) if percepts else 'None'
        percept_text = f"Percepts: {percept_str}"
        self._draw_text(percept_text, self.font_small, self.side_x, y)
        y += 40
        log_title = self.font_small.render("Action Log (Last 6):", True, self.BLACK)
        self.screen.blit(log_title, (self.side_x, y))
        y += 25
        for line in self.log_lines[-6:]:
            line_text = self.font_xsmall.render(line, True, self.DARK_GRAY)
            self.screen.blit(line_text, (self.side_x, y))
            y += 20
        y += 10
        for key, rect in self.buttons.items():
            pygame.draw.rect(self.screen, self.VISITED_BLUE, rect)
            pygame.draw.rect(self.screen, self.DARK_GRAY, rect, 2)
            if key == 'MoveForward': text = 'Move Forward (↑)'
            elif key == 'TurnLeft': text = 'Turn Left (←)'
            elif key == 'TurnRight': text = 'Turn Right (→)'
            elif key == 'Grab': text = 'Grab Gold (G)'
            elif key == 'Shoot': text = 'Shoot Arrow (S)'
            elif key == 'Climb': text = 'Climb Out (C)'
            elif key == 'toggle_autoplay': text = 'Stop Auto-Play' if self.is_auto_playing else 'Auto-Play Agent (A)'
            elif key == 'reset': text = 'New World / Reset (R)'
            else: text = key
            button_text = self.font_small.render(text, True, self.BLACK)
            self.screen.blit(button_text, (rect.x + 5, rect.y + 5))
        pygame.display.flip()
    def draw_agent_arrow(self, x, y, direction):
        """Draws an arrow shape for the agent direction."""
        center_x = x + self.CELL_SIZE // 2
        center_y = y + self.CELL_SIZE // 2
        if direction == 0:
            points = [(center_x - 15, center_y - 10), (center_x + 15, center_y), (center_x - 15, center_y + 10)]
        elif direction == 1:
            points = [(center_x - 10, center_y - 15), (center_x + 10, center_y - 15), (center_x, center_y + 15)]
        elif direction == 2:
            points = [(center_x + 15, center_y - 10), (center_x - 15, center_y), (center_x + 15, center_y + 10)]
        else:
            points = [(center_x - 10, center_y + 15), (center_x + 10, center_y + 15), (center_x, center_y - 15)]
        pygame.draw.polygon(self.screen, self.BLACK, points)
    def _draw_text(self, text, font, x, y, color=None):
        """Helper to draw text with specified font and optional color."""
        if color is None: color = self.BLACK
        text_surf = font.render(text, True, color)
        self.screen.blit(text_surf, (x, y))
    def perform_action(self, action, is_agent=False):
        """Performs the action, updates log and draws."""
        percepts, message = self.world.process_action(action)
        if action != 'Start':
            self.world.agent.tell_kb(percepts, self.world.agent_x, self.world.agent_y)
            self.world.agent.infer_safety()
        prefix = "[A]" if is_agent else "[M]"
        self.log_lines.append(f"{prefix} {message}")
        if is_agent and action == 'TurnLeft' and self.world.alive and self.world.agent.find_safe_unvisited() is None:
            self.log_lines.append("--- AGENT STUCK / EXPLORING RANDOMLY ---")
        if 'Scream' in percepts and is_agent:
            self.log_lines.append("--- WUMPUS SCREAMED! ---")
        if not self.world.alive:
            self.log_lines.append(f"*** GAME OVER: {message} ***")
            self.is_auto_playing = False
        self.draw()
        return self.world.alive
    def toggle_autoplay(self, force_stop=False):
        """Starts or stops the agent's auto-play."""
        if self.is_auto_playing or force_stop:
            self.is_auto_playing = False
            self.log_lines.append("--- AUTOPLAY STOPPED ---")
        elif self.world.alive:
            self.is_auto_playing = True
            self.log_lines.append("--- AUTOPLAY STARTED ---")
        self.draw()
    def agent_action(self):
        """Performs one agent action."""
        if not self.is_auto_playing or not self.world.alive:
            self.is_auto_playing = False
            return
        percepts = self.world.get_percepts(self.world.agent_x, self.world.agent_y)
        action = self.world.agent.choose_action(percepts)
        self.perform_action(action, is_agent=True)
    def reset_game(self):
        """Resets the world and agent and starts a new game."""
        self.toggle_autoplay(force_stop=True)
        self.world._setup_world()
        self.log_lines.clear()
        self.log_lines.append("--- NEW WORLD GENERATED ---")
        initial_percepts = self.world.get_percepts(self.world.agent_x, self.world.agent_y)
        self.world.agent.tell_kb(initial_percepts, self.world.agent_x, self.world.agent_y)
        self.world.agent.infer_safety()
        self.perform_action('Start', is_agent=False)
    def run(self):
        """Main game loop."""
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.world.direction = 3
                        self.world.agent.direction = 3
                        self.perform_action('MoveForward', is_agent=False)
                    elif event.key == pygame.K_DOWN:
                        self.world.direction = 1
                        self.world.agent.direction = 1
                        self.perform_action('MoveForward', is_agent=False)
                    elif event.key == pygame.K_LEFT:
                        self.world.direction = 2
                        self.world.agent.direction = 2
                        self.perform_action('MoveForward', is_agent=False)
                    elif event.key == pygame.K_RIGHT:
                        self.world.direction = 0
                        self.world.agent.direction = 0
                        self.perform_action('MoveForward', is_agent=False)
                    elif event.key == pygame.K_g:
                        self.perform_action('Grab', is_agent=False)
                    elif event.key == pygame.K_s:
                        self.perform_action('Shoot', is_agent=False)
                    elif event.key == pygame.K_c:
                        self.perform_action('Climb', is_agent=False)
                    elif event.key == pygame.K_a:
                        self.toggle_autoplay()
                    elif event.key == pygame.K_r:
                        self.reset_game()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for key, rect in self.buttons.items():
                            if rect.collidepoint(event.pos):
                                if key in ['MoveForward', 'TurnLeft', 'TurnRight', 'Grab', 'Shoot', 'Climb']:
                                    self.perform_action(key, is_agent=False)
                                elif key == 'toggle_autoplay':
                                    self.toggle_autoplay()
                                elif key == 'reset':
                                    self.reset_game()
                                break
                elif event.type == self.AGENT_EVENT:
                    if self.is_auto_playing:
                        self.agent_action()
            self.draw()
            clock.tick(60)
        pygame.quit()
if __name__ == "__main__":
    world = WumpusWorld()
    gui = WumpusGUI(world)
    gui.run()
    gui.run()
