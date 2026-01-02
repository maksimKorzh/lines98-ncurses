import random, curses, sys
from copy import deepcopy

board = [0] * 121

next_pieces = []
current_pieces = []
pieces = ['.', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'X']
piece_colors = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}
cur_row, cur_col = 1, 1
board_start_y, board_start_x = 0, 0
selected = None
score = 0

def init_board():
  offboard = pieces.index('X')
  for row in range(11):
    for col in range(11):
      if row == 0 or row == 10 or col == 0 or col == 10:
        board[row * 11 + col] = offboard
      else:
        board[row * 11 + col] = 0

def generate_next_colors():
  global next_pieces
  next_pieces.clear()
  for _ in range(3):
    color = random.randint(1,7)
    next_pieces.append({'color': color, 'index': 0})

def generate_next_indexes():
  global next_pieces
  empty_indexes = [i for i, v in enumerate(board) if v == 0]
  for i in range(3):
    if not empty_indexes: break
    index = random.choice(empty_indexes)
    empty_indexes.remove(index)
    color = random.randint(1,7)
    next_pieces[i]['index'] = index
  if not empty_indexes: return 0
  else: return 1

def place_next_pieces():
  for piece in next_pieces:
    if board[piece['index']] == 0:
      board[piece['index']] = piece['color']
    else:
      empty_indexes = [i for i, v in enumerate(board) if v == 0]
      if len(empty_indexes):
        index = random.choice(empty_indexes)
        board[index] = piece['color']

def pos_to_index(pos):
  col = ord(pos[0].lower()) - ord('a') + 1
  row = 10-int(pos[1])
  return row * 11 + col

def index_to_pos(idx):
  row = idx // 11
  col = idx % 11
  if not (1 <= row <= 9 and 1 <= col <= 9): return None
  file = chr(ord('a') + (col - 1))
  rank = str(10 - row)
  return file + rank

def make_move(src, dst):
  if dst == src: return 0
  src_index = pos_to_index(src)
  dst_index = pos_to_index(dst)
  if board[src_index] == 0: return 0
  visited = set()
  queue = [src_index]
  while queue:
    current = queue.pop(0)
    if current == dst_index:
      board[dst_index] = board[src_index]
      board[src_index] = 0
      return 1
    visited.add(current)
    row = current // 11
    col = current % 11
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
      nr, nc = row + dr, col + dc
      ni = nr * 11 + nc
      if ni not in visited and board[ni] == 0:
        queue.append(ni)
  return 0

def remove_lines():
  global score
  removed = set()
  directions = [(0,1), (1,0), (1,1), (-1,1)]
  for row in range(1, 10):
    for col in range(1, 10):
      index = row * 11 + col
      color = board[index]
      if color == 0: continue
      for dr, dc in directions:
        line = [index]
        r, c = row + dr, col + dc
        while 1 <= r <= 9 and 1 <= c <= 9:
          ni = r * 11 + c
          if board[ni] == color:
            line.append(ni)
            r += dr
            c += dc
          else:
            break
        r, c = row - dr, col - dc
        while 1 <= r <= 9 and 1 <= c <= 9:
          ni = r * 11 + c
          if board[ni] == color:
            line.append(ni)
            r -= dr
            c -= dc
          else:
            break
        if len(line) >= 5:
          removed.update(line)
  for idx in removed:
    board[idx] = 0
    score += 1
  return len(removed)

def render_board(stdscr):
  global board_start_y, board_start_x
  height, width = stdscr.getmaxyx()
  board_start_y = height//2 - 4
  board_start_x = width//2 - 9
  stdscr.addstr(board_start_y-4, board_start_x+4, 'Next: ')
  cx = board_start_x+10
  for piece in next_pieces:
    ch = pieces[piece['color']]
    color = curses.color_pair(piece_colors[piece['color']])
    stdscr.addstr(board_start_y-4, cx, ch, color)
    cx += 1
  stdscr.addstr(board_start_y-3, board_start_x+2, ' Score: ' + str(score))
  stdscr.clrtoeol()
  stdscr.addstr(board_start_y-2, board_start_x-1, ' Selected: ')
  if selected is not None:
    selected_piece = board[selected[0]*11+selected[1]]
    color = curses.color_pair(piece_colors[selected_piece])
    stdscr.addstr(board_start_y-2, board_start_x+10, pieces[selected_piece], color)
  else:
    stdscr.addstr(board_start_y-2, board_start_x+10, 'None')
  stdscr.clrtoeol()
  for row in range(1,10):
    for col in range(1,10):
      idx = row*11 + col
      ch = pieces[board[idx]]
      color = curses.color_pair(piece_colors[board[idx]]) if board[idx] != 0 else curses.A_NORMAL
      dark = curses.A_DIM if ch == '.' else 0
      if row == cur_row and col == cur_col:
        stdscr.addch(board_start_y + row-1, board_start_x + (col-1)*2, ch, color | curses.A_REVERSE)
      else:
        stdscr.addch(board_start_y + row-1, board_start_x + (col-1)*2, ch, color | dark)
        for piece in next_pieces:
          if idx == piece['index']:
            color = curses.color_pair(piece_colors[piece['color']])
            stdscr.addch(board_start_y + row-1, board_start_x + (col-1)*2, 'o', color)
    stdscr.clrtoeol()
  stdscr.addstr(board_start_y+10, board_start_x+2, 'New:    N')
  stdscr.addstr(board_start_y+11, board_start_x+2, 'Move:   hjkl')
  stdscr.addstr(board_start_y+12, board_start_x+2, 'Select: SPACE')
  stdscr.refresh()

