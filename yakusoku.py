#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "rawrgrr"

from sys import stdin
import curses
import time

# TODO update help line
# TODO handle command line arguments
# TODO loading from files
# TODO show help
# TODO allow multiple files
# TODO handle mouse clicks

class TaskStatus:
    TODO = 1
    DOING = 2
    DONE = 3

class TaskList:
    def __init__(self):
        self.selected_task = -1
        self.tasks = []
        self.statuses = []

    def __init__(self, tasks):
        if len(tasks) >= 0:
            self.selected_task = 0
            self.tasks = tasks
            self.statuses = []
            for i in xrange(len(self.tasks)):
                self.statuses.append(TaskStatus.TODO)
        else:
            return self.__init__()

    def add_task(self, task):
        self.tasks.append(task)
        self.statuses.append(TaskStatus.TODO)

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
        return self.statuses[self.selected_task] == TaskStatus.TODO

    def is_selected_task_doing(self):
        return self.statuses[self.selected_task] == TaskStatus.DOING

    def is_selected_task_done(self):
        return self.statuses[self.selected_task] == TaskStatus.DONE

    def transition_selected_task(self):
        if self.is_selected_task_todo():
            self.statuses[self.selected_task] = TaskStatus.DOING
        elif self.is_selected_task_doing():
            self.statuses[self.selected_task] = TaskStatus.DONE

    def untransition_selected_task(self):
        if self.is_selected_task_done():
            self.statuses[self.selected_task] = TaskStatus.DOING
        elif self.is_selected_task_doing():
            self.statuses[self.selected_task] = TaskStatus.TODO

    def size(self):
        return len(self.tasks)

tasks = []

tasks.append("foobar a")
tasks.append("foobar b")
tasks.append("foobar c")
tasks.append("foobar d")
tasks.append("foobar e")
tasks.append("foobar f")
tasks.append("foobar g")
tasks.append("foobar h")
tasks.append("foobar i")
tasks.append("foobar j")
tasks.append("foobar k")
tasks.append("foobar l")
tasks.append("foobar m")
tasks.append("foobar n")
tasks.append("foobar o")
tasks.append("foobar p")
tasks.append("foobar q")
tasks.append("foobar r")
tasks.append("foobar s")
tasks.append("foobar t")
tasks.append("foobar u")
tasks.append("foobar v")
tasks.append("foobar w")
tasks.append("foobar x")
tasks.append("foobar y")
tasks.append("foobar z")
tasks.append("foobar a")
tasks.append("foobar b")
tasks.append("foobar c")
tasks.append("foobar d")
tasks.append("foobar e")
tasks.append("foobar f")
tasks.append("foobar g")
tasks.append("foobar h")
tasks.append("foobar i")
tasks.append("foobar j")
tasks.append("foobar k")
tasks.append("foobar l")
tasks.append("foobar m")

selected_task_list = TaskList(tasks)

OFFSET_FOR_TOP = 2
OFFSET_FOR_BOT = -2
SKIP_LEVEL = 10
INVERTED = False
DEBUG = False

