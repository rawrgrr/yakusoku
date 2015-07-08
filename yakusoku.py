#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "rawrgrr"

from sys import stdin

import argparse
import curses
import json
import time

# TODO customize loading from files
# TODO create stacks of workflows
# TODO handle mouse clicks

class TaskStatus:
    TODO = 1
    DOING = 2
    DONE = 3

class TaskItem:
    def __init__(self, description, status=TaskStatus.TODO, level=0):
        self.description = description
        if status.lower() == "todo":
            self.status = TaskStatus.TODO
        elif status.lower() == "doing":
            self.status = TaskStatus.DOING
        elif status.lower() == "done":
            self.status = TaskStatus.DONE
        self.level = level

class TaskList:
    def __init__(self):
        self.selected_task = -1
        self.tasks = []

    def __init__(self, tasks):
        if len(tasks) >= 0:
            self.selected_task = 0
            self.tasks = tasks
            self.statuses = []
            self.levels = []
            for i in xrange(len(self.tasks)):
                self.statuses.append(TaskStatus.TODO)
        else:
            return self.__init__()

    def __init__(self, json_file_name):
        self.selected_task = 0
        with open(json_file_name, 'r') as tasks_json_file:
            json_data = json.load(tasks_json_file)

        self.tasks = []

        for item in json_data:
            description = item["description"]
            status = item["status"]
            level = item["level"]
            self.tasks.append(TaskItem(description, status, level))

    def add_task(self, description, status=TaskStatus.TODO, level=0):
        self.tasks.append(TaskItem(description, status, level))

    def select(self, index):
        if index < 0:
            self.selected_task = 0
        elif index >= len(self.tasks):
            self.selected_task = len(self.tasks) - 1
        else:
            self.selected_task = index

    def can_select_next_task(self):
        return self.selected_task < len(self.tasks) - 1

    def can_select_prev_task(self):
        return self.selected_task > 0

    def select_next_task(self):
        if self.can_select_next_task():
            self.selected_task += 1

    def select_prev_task(self):
        if self.can_select_prev_task():
            self.selected_task -= 1

    def select_first_task(self):
        self.selected_task = 0

    def select_last_task(self):
        self.selected_task = len(self.tasks) - 1

    def select_middle_task(self):
        self.selected_task = len(self.tasks) / 2

    def is_selected_task_todo(self):
        return self.tasks[self.selected_task].status == TaskStatus.TODO

    def is_selected_task_doing(self):
        return self.tasks[self.selected_task].status == TaskStatus.DOING

    def is_selected_task_done(self):
        return self.tasks[self.selected_task].status == TaskStatus.DONE

    def transition_selected_task(self):
        if self.is_selected_task_todo():
            self.tasks[self.selected_task].status = TaskStatus.DOING
        elif self.is_selected_task_doing():
            self.tasks[self.selected_task].status = TaskStatus.DONE

    def untransition_selected_task(self):
        if self.is_selected_task_done():
            self.tasks[self.selected_task].status = TaskStatus.DOING
        elif self.is_selected_task_doing():
            self.tasks[self.selected_task].status = TaskStatus.TODO

    def decrement_selected_task_level(self):
        if 0 <= self.selected_task < len(self.tasks):
            current_level = self.tasks[self.selected_task].level
            if current_level > 0:
                self.tasks[self.selected_task].level -= 1

    def increment_selected_task_level(self):
        if 0 <= self.selected_task < len(self.tasks):
            self.tasks[self.selected_task].level += 1

    def size(self):
        return len(self.tasks)

OFFSET_FOR_TOP = 2
OFFSET_FOR_BOT = -1
LEFT_PADDING = 8 * ' '

list_position = 0
selected_position = 0
show_help = False

