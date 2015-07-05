#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "rawrgrr"

from sys import stdin
import curses
import json
import time

# TODO update help line
# TODO handle command line arguments
# TODO loading from files
# TODO handle levels (tab to increase level, shift-tab to decrease level
# TODO handle long todo-lists (longer than one screen vertically)
# TODO customize loading from files
# TODO show help
# TODO allow multiple files
# TODO handle mouse clicks

class TaskStatus:
    TODO = 1
    DOING = 2
    DONE = 3

class TaskItem:
    def __init__(self, description, status=TaskStatus.TODO, level=0):
        self.description = description
        if status == "todo":
            self.status = TaskStatus.TODO
        elif status == "doing":
            self.status = TaskStatus.DOING
        elif status == "done":
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
        with open(DEFAULT_JSON_FILE, 'r') as tasks_json_file:
            json_data = json.load(tasks_json_file)

        self.tasks = []

        for item in json_data:
            description = item["description"]
            status = item["status"]
            level = item["level"]
            self.tasks.append(TaskItem(description, status, level))

    def add_task(self, description, status=TaskStatus.TODO, level=0):
        self.tasks.append(TaskItem(description, status, level))

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

DEFAULT_JSON_FILE = "tasks.json"

selected_task_list = TaskList(DEFAULT_JSON_FILE)

OFFSET_FOR_TOP = 2
OFFSET_FOR_BOT = -2
SKIP_LEVEL = 10
INVERTED = False
DEBUG = False

list_position = 0
selected_position = 0

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

            if INVERTED:
                if task_status == TaskStatus.TODO:
                    print_row(row + OFFSET_FOR_TOP - offset, " TODO    " + (2 * task_list.tasks[row].level) * " " + task_list.tasks[row].description + "   ", STANDOUT_RED if task_list.selected_task == row else RED)
                elif task_status == TaskStatus.DOING:
                    print_row(row + OFFSET_FOR_TOP - offset, " DOING   " + (2 * task_list.tasks[row].level) * " " + task_list.tasks[row].description + "   ", STANDOUT_YELLOW if task_list.selected_task == row else YELLOW)
                elif task_status == TaskStatus.DONE:
                    print_row(row + OFFSET_FOR_TOP - offset, " DONE    " + (2 * task_list.tasks[row].level) * " " + task_list.tasks[row].description + "   ", STANDOUT_GREEN if task_list.selected_task == row else GREEN)
            else:
                if task_status == TaskStatus.TODO:
                    print_row(row + OFFSET_FOR_TOP - offset, " TODO    " + (2 * task_list.tasks[row].level) * " " + task_list.tasks[row].description + "   ", RED if task_list.selected_task == row else STANDOUT_RED)
                elif task_status == TaskStatus.DOING:
                    print_row(row + OFFSET_FOR_TOP - offset, " DOING   " + (2 * task_list.tasks[row].level) * " " + task_list.tasks[row].description + "   ", YELLOW if task_list.selected_task == row else STANDOUT_YELLOW)
                elif task_status == TaskStatus.DONE:
                    print_row(row + OFFSET_FOR_TOP - offset, " DONE    " + (2 * task_list.tasks[row].level) * " " + task_list.tasks[row].description + "   ", GREEN if task_list.selected_task == row else STANDOUT_GREEN)


        def redraw_all():
            # print out everything once
            for i in xrange(selected_task_list.size()):
                if list_position <= i < (list_position + selected_window.getmaxyx()[0] - OFFSET_FOR_TOP + OFFSET_FOR_BOT):
                    print_task_row(selected_task_list, i, list_position)

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
                    if selected_position == selected_window.getmaxyx()[0] - OFFSET_FOR_TOP + OFFSET_FOR_BOT - 1:
                        list_position += 1
                        redraw_all()
                    else:
                        selected_position += 1
                    prev_task = selected_task_list.selected_task
                    selected_task_list.select_next_task()
                    print_task_row(selected_task_list, prev_task, list_position)
                    print_task_row(selected_task_list, selected_task_list.selected_task, list_position)

            elif key == ord('k') or key == curses.KEY_UP:
                # go up
                if selected_task_list.can_select_prev_task():
                    if selected_position == 0 and list_position > 0:
                        list_position -= 1
                        redraw_all()
                    else:
                        selected_position -= 1
                    prev_task = selected_task_list.selected_task
                    selected_task_list.select_prev_task()
                    print_task_row(selected_task_list, prev_task, list_position)
                    print_task_row(selected_task_list, selected_task_list.selected_task, list_position)

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

            elif key == ord('1'):
                # decrement level
                selected_task_list.decrement_selected_task_level()
                print_task_row(selected_task_list, selected_task_list.selected_task)

            elif key == ord('2'):
                # increment level
                selected_task_list.increment_selected_task_level()
                print_task_row(selected_task_list, selected_task_list.selected_task)

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
