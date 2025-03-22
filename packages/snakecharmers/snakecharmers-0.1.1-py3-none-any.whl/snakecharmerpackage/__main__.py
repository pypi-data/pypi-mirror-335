from snakecharmerpackage.random_snake import RandomSnake
import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Random Snake")
    snake = RandomSnake(root)
    root.mainloop()

if __name__ == "__main__":
    main()