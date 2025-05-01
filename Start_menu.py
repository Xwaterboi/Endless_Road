import pygame
import sys
from pygame import mixer

class MenuScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        #pygame.display.set_caption("Road Runner")
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (150, 150, 150)
        self.BLUE = (0, 102, 204)
        self.GREEN = (0, 153, 0)
        self.RED = (250, 0, 0)
        self.YELLOW = (255, 255, 0)
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.option_font = pygame.font.SysFont('Arial', 28)
        self.info_font = pygame.font.SysFont('Arial', 20)
        
        # Menu state
        self.difficulty = 'Normal'  # Easy, Normal, Hard
        self.agent_type = 'AI'  # AI, Human
        self.selected_option = 0  # 0: Difficulty, 1: Agent, 2: Start
        self.menu_options = ['Difficulty', 'Agent', 'Start Game']
        
        # Store button positions for touch support
        self.difficulty_buttons = []  # Will store rects for Easy, Normal, Hard buttons
        self.agent_buttons = []       # Will store rects for AI, Human buttons
        self.start_button = None      # Will store rect for Start Game button
        
        # Load sound effects (optional)
        # try:
        #     mixer.init()
        #     self.select_sound = mixer.Sound('assets/select.wav')
        #     self.confirm_sound = mixer.Sound('assets/confirm.wav')
        #     self.sound_loaded = True
        # except:
        self.sound_loaded = False
            
        self.car_image = pygame.image.load('pics/car.png').convert_alpha()
        self.bg_loaded = False
        
    def draw_text(self, text, font, color, x, y, center=True):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)
        
    def draw_button(self, text, x, y, width, height, selected=False):
        color = self.BLUE if selected else self.GRAY
        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, color, button_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.WHITE, button_rect, 2, border_radius=10)
        self.draw_text(text, self.option_font, self.WHITE, x + width // 2, y + height // 2)
        return button_rect
        
    def draw_selector(self, option, x, y, width, selected=False):
        button_rects = []
        
        if option == 'Difficulty':
            difficulties = ['Easy', 'Normal', 'Hard']
            for i, diff in enumerate(difficulties):
                button_x = x + i * (width // 3)
                button_w = width // 3 - 10
                color = self.GREEN if diff == 'Easy' else self.BLUE if diff == 'Normal' else self.RED
                button_rect = pygame.Rect(button_x, y, button_w, 40)
                
                if diff == self.difficulty:
                    pygame.draw.rect(self.screen, color, button_rect, border_radius=5)
                    pygame.draw.rect(self.screen, self.WHITE, button_rect, 2, border_radius=5)
                else:
                    pygame.draw.rect(self.screen, self.GRAY, button_rect, border_radius=5)
                    pygame.draw.rect(self.screen, self.WHITE, button_rect, 1, border_radius=5)
                    
                self.draw_text(diff, self.option_font, self.WHITE, 
                               button_x + button_w // 2, y + 20)
                button_rects.append((button_rect, diff))
                
        elif option == 'Agent':
            agents = ['AI', 'Human']
            for i, agent in enumerate(agents):
                button_x = x + i * (width // 2)
                button_w = width // 2 - 10
                color = self.BLUE if agent == self.agent_type else self.GRAY
                button_rect = pygame.Rect(button_x, y, button_w, 40)
                
                if agent == self.agent_type:
                    pygame.draw.rect(self.screen, color, button_rect, border_radius=5)
                    pygame.draw.rect(self.screen, self.WHITE, button_rect, 2, border_radius=5)
                else:
                    pygame.draw.rect(self.screen, self.GRAY, button_rect, border_radius=5)
                    pygame.draw.rect(self.screen, self.WHITE, button_rect, 1, border_radius=5)
                
                self.draw_text(agent, self.option_font, self.WHITE, 
                               button_x + button_w // 2, y + 20)
                button_rects.append((button_rect, agent))
        
        return button_rects
    
    def draw_menu(self):
        # Draw background
        if self.bg_loaded:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            # Gradient background as fallback
            for y in range(self.height):
                color_value = int(y / self.height * 100)
                color = (0, 30 + color_value, 60 + color_value)
                pygame.draw.line(self.screen, color, (0, y), (self.width, y))
            
            # Road pattern in background
            for y in range(0, self.height, 40):
                pygame.draw.rect(self.screen, (80, 80, 80), (self.width//2 - 40, y, 80, 30))
                
        # Title with shadow effect
        self.draw_text("Endless Road", self.title_font, self.BLACK, self.width//2 + 3, 103)
        self.draw_text("Endless Road", self.title_font, self.RED, self.width//2, 100)
        
       
        car_width, car_height = 80, 120
        car_scaled = pygame.transform.scale(self.car_image, (car_width, car_height))
        self.screen.blit(car_scaled, (self.width//2 - car_width//2, 160))
        
        # Options
        option_y = 300
        
        # Difficulty option
        option_x = self.width // 2 - 150
        self.draw_text("DIFFICULTY:", self.option_font, self.WHITE, option_x, option_y, False)
        self.difficulty_buttons = self.draw_selector('Difficulty', option_x, option_y + 40, 300, self.selected_option == 0)
        
        # Agent option
        option_y += 120
        self.draw_text("AGENT TYPE:", self.option_font, self.WHITE, option_x, option_y, False)
        self.agent_buttons = self.draw_selector('Agent', option_x, option_y + 40, 300, self.selected_option == 1)
        
        # Start game button
        option_y += 120
        start_button_width = 200
        start_button_x = self.width // 2 - start_button_width // 2
        self.start_button = self.draw_button("START GAME", start_button_x, option_y, start_button_width, 50, 
                            self.selected_option == 2)
        
        # Instructions
        instructions = "Use arrow keys or touch to navigate"
        self.draw_text(instructions, self.info_font, self.WHITE, self.width // 2, self.height - 40)
        
        # Difficulty info
        diff_info = {
            'Easy': "Few obstacles, easy to pick up coins,slow",
            'Normal': "Balanced gameplay",
            'Hard': "High obstacle density, fewer coins,fast"
        }
        
        self.draw_text(diff_info[self.difficulty], self.info_font, self.WHITE, 
                      self.width // 2, option_y - 30)
    
    def handle_touch(self, pos):
        # Check if difficulty buttons were clicked
        for button, difficulty in self.difficulty_buttons:
            if button.collidepoint(pos):
                self.difficulty = difficulty
                self.selected_option = 0
                return {'action': 'none'}
        
        # Check if agent buttons were clicked
        for button, agent in self.agent_buttons:
            if button.collidepoint(pos):
                self.agent_type = agent
                self.selected_option = 1
                return {'action': 'none'}
        
        # Check if start button was clicked
        if self.start_button and self.start_button.collidepoint(pos):
            self.selected_option = 2
            return {
                'action': 'start',
                'difficulty': self.difficulty,
                'agent_type': self.agent_type
            }
            
        return {'action': 'none'}
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return {'action': 'quit'}
            
            # Touch/mouse input handling    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return self.handle_touch(event.pos)
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % 3
                    
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % 3
                    
                elif event.key == pygame.K_LEFT:
                    if self.selected_option == 0:  # Difficulty
                        if self.difficulty == 'Normal':
                            self.difficulty = 'Easy'
                        elif self.difficulty == 'Hard':
                            self.difficulty = 'Normal'
                    elif self.selected_option == 1:  # Agent
                        self.agent_type = 'AI'
                        
                elif event.key == pygame.K_RIGHT:
                    if self.selected_option == 0:  # Difficulty
                        if self.difficulty == 'Easy':
                            self.difficulty = 'Normal'
                        elif self.difficulty == 'Normal':
                            self.difficulty = 'Hard'
                    elif self.selected_option == 1:  # Agent
                        self.agent_type = 'Human'
                        
                elif event.key == pygame.K_RETURN:
                    if self.selected_option == 2:  # Start Game
                        return {
                            'action': 'start',
                            'difficulty': self.difficulty,
                            'agent_type': self.agent_type
                        }
                        
                elif event.key == pygame.K_ESCAPE:
                    return {'action': 'quit'}
                    
        return {'action': 'none'}
    
    def run(self):
        running = True
        clock = pygame.time.Clock()
        
        while running:
            self.screen.fill(self.BLACK)
            self.draw_menu()
            pygame.display.flip()
            
            result = self.handle_events()
            
            if result['action'] == 'quit':
                return None
            elif result['action'] == 'start':
                return result
            
            clock.tick(60)

if __name__ == "__main__":
    # Test the menu screen independently
    pygame.init()
    menu = MenuScreen(400, 800)
    result = menu.run()
    print(result)
    pygame.quit()
    sys.exit()