if __name__ == "__main__":

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
        NORMAL = curses.color_pair(0)
        RED = curses.color_pair(1)
        GREEN = curses.color_pair(2)
        YELLOW = curses.color_pair(3)
        BLUE = curses.color_pair(4)
        MAGENTA = curses.color_pair(5)
        CYAN = curses.color_pair(6)
        WHITE = curses.color_pair(7)

        # standout variants
        STANDOUT_RED = curses.color_pair(1) | curses.A_STANDOUT
        STANDOUT_GREEN = curses.color_pair(2) | curses.A_STANDOUT
        STANDOUT_YELLOW = curses.color_pair(3) | curses.A_STANDOUT
        STANDOUT_BLUE = curses.color_pair(4) | curses.A_STANDOUT
        STANDOUT_MAGENTA = curses.color_pair(5) | curses.A_STANDOUT
        STANDOUT_CYAN = curses.color_pair(6) | curses.A_STANDOUT
        STANDOUT_WHITE = curses.color_pair(7) | curses.A_STANDOUT

        # bold variants
        BOLD_RED = curses.color_pair(1) | curses.A_BOLD
        BOLD_GREEN = curses.color_pair(2) | curses.A_BOLD
        BOLD_YELLOW = curses.color_pair(3) | curses.A_BOLD
        BOLD_BLUE = curses.color_pair(4) | curses.A_BOLD
        BOLD_MAGENTA = curses.color_pair(5) | curses.A_BOLD
        BOLD_CYAN = curses.color_pair(6) | curses.A_BOLD
        BOLD_WHITE = curses.color_pair(7) | curses.A_BOLD

        # bold standout variants
        BOLD_STANDOUT_RED = curses.color_pair(1) | curses.A_BOLD | curses.A_STANDOUT
        BOLD_STANDOUT_GREEN = curses.color_pair(2) | curses.A_BOLD | curses.A_STANDOUT
        BOLD_STANDOUT_YELLOW = curses.color_pair(3) | curses.A_BOLD | curses.A_STANDOUT
        BOLD_STANDOUT_BLUE = curses.color_pair(4) | curses.A_BOLD | curses.A_STANDOUT
        BOLD_STANDOUT_MAGENTA = curses.color_pair(5) | curses.A_BOLD | curses.A_STANDOUT
        BOLD_STANDOUT_CYAN = curses.color_pair(6) | curses.A_BOLD | curses.A_STANDOUT
        BOLD_STANDOUT_WHITE = curses.color_pair(7) | curses.A_BOLD | curses.A_STANDOUT

        # main printing function
        def print_row(row, message, color):
            spaces = " " * selected_window.getmaxyx()[1]
            selected_window.addnstr(row, 0, spaces, selected_window.getmaxyx()[1], color)
            selected_window.addnstr(row, 0, message, selected_window.getmaxyx()[1], color)

        def print_task_row(task_list, row):
            task_status = task_list.statuses[row]

            if INVERTED:
                if task_status == TaskStatus.TODO:
                    print_row(row + OFFSET_FOR_TOP, " TODO    " + task_list.tasks[row] + "   ", STANDOUT_RED if task_list.selected_task == row else RED)
                elif task_status == TaskStatus.DOING:
                    print_row(row + OFFSET_FOR_TOP, " DOING   " + task_list.tasks[row] + "   ", STANDOUT_YELLOW if task_list.selected_task == row else YELLOW)
                elif task_status == TaskStatus.DONE:
                    print_row(row + OFFSET_FOR_TOP, " DONE    " + task_list.tasks[row] + "   ", STANDOUT_GREEN if task_list.selected_task == row else GREEN)
            else:
                if task_status == TaskStatus.TODO:
                    print_row(row + OFFSET_FOR_TOP, " TODO    " + task_list.tasks[row] + "   ", RED if task_list.selected_task == row else STANDOUT_RED)
                elif task_status == TaskStatus.DOING:
                    print_row(row + OFFSET_FOR_TOP, " DOING   " + task_list.tasks[row] + "   ", YELLOW if task_list.selected_task == row else STANDOUT_YELLOW)
                elif task_status == TaskStatus.DONE:
                    print_row(row + OFFSET_FOR_TOP, " DONE    " + task_list.tasks[row] + "   ", GREEN if task_list.selected_task == row else STANDOUT_GREEN)

        def redraw_all():
            # print out everything once
            for i in xrange(selected_task_list.size()):
                print_task_row(selected_task_list, i)

            # print title and status lines
            print_row(0, "[Demo TODO List]", STANDOUT_WHITE if INVERTED else BLUE)
            print_row(1, " Status  Task", STANDOUT_WHITE if INVERTED else MAGENTA)
            print_row(selected_window.getmaxyx()[0] + OFFSET_FOR_BOT, "", STANDOUT_WHITE if INVERTED else WHITE)
            print_row(selected_window.getmaxyx()[0] + OFFSET_FOR_BOT, " j: down        k: up        space: transition task        backspace: untransition task", STANDOUT_WHITE if INVERTED else WHITE)

            selected_window.refresh()

        redraw_all()

        # main loop
        while True:
            #key = stdin.read(1)
            key = selected_window.getch()

            if key == ord(' '):
                # transition task
                prev_task = selected_task_list.selected_task
                selected_task_list.transition_selected_task()
                if selected_task_list.is_selected_task_done():
                    selected_task_list.select_next_task()
                    print_task_row(selected_task_list, prev_task)
                print_task_row(selected_task_list, selected_task_list.selected_task)

            elif key == 127 or key == curses.KEY_DC or key == curses.KEY_BACKSPACE:
                # untransition task
                prev_task = selected_task_list.selected_task
                selected_task_list.untransition_selected_task()
                if selected_task_list.is_selected_task_todo():
                    selected_task_list.select_prev_task()
                    print_task_row(selected_task_list, prev_task)
                print_task_row(selected_task_list, selected_task_list.selected_task)

            if key == ord('q') or key == ord('Q'):
                # quit
                break

            elif key == ord('j') or key == curses.KEY_DOWN:
                # go down
                if selected_task_list.can_select_next_task():
                    prev_task = selected_task_list.selected_task
                    selected_task_list.select_next_task()
                    print_task_row(selected_task_list, prev_task)
                    print_task_row(selected_task_list, selected_task_list.selected_task)

            elif key == ord('k') or key == curses.KEY_UP:
                # go up
                if selected_task_list.can_select_prev_task():
                    prev_task = selected_task_list.selected_task
                    selected_task_list.select_prev_task()
                    print_task_row(selected_task_list, prev_task)
                    print_task_row(selected_task_list, selected_task_list.selected_task)

            elif key == ord('J') or key == curses.KEY_NPAGE:
                # go down by SKIP_LEVEL
                prev_task = selected_task_list.selected_task
                for i in xrange(SKIP_LEVEL):
                    if selected_task_list.can_select_next_task():
                        selected_task_list.select_next_task()
                print_task_row(selected_task_list, prev_task)
                print_task_row(selected_task_list, selected_task_list.selected_task)

            elif key == ord('K') or key == curses.KEY_PPAGE:
                # go up by SKIP_LEVEL
                prev_task = selected_task_list.selected_task
                for i in xrange(SKIP_LEVEL):
                    if selected_task_list.can_select_prev_task():
                        selected_task_list.select_prev_task()
                print_task_row(selected_task_list, prev_task)
                print_task_row(selected_task_list, selected_task_list.selected_task)

            elif key == curses.KEY_END or key == 336 or key == ord('L'):
                # got to the bottom
                prev_task = selected_task_list.selected_task
                selected_task_list.select_last_task()
                print_task_row(selected_task_list, prev_task)
                print_task_row(selected_task_list, selected_task_list.selected_task)

            elif key == curses.KEY_HOME or key == 337 or key == ord('H'):
                # go to the top
                prev_task = selected_task_list.selected_task
                selected_task_list.select_first_task()
                print_task_row(selected_task_list, prev_task)
                print_task_row(selected_task_list, selected_task_list.selected_task)

            elif key == ord('M'):
                # go to the middle
                prev_task = selected_task_list.selected_task
                selected_task_list.select_middle_task()
                print_task_row(selected_task_list, prev_task)
                print_task_row(selected_task_list, selected_task_list.selected_task)

            elif key == ord('i'):
                # invert colors
                INVERTED = not INVERTED
                redraw_all()

            # debug information
            if DEBUG:
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
