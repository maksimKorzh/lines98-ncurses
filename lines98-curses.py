import random, curses, sys

board = [0] * 121
next_pieces = []
#pieces = ['.', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'X']
pieces = ['.', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'X']
piece_colors = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}
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

def generate_next_pieces():
  global next_pieces
  next_pieces.clear()
  empty_indexes = [i for i, v in enumerate(board) if v == 0]
  for _ in range(3):
    if not empty_indexes: break
    index = random.choice(empty_indexes)
    empty_indexes.remove(index)
    color = random.randint(1,7)
    next_pieces.append({'color': color, 'index': index})
  if not empty_indexes: return 0
  else: return 1

def make_move(src, dst):
  if dst == src: return 0
  def to_index(pos):
    col = ord(pos[0].lower()) - ord('a') + 1
    row = 10-int(pos[1])
    return row * 11 + col
  src_index = to_index(src)
  dst_index = to_index(dst)
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
  stdscr.addstr(board_start_y-3, board_start_x+4, 'Next: ' + ''.join([pieces[p['color']] for p in next_pieces]))
  stdscr.addstr(board_start_y-2, board_start_x+2, ' Score: ' + str(score))
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
    stdscr.clrtoeol()
    stdscr.refresh()

def handle_command(stdscr):
  global cur_row, cur_col, selected
  key = -1
  while key == -1: key = stdscr.getch()
  if key == ord('Q'): return 'exit'
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
        remove_lines()
        selected = None
        if not generate_next_pieces():
          for piece in next_pieces:
            board[piece['index']] = piece['color']
          render_board(stdscr)
          stdscr.addstr(board_start_y + 11, board_start_x+4, 'Game Over')
          stdscr.refresh()
          key = -1
          while key == -1: key = stdscr.getch()
          return 'exit'
        for piece in next_pieces:
          board[piece['index']] = piece['color']
      else: selected = None
  return 'move'

def main(stdscr):
  curses.use_default_colors()
  curses.init_pair(1, curses.COLOR_RED, -1)
  curses.init_pair(2, curses.COLOR_GREEN, -1)
  curses.init_pair(3, curses.COLOR_YELLOW, -1)
  curses.init_pair(4, curses.COLOR_BLUE, -1)
  curses.init_pair(5, curses.COLOR_MAGENTA, -1)
  curses.init_pair(6, curses.COLOR_CYAN, -1)
  curses.init_pair(7, curses.COLOR_WHITE, -1)
  curses.init_pair(8, curses.COLOR_BLACK, -1)
  curses.curs_set(0)
  curses.raw(1)
  stdscr.nodelay(1)
  stdscr.keypad(1)
  curses.noecho()
  init_board()
  generate_next_pieces()
  for piece in next_pieces:
    board[piece['index']] = piece['color']
  while True:
    render_board(stdscr)
    if handle_command(stdscr) == 'exit': break

curses.wrapper(main)
