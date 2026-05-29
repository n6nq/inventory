import curses

def main(stdscr):
    # Sample data
    items = [f"Item {i}" for i in range(1, 31)]  # 30 items
    selected = 0
    start_idx = 0
    max_lines = curses.LINES - 2

    curses.curs_set(0)
    stdscr.keypad(True)

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Use ↑ ↓ to scroll, 'q' to quit")

        # Calculate visible slice
        end_idx = min(start_idx + max_lines, len(items))
        for idx, item in enumerate(items[start_idx:end_idx]):
            line = idx + 1
            if start_idx + idx == selected:
                stdscr.addstr(line, 0, f"> {item}", curses.A_REVERSE)
            else:
                stdscr.addstr(line, 0, f"  {item}")

        key = stdscr.getch()

        if key == ord("q"):
            break
        elif key == curses.KEY_DOWN and selected < len(items) - 1:
            selected += 1
            if selected >= start_idx + max_lines:
                start_idx += 1
        elif key == curses.KEY_UP and selected > 0:
            selected -= 1
            if selected < start_idx:
                start_idx -= 1

        stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(main)
