import tkinter as tk
from PIL import ImageColor, ImageTk, Image
from tkinter import ttk
import random
# nvm did not figure out how to get both main and tests to work (requires no ., tests requires .)
from .settings import Settings

move_size = 10 # pixels

class RandomSnake(tk.Canvas): # self is Canvas object
    '''
    A small snake game, where any key press randomizes the 
    direction that your snake heads in.
    '''

    def __init__(self, master):
        # set up Canvas (container for all objects)
        super().__init__(
            master, width=500, height=500, background="darkgreen", highlightthickness=0
        )
        # is defining this necessary?
        mainframe = ttk.Frame(self, padding="3 3 12 12")

        self.master = master
        self.master.settings = {"speed": 50}
        self.master.color_settings = {"color": "yellow"}
        self.wait_for_settings()

        # initialize
        initial_x, initial_y = random.randint(100, 400), random.randint(100, 400) # spawn within center area
        self.snake_positions = [(initial_x, initial_y), (initial_x - 20, initial_y), (initial_x - 40, initial_y)] # positions of three segments
        self.apples = []
        self.apple_positions = []

   
        
        # set up game loop
        self.direction = "right"
        #self.bind_all("<Key>", self.move_random) # listens for any key press too annoying
        self.bind('space>',   self.move_random) 
        self.score = 0
        
        self.pack()

        self.after(100, self.perform_actions)

    def draw(self):
        self.delete("snake")
        for x, y in self.snake_positions:
            self.create_rectangle(x, y, x + 10, y + 10, fill=self.color, tag="snake")

    def spawn_apples(self,num):
        for i in range(num):
            x = random.randint(0, 49)*10
            y = random.randint(0,49)*10
            apple = self.create_oval(x, y, x+10, y+10, fill='red')
            self.apples.append(apple)
            self.apple_positions.append((x,y))

    def check_apple(self):
        head_x, head_y = self.snake_positions[0]
        for i, (apple_x, apple_y) in enumerate(self.apple_positions):
            if apple_x <= head_x < apple_x + 15 and apple_y <= head_y < apple_y + 15:
                self.delete(self.apples.pop(i))
                self.apple_positions.pop(i)
                self.score += 10
                return True
        return False

    def move_snake(self):
        '''
        Defines movement for the snake.
        '''
        head_x, head_y = self.snake_positions[0]

        if self.direction == "left":
            new_head_pos = (head_x - move_size, head_y)
        elif self.direction == "right":
            new_head_pos = (head_x + move_size, head_y)
        elif self.direction == "down":
            new_head_pos = (head_x, head_y + move_size)
        elif self.direction == "up":
            new_head_pos = (head_x, head_y - move_size)

        if self.check_apple():
            self.snake_positions.insert(0,new_head_pos)
        else:
            # replace head with body
            self.snake_positions = [new_head_pos] + self.snake_positions[:-1]

        self.draw()

    def move_random(self, event):
        ''' 
        Randomizes the snake's movement. 
        '''
        all_directions = ["up", "down", "left", "right"]
        opposites = ({"up", "down"}, {"left", "right"})

        # make next direction != current direction
        all_directions.remove(self.direction)
        random_direction = random.choice(all_directions)
        all_directions.append(self.direction)

        if ( 
            random_direction in all_directions 
            and {random_direction, self.direction} not in opposites # make sure snake doesn't collide with itself
        ):
            self.direction = random_direction

    def wait_for_settings(self):
        settings_window = Settings(self.master)
        self.master.wait_window(settings_window)
        self.speed(self.master.settings["speed"])
        try: #if input is a valid color, then all clear!
            ImageColor.getrgb(self.master.color_settings["color"])#check if valid
            self.color = self.master.color_settings["color"]#set!
        except: #else, randomize!
            #sorry for how gross and long this is, but needs must
            self.color = "#" + '{:02x}'.format(random.randint(0, 255)) + '{:02x}'.format(random.randint(0, 255)) + '{:02x}'.format(random.randint(0, 255))
        
        self.start_game()

    def speed(self, val):
        self.game_speed = int((1000 / val) * 10)

    #color change section
    # What does this method actually do? Removing it doesn't break anything
    def color(self, val):
        self.color = "yellow"
    
    def perform_actions(self):
        ''' 
        Performs game loop's actions. 
        '''
        if self.check_collisions(): 
            self.end_game()
            return
        self.move_snake()

        self.after(self.game_speed, self.perform_actions) # move snake according to speed setting


    def check_collisions(self):
        ''' 
        Returns a bool that checks for collisions. 
        '''
        head_x, head_y = self.snake_positions[0]

        # borders of play and self-collision
        return (head_x not in range(20, 480) or head_y not in range(20,480) or (head_x, head_y) in self.snake_positions[1:])

    def apple_window(self):
        self.n = tk.StringVar() 
        new_window = tk.Toplevel(self.master)
        new_window.title("Apples")
        new_window.geometry("300x200")
        # Speed
        ttk.Label(new_window, text="Enter apples to spawn (1-10):").pack(pady=5)
        apple_entry = ttk.Entry(new_window, textvariable=self.n)
        apple_entry.pack()
        # button
        start_button = tk.Button(new_window, text="Spawn", command=lambda: self.spawn_apples(int(self.n.get())), bg="lightgray", fg="black")
        start_button.pack(pady=10)

    def start_game(self):

        self.snake_positions = [(250, 250), (240, 250), (230, 250)]
        self.direction = "right"
        self.bind_all("<Key>", self.move_random)
        self.apples = []
        self.apple_window()
        self.pack()
        self.after(self.game_speed, self.perform_actions)

    def end_game(self):
        '''Ends the game and displays the Game Over screen.'''
        self.delete(self.find_withtag("snake"))
        self.delete(tk.ALL)  # Clear canvas
        self.create_text(
            250, 250,
            text="Game over!\nMay the RNG gods bestow\nfavor upon you next time.",
            fill="white",
            font=("", 20),
            tag="game_over")
        self.after_cancel(self.perform_actions)