if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser(
            description="CLI TODO List Manager",
            epilog="The json file needs to be structured like:"
            )
    parser.add_argument('json_file', metavar="filename", help="Tasks in a json file")
    parser.add_argument('-t', '--indentation', metavar="spaces", type=int, default=4, help="Number of spaces per level of indentation")
    parser.add_argument('-i', '--invert', action='store_true', help="Invert colors")
    parser.add_argument('-s', '--scroll-lines', metavar="lines", type=int, default=10, help="Number of lines to move per scroll")
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug mode")
    args = parser.parse_args()

    selected_task_list = TaskList(args.json_file)
    INVERTED = args.invert

    try:
        # initial curses window setup
        stdscr = curses.initscr()
        curses.start_color()

        win1 = stdscr.derwin(stdscr.getmaxyx()[0], stdscr.getmaxyx()[1], 0, 0)
        #win1 = stdscr.derwin(len(tasks) + 5, stdscr.getmaxyx()[1], 0, 0)
        #win2 = win1.derwin(len(tasks) + 5, stdscr.getmaxyx()[1], 0, 0)

        selected_window = win1

        # setup
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        selected_window.scrollok(0)
        selected_window.keypad(1)
        selected_window.nodelay(1)

        # define color_pairs for later usage
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK)

        # color constants for easy reference
        NORMAL  = curses.color_pair(0)
        RED     = curses.color_pair(1)
        GREEN   = curses.color_pair(2)
        YELLOW  = curses.color_pair(3)
        BLUE    = curses.color_pair(4)
        MAGENTA = curses.color_pair(5)
        CYAN    = curses.color_pair(6)
        WHITE   = curses.color_pair(7)

        # standout variants
        STANDOUT_RED     = curses.color_pair(1) | curses.A_STANDOUT
        STANDOUT_GREEN   = curses.color_pair(2) | curses.A_STANDOUT
        STANDOUT_YELLOW  = curses.color_pair(3) | curses.A_STANDOUT
        STANDOUT_BLUE    = curses.color_pair(4) | curses.A_STANDOUT
        STANDOUT_MAGENTA = curses.color_pair(5) | curses.A_STANDOUT
        STANDOUT_CYAN    = curses.color_pair(6) | curses.A_STANDOUT
        STANDOUT_WHITE   = curses.color_pair(7) | curses.A_STANDOUT

        # bold variants
        BOLD_RED     = curses.color_pair(1) | curses.A_BOLD
        BOLD_GREEN   = curses.color_pair(2) | curses.A_BOLD
        BOLD_YELLOW  = curses.color_pair(3) | curses.A_BOLD
        BOLD_BLUE    = curses.color_pair(4) | curses.A_BOLD
        BOLD_MAGENTA = curses.color_pair(5) | curses.A_BOLD
        BOLD_CYAN    = curses.color_pair(6) | curses.A_BOLD
        BOLD_WHITE   = curses.color_pair(7) | curses.A_BOLD

        # bold standout variants
        BOLD_STANDOUT_RED     = curses.color_pair(1) | curses.A_BOLD | curses.A_STANDOUT
        BOLD_STANDOUT_GREEN   = curses.color_pair(2) | curses.A_BOLD | curses.A_STANDOUT
        BOLD_STANDOUT_YELLOW  = curses.color_pair(3) | curses.A_BOLD | curses.A_STANDOUT
        BOLD_STANDOUT_BLUE    = curses.color_pair(4) | curses.A_BOLD | curses.A_STANDOUT
        BOLD_STANDOUT_MAGENTA = curses.color_pair(5) | curses.A_BOLD | curses.A_STANDOUT
        BOLD_STANDOUT_CYAN    = curses.color_pair(6) | curses.A_BOLD | curses.A_STANDOUT
        BOLD_STANDOUT_WHITE   = curses.color_pair(7) | curses.A_BOLD | curses.A_STANDOUT

        # main printing function
        def print_row(row, message, color):
            spaces = " " * selected_window.getmaxyx()[1]
            selected_window.addnstr(row, 0, spaces, selected_window.getmaxyx()[1], color)
            selected_window.addnstr(row, 0, message, selected_window.getmaxyx()[1], color)

        def print_task_row(task_list, row, offset):
            task_status = task_list.tasks[row].status
            row_offset = row + OFFSET_FOR_TOP - offset
            level = task_list.tasks[row].level
            description = task_list.tasks[row].description
            selected = task_list.selected_task == row

            if INVERTED:
                if task_status == TaskStatus.TODO:
                    status = "TODO    "
                    standout_color = STANDOUT_RED
                    color = RED
                elif task_status == TaskStatus.DOING:
                    status = "DOING   "
                    standout_color = STANDOUT_YELLOW
                    color = YELLOW
                elif task_status == TaskStatus.DONE:
                    status = "DONE    "
                    standout_color = STANDOUT_GREEN
                    color = GREEN
                text = LEFT_PADDING + status + (level * args.indentation) * " " + description
                print_row(row_offset, text, standout_color if selected else color)
            else:
                if task_status == TaskStatus.TODO:
                    status = "TODO    "
                    color = RED
                    standout_color = STANDOUT_RED
                elif task_status == TaskStatus.DOING:
                    status = "DOING   "
                    color = YELLOW
                    standout_color = STANDOUT_YELLOW
                elif task_status == TaskStatus.DONE:
                    status = "DONE    "
                    color = GREEN
                    standout_color = STANDOUT_GREEN
                text = LEFT_PADDING + status + (level * args.indentation) * " " + description
                print_row(row_offset, text, color if selected else standout_color)


        def redraw_all():
            if show_help:
                for row in xrange(selected_window.getmaxyx()[0] - 1):
                    print_row(row, "", NORMAL)
                help_texts = [
                        "",
                        "",
                        "          KEY(S)            ACTION",
                        "",
                        "          h/?               show/hide this help menu",
                        "",
                        "          j/J/<up-arrow>    down",
                        "          k/K/<down-arrow>  up",
                        "",
                        "          <space>           TODO --> DOING --> DONE",
                        "          <backspace>       DONE --> DOING --> TODO",
                        "",
                        "          H                 move to top of visible items",
                        "          M                 move to middle of visible items",
                        "          L                 move to bottom of visible items",
                        "",
                        "          g                 move and scroll to the top of the list",
                        "          G                 move and scroll to the bottom of the list",
                        "",
                        "          i                 invert colors"
                        ]
                for row, text in zip(xrange(len(help_texts)), help_texts):
                    print_row(row + OFFSET_FOR_TOP, text, NORMAL)
            else:
                # print title and status lines
                print_row(0, LEFT_PADDING + "[Demo TODO List]", STANDOUT_WHITE if INVERTED else BLUE)
                print_row(1, LEFT_PADDING + "Status  Task"   , STANDOUT_WHITE if INVERTED else MAGENTA)

                # print out help
                space_for_items = selected_window.getmaxyx()[0] - OFFSET_FOR_TOP + OFFSET_FOR_BOT
                # print out everything once
                for i in xrange(selected_task_list.size()):
                    if list_position <= i < (list_position + space_for_items):
                        print_task_row(selected_task_list, i, list_position)

                selected_window.refresh()

        redraw_all()

        # main loop
        while True:
            #key = stdin.read(1)
            key = selected_window.getch()
            disable_movement = show_help

            if key == ord(' ') and not disable_movement:
                # transition task
                prev_task = selected_task_list.selected_task
                selected_task_list.transition_selected_task()
                if selected_task_list.is_selected_task_done() and selected_task_list.can_select_next_task():
                    if selected_position == list_position + selected_window.getmaxyx()[0] - OFFSET_FOR_TOP + OFFSET_FOR_BOT - 1:
                        list_position += 1
                        redraw_all()
                    selected_position += 1
                    selected_task_list.select_next_task()
                    print_task_row(selected_task_list, prev_task, list_position)
                print_task_row(selected_task_list, selected_task_list.selected_task, list_position)

            elif (key == 127 or key == curses.KEY_DC or key == curses.KEY_BACKSPACE) and not disable_movement:
                # untransition task
                prev_task = selected_task_list.selected_task
                selected_task_list.untransition_selected_task()
                if selected_task_list.is_selected_task_todo() and selected_task_list.can_select_prev_task():
                    if selected_position == list_position:
                        list_position -= 1
                        redraw_all()
                    selected_position -= 1
                    selected_task_list.select_prev_task()
                    print_task_row(selected_task_list, prev_task, list_position)
                print_task_row(selected_task_list, selected_task_list.selected_task, list_position)

            elif key == ord('q') or key == ord('Q'):
                # quit
                break

            elif (key == ord('j') or key == curses.KEY_DOWN) and not disable_movement:
                # go down
                if selected_task_list.can_select_next_task():
                    if selected_position == list_position + selected_window.getmaxyx()[0] - OFFSET_FOR_TOP + OFFSET_FOR_BOT - 1:
                        list_position += 1
                        redraw_all()
                    selected_position += 1
                    prev_task = selected_task_list.selected_task
                    selected_task_list.select_next_task()
                    print_task_row(selected_task_list, prev_task, list_position)
                    print_task_row(selected_task_list, selected_task_list.selected_task, list_position)

            elif (key == ord('k') or key == curses.KEY_UP) and not disable_movement:
                # go up
                if selected_task_list.can_select_prev_task():
                    if selected_position == list_position:
                        list_position -= 1
                        redraw_all()
                    selected_position -= 1
                    prev_task = selected_task_list.selected_task
                    selected_task_list.select_prev_task()
                    print_task_row(selected_task_list, prev_task, list_position)
                    print_task_row(selected_task_list, selected_task_list.selected_task, list_position)

            elif (key == ord('J') or key == curses.KEY_NPAGE) and not disable_movement:
                # go down by args.scroll_lines
                prev_task = selected_task_list.selected_task
                should_redraw_all = False
                for i in xrange(args.scroll_lines):
                    if selected_task_list.can_select_next_task():
                        if selected_position == list_position + selected_window.getmaxyx()[0] - OFFSET_FOR_TOP + OFFSET_FOR_BOT - 1:
                            list_position += 1
                            should_redraw_all = True
                        selected_position += 1
                        selected_task_list.select_next_task()
                if should_redraw_all:
                    redraw_all()
                if prev_task < list_position + selected_window.getmaxyx()[0]:
                    print_task_row(selected_task_list, prev_task, list_position)
                if selected_task_list.selected_task < list_position + selected_window.getmaxyx()[0]:
                    print_task_row(selected_task_list, selected_task_list.selected_task, list_position)

            elif (key == ord('K') or key == curses.KEY_PPAGE) and not disable_movement:
                # go up by args.scroll_lines
                prev_task = selected_task_list.selected_task
                should_redraw_all = False
                for i in xrange(args.scroll_lines):
                    if selected_task_list.can_select_prev_task():
                        if selected_position == list_position:
                            list_position -= 1
                            should_redraw_all = True
                        selected_position -= 1
                        selected_task_list.select_prev_task()
                if should_redraw_all:
                    redraw_all()
                if prev_task < list_position + selected_window.getmaxyx()[0]:
                    print_task_row(selected_task_list, prev_task, list_position)
                if selected_task_list.selected_task < list_position + selected_window.getmaxyx()[0]:
                    print_task_row(selected_task_list, selected_task_list.selected_task, list_position)

            elif (key == curses.KEY_END or key == 336 or key == ord('L')) and not disable_movement:
                # got to the bottom of the viewable area
                prev_task = selected_task_list.selected_task
                window_size = selected_window.getmaxyx()[0] - OFFSET_FOR_TOP + OFFSET_FOR_BOT - 1
                selected_position = min(selected_task_list.size() - 1, list_position + window_size)
                selected_task_list.select(selected_position)
                if prev_task < list_position + selected_window.getmaxyx()[0]:
                    print_task_row(selected_task_list, prev_task, list_position)
                if selected_task_list.selected_task < list_position + selected_window.getmaxyx()[0]:
                    print_task_row(selected_task_list, selected_task_list.selected_task, list_position)

            elif (key == curses.KEY_HOME or key == 337 or key == ord('H')) and not disable_movement:
                # go to the top of the viewable area
                prev_task = selected_task_list.selected_task
                selected_position = list_position
                selected_task_list.select(selected_position)
                if prev_task < list_position + selected_window.getmaxyx()[0]:
                    print_task_row(selected_task_list, prev_task, list_position)
                if selected_task_list.selected_task < list_position + selected_window.getmaxyx()[0]:
                    print_task_row(selected_task_list, selected_task_list.selected_task, list_position)

            elif key == ord('M') and not disable_movement:
                # go to the middle of the viewable area
                prev_task = selected_task_list.selected_task
                selected_position = list_position + min(selected_task_list.size() / 2 - 1, ((selected_window.getmaxyx()[0] - OFFSET_FOR_TOP + OFFSET_FOR_BOT) / 2) - 1)
                selected_task_list.select(selected_position)
                if prev_task < list_position + selected_window.getmaxyx()[0]:
                    print_task_row(selected_task_list, prev_task, list_position)
                if selected_task_list.selected_task < list_position + selected_window.getmaxyx()[0]:
                    print_task_row(selected_task_list, selected_task_list.selected_task, list_position)

            elif key == ord('g') and not disable_movement:
                # go to the top
                selected_position = 0
                list_position = 0
                selected_task_list.select(selected_position)
                redraw_all()

            elif key == ord('G') and not disable_movement:
                window_size = selected_window.getmaxyx()[0] - OFFSET_FOR_TOP + OFFSET_FOR_BOT - 1
                list_position = max(0, selected_task_list.size() - window_size - 1)
                selected_position = list_position + min(selected_task_list.size() - 1, window_size)
                selected_task_list.select(selected_position)
                redraw_all()

            elif key == ord('i'):
                # invert colors
                INVERTED = not INVERTED
                redraw_all()

            elif key == ord('h') or key == ord('?'):
                # show help panel
                show_help = not show_help
                redraw_all()

            elif key == 353 and not disable_movement:
                # decrement level
                selected_task_list.decrement_selected_task_level()
                print_task_row(selected_task_list, selected_task_list.selected_task, list_position)

            elif key == 9 and not disable_movement:
                # increment level
                selected_task_list.increment_selected_task_level()
                print_task_row(selected_task_list, selected_task_list.selected_task, list_position)

            # debug information
            if args.debug:
                if key < 256:
                    #print_row((selected_window.getmaxyx()[0] + OFFSET_FOR_BOT - 1), "Character: " + chr(key), WHITE if INVERTED else STANDOUT_WHITE)
                    print_row((selected_window.getmaxyx()[0] + OFFSET_FOR_BOT - 1), "Character: " + str(key), WHITE if INVERTED else STANDOUT_WHITE)
                else:
                    print_row((selected_window.getmaxyx()[0] + OFFSET_FOR_BOT - 1), "Character: " + str(key), WHITE if INVERTED else STANDOUT_WHITE)
            else:
                pass

            selected_window.refresh()

            # is this sleep actually needed?
            time.sleep(1.0 / 60.0)

    except KeyboardInterrupt:
        pass

    finally:
        # teardown
        stdscr.keypad(0)
        stdscr.scrollok(1)
        curses.curs_set(1)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
