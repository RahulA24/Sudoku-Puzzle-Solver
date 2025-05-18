import tkinter as tk
from tkinter import messagebox, ttk
import random, copy, time, platform

# Cross-platform beep
if platform.system() == "Windows":
    import winsound
    def beep(): winsound.Beep(1000, 150)
else:
    def beep(): print("\a")

# ---- Solver Logic ----
def solve_board(board):
    empty_pos = find_empty(board)
    if not empty_pos:
        return True
    row_idx, col_idx = empty_pos
    for num in range(1, 10):
        if is_valid(board, num, (row_idx, col_idx)):
            board[row_idx][col_idx] = num
            if solve_board(board):
                return True
            board[row_idx][col_idx] = 0
    return False

def find_empty(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None

def is_valid(board, num, pos):
    r, c = pos
    if any(board[r][j] == num and j != c for j in range(9)): return False
    if any(board[i][c] == num and i != r for i in range(9)): return False
    box_x, box_y = c // 3, r // 3
    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if board[i][j] == num and (i, j) != pos:
                return False
    return True

def generate_full_board():
    full = [[0]*9 for _ in range(9)]
    solve_board(full)
    return full

def remove_cells(board, difficulty="Medium"):
    puzzle = copy.deepcopy(board)
    attempts = {"Easy": 30, "Medium": 40, "Hard": 55}.get(difficulty, 40)
    while attempts > 0:
        r, c = random.randint(0, 8), random.randint(0, 8)
        if puzzle[r][c] != 0:
            puzzle[r][c] = 0
            attempts -= 1
    return puzzle

def validate_input(char):
    return char.isdigit() and 1 <= int(char) <= 9

def is_valid_input(board):
    for r in range(9):
        for c in range(9):
            num = board[r][c]
            if num != 0:
                board[r][c] = 0
                if not is_valid(board, num, (r, c)):
                    return False
                board[r][c] = num
    return True

# ---- GUI ----
root = tk.Tk()
root.title("Sudoku Solver")
initial_board = []
entries = []
start_time = 0
vcmd = (root.register(validate_input), '%S')

timer_label = tk.Label(root, text="Time: 00:00", font=('Arial', 12))
timer_label.grid(row=11, column=0, columnspan=3)

def update_timer():
    global start_time
    if start_time:
        elapsed = int(time.time() - start_time)
        mins, secs = divmod(elapsed, 60)
        timer_label.config(text=f"Time: {mins:02}:{secs:02}")
        root.after(1000, update_timer)

def load_board_to_gui(board):
    for r in range(9):
        for c in range(9):
            entries[r][c].config(state='normal', fg="black")
            entries[r][c].delete(0, tk.END)
            val = board[r][c]
            if val != 0:
                entries[r][c].insert(0, str(val))
                entries[r][c].config(state='readonly', readonlybackground="light gray")

def get_board_from_gui():
    return [[int(entries[r][c].get()) if entries[r][c].get().isdigit() else 0 for c in range(9)] for r in range(9)]

def validate_and_highlight(event=None):
    board = get_board_from_gui()
    for r in range(9):
        for c in range(9):
            entry = entries[r][c]
            val = entry.get()
            if val.isdigit():
                num = int(val)
                board[r][c] = 0
                if not is_valid(board, num, (r, c)):
                    entry.config(bg="tomato")
                    beep()
                else:
                    entry.config(bg="white")
                    if initial_board[r][c] != 0:
                        entry.config(bg="light gray")
                board[r][c] = num
            else:
                entry.config(bg="white")

def solve_from_gui():
    board = get_board_from_gui()
    if not is_valid_input(board):
        messagebox.showerror("Invalid Input", "The board has invalid entries!")
        return
    if solve_board(board):
        for r in range(9):
            for c in range(9):
                if initial_board[r][c] == 0:
                    entries[r][c].delete(0, tk.END)
                    entries[r][c].insert(0, str(board[r][c]))
                    entries[r][c].config(fg="blue")
    else:
        messagebox.showerror("No Solution", "The Sudoku puzzle cannot be solved.")

def clear_board():
    for r in range(9):
        for c in range(9):
            entries[r][c].config(state='normal', fg="black")
            entries[r][c].delete(0, tk.END)
            if initial_board[r][c] != 0:
                entries[r][c].insert(0, str(initial_board[r][c]))
                entries[r][c].config(state='readonly', readonlybackground="light gray")

def new_puzzle():
    global initial_board, start_time
    full_board = generate_full_board()
    initial_board = remove_cells(full_board, difficulty_var.get())
    load_board_to_gui(initial_board)
    start_time = time.time()
    update_timer()

def give_hint():
    board = get_board_from_gui()
    solution = copy.deepcopy(board)
    if not solve_board(solution):
        messagebox.showerror("No Solution", "Board cannot be solved!")
        return
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                entries[r][c].delete(0, tk.END)
                entries[r][c].insert(0, str(solution[r][c]))
                entries[r][c].config(fg="green")
                return

# Draw Grid
canvas = tk.Canvas(root, width=450, height=450)
canvas.grid(row=0, column=0, columnspan=9)
cell_size = 50

for i in range(10):
    width = 3 if i % 3 == 0 else 1
    canvas.create_line(0, i * cell_size, 450, i * cell_size, width=width, fill="black")
    canvas.create_line(i * cell_size, 0, i * cell_size, 450, width=width, fill="black")

for r in range(9):
    row_entries = []
    for c in range(9):
        entry = tk.Entry(root, width=2, font=('Arial', 18), justify='center',
                         validate="key", validatecommand=vcmd, bg="white")
        entry.place(x=c * 50 + 2, y=r * 50 + 2, width=46, height=46)
        entry.bind("<KeyRelease>", validate_and_highlight)
        row_entries.append(entry)
    entries.append(row_entries)

# Controls
difficulty_var = tk.StringVar(value="Medium")
difficulty_label = tk.Label(root, text="Difficulty:", font=('Arial', 12))
difficulty_label.grid(row=11, column=3)
difficulty_menu = ttk.Combobox(root, textvariable=difficulty_var, values=["Easy", "Medium", "Hard"], width=8)
difficulty_menu.grid(row=11, column=4)

new_btn = tk.Button(root, text="New Puzzle", font=('Arial', 12), command=new_puzzle)
new_btn.grid(row=10, column=0, columnspan=2)

solve_btn = tk.Button(root, text="Solve", font=('Arial', 12), command=solve_from_gui)
solve_btn.grid(row=10, column=2, columnspan=2)

clear_btn = tk.Button(root, text="Clear", font=('Arial', 12), command=clear_board)
clear_btn.grid(row=10, column=4, columnspan=2)

hint_btn = tk.Button(root, text="Hint", font=('Arial', 12), command=give_hint)
hint_btn.grid(row=10, column=6, columnspan=2)

check_btn = tk.Button(root, text="Check", font=('Arial', 12), command=validate_and_highlight)
check_btn.grid(row=10, column=8)

root.mainloop()