def handle_command(stdscr):
  global cur_row, cur_col, selected
  key = -1
  while key == -1: key = stdscr.getch()
  if key == ord('Q'): return 'exit'
  elif key == ord('N'): new_game()
  elif key == ord('k'): cur_row = max(1, cur_row-1)
  elif key == ord('j'): cur_row = min(9, cur_row+1)
  elif key == ord('h'): cur_col = max(1, cur_col-1)
  elif key == ord('l'): cur_col = min(9, cur_col+1)
  elif key == ord(' '):
    if not selected:
      selected = (cur_row, cur_col)
    else:
      src_pos = chr(ord('a') + selected[1]-1) + str(10 - selected[0])
      dst_pos = chr(ord('a') + cur_col-1) + str(10 - cur_row)
      if make_move(src_pos, dst_pos):
        selected = None
        if not remove_lines():
          current_pieces = deepcopy(next_pieces)
          place_next_pieces()
          remove_lines()
          generate_next_colors()
          generate_next_indexes()
          if not generate_next_indexes():
            place_next_pieces()
            render_board(stdscr)
            stdscr.addstr(board_start_y+4, board_start_x+4, 'Game Over')
            stdscr.refresh()
            key = -1
            while key == -1: key = stdscr.getch()
            scores = []
            with open('scores.txt') as f: scores = sorted([int(i) for i in f.read().split('\n')[:-1]], reverse=True)
            scores.append(score)
            with open('scores.txt', 'w') as f: [f.write(str(i)+'\n') for i in scores]
            stdscr.clear()
            new_game()
      else: selected = None
  return 'move'

def print_board():
  print()
  for row in range(1, 10):
    for col in range(1, 10):
      idx = row * 11 + col
      if col == 1: print(' ' + str(10-row), end=' ')
      print(' ' + str(board[idx]), end='')
    print()
  print('\n    a b c d e f g h i\n')

def generate_moves():
  moves = []
  for src in range(len(board)):
    if board[src] == 8 or board[src] == 0: continue
    for dst in range(len(board)):
      if board[dst] != 0: continue
      moves.append((index_to_pos(src), index_to_pos(dst)))
  return moves

def legal_moves():
  moves = []
  for move in generate_moves():
    old_board = deepcopy(board)
    if make_move(move[0], move[1]): moves.append(move)
    board[:] = old_board
  return moves
  
def new_game():
  global score
  score = 0
  init_board()
  generate_next_colors()
  generate_next_indexes()
  current_pieces = deepcopy(next_pieces)
  generate_next_colors()
  for piece in current_pieces:
    board[piece['index']] = piece['color']
  generate_next_indexes()

def main(stdscr):
  curses.use_default_colors()
  curses.init_pair(1, curses.COLOR_RED, -1)
  curses.init_pair(2, curses.COLOR_GREEN, -1)
  curses.init_pair(3, curses.COLOR_YELLOW, -1)
  curses.init_pair(4, curses.COLOR_BLUE, -1)
  curses.init_pair(5, curses.COLOR_MAGENTA, -1)
  curses.init_pair(6, curses.COLOR_CYAN, -1)
  curses.init_pair(7, curses.COLOR_WHITE, -1)
  curses.curs_set(0)
  curses.raw(1)
  stdscr.nodelay(1)
  stdscr.keypad(1)
  curses.noecho()
  new_game()
  while True:
    render_board(stdscr)
    if handle_command(stdscr) == 'exit': break

if __name__ == '__main__': curses.wrapper(main)
