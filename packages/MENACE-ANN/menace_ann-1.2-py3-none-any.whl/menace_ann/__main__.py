# Jacobus Burger (2024)
# MENACE (short for Matchbox Educable Noughts and Crosses Engine) was
#   an early convolutional neural network. This program is a replication
#   of the basic principle of MENACE in Python 3.
# see: https://en.wikipedia.org/wiki/Matchbox_Educable_Noughts_and_Crosses_Engine
from time import sleep
from random import choice, randint
from random import choice
import json
import os





# what square "colors" are open on the current board state
open_tiles = [*range(9)]
# constants representing each player occupancy with a number
NO_ONE = 0
MENACE = 1
PLAYER = 2
# which tile is occupied by which player
board_state = [NO_ONE] * 9
# constants representing the number of beads added/removed in learning
REWARD = 2
TIE = 1
PUNISH = 1
# which bead was picked for which board state represented as a list of tuples of (bead_number, board_state), for learning
actions = []
# the "neural network" of MENACE. Represents each board state as a hashable string with a corresponding list reprensenting the matchbox of beads
matchboxes = { "         ": [0, 1, 2, 3, 4, 5, 6, 7, 8] }
# the current generation of MENACE
generation = 0
# interesting note: move order doesn't need to be remembered, only the choice for each board state
DELAY = 0.5  # number of seconds to wait before displaying MENACE's move
CHAR_MAP = {
    NO_ONE: ' ',
    MENACE: 'O',
    PLAYER: 'X',
}
if os.name == "nt":
    # Windows is a mess, so I've chosen to just put data in whatever the
    # current directory is when the user runs the script. Is this ~robust~?
    # NO. I'm betting on the fact that the group of people who use Windows
    # AND install Python3 packages with Pip AND run scripts they installed
    # with pip in terminal AND would pay attention to this project are so
    # small that I'll never have to deal with it.
    # It's "bad practice", but perfection is overrated anyways.
    DATA_PATH=os.getcwd()
else:
    DATA_PATH=f"/home/{os.getlogin()}/.local/bin/matchboxes.json"





def save(generation, matchboxes):
    """
    save(filename, generation, matchboxes)

    Serialize current [generation, matchboxes] for persistent storage.
    """
    with open(DATA_PATH, "w") as file:
        try:
            json.dump([generation, matchboxes], file)
        except:
            print("failed to save to {}".format(DATA_PATH))


def load():
    """
    load(filename)

    Deserialize a json file and return [generation, matchboxes]
        stored within it. For persistent memory of MENACE.
    If no file exists, return default struct definitions instead.
    """
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as file:
            generation, matchboxes = json.load(file)
    else:
        generation = 0
        matchboxes = { "         ": [0, 1, 2, 3, 4, 5, 6, 7, 8] }
    return [generation, matchboxes]


def learn(winner, matchboxes, actions, open_tiles):
    """
    learn(matchboxes, winner, actions)

    Backpropogates learned information into matchboxes based on who
        the winner is using move informtion from actions.
    """
    # punish MENACE by taking away some of the bead colours used from
    #   their matchboxes during the game
    if winner == PLAYER:
        for bead, state in actions:
            for _ in range(PUNISH):
                # ensure there's always at least 1 bead in each matchbox
                if type(matchboxes[state]) != list:
                    matchboxes[state] = [randint(0, 8)]
                else:
                    matchboxes[state].remove(bead)
    # reward MENACE by adding back more of the bead colours used from
    #   their matchboxes during the game
    if winner == MENACE:
        for bead, state in actions:
            for _ in range(REWARD):
                matchboxes[state].append(bead)
    # encourage MENACE to explore more by adding more of a random bead
    #   into each matchbox
    if winner == NO_ONE:
        for _, state in actions:
            for _ in range(TIE):
                bead = choice(matchboxes[state])
                matchboxes[state].append(bead)


def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def board_string(board_state):
    return ''.join(CHAR_MAP[n] for n in board_state)


def show_board(generation, board_state):
    sleep(DELAY)
    clear()
    print("===== MENACE gen {} =====".format(generation))
    board = board_string(board_state)
    for i in range(2):
        print('|'.join(board[i * 3 : i * 3 + 3]))
        print("-+-+-")
    print('|'.join(board[6:9]))
    sleep(DELAY)


def winning_player(board_state):
    # I love snake lang 🐍
    for i in range(3):
        # check for rows
        if all(state == MENACE for state in board_state[i * 3 : i * 3 + 3]):
            return MENACE
        if all(state == PLAYER for state in board_state[i * 3 : i * 3 + 3]):
            return PLAYER
        # check for columns
        if all(state == MENACE for state in board_state[i :: 3]):
            return MENACE
        if all(state == PLAYER for state in board_state[i :: 3]):
            return PLAYER
    # check for diagonals
    #   check top-right to bottom-left
    if all(state == MENACE for state in board_state[2 : 7 : 2]):
        return MENACE
    if all(state == PLAYER for state in board_state[2 : 7 : 2]):
        return PLAYER
    #   check top-left to bottom-right
    if all(state == MENACE for state in board_state[0 :: 4]):
        return MENACE
    if all(state == PLAYER for state in board_state[0 :: 4]):
        return PLAYER
    return NO_ONE


def main():
    # retrieve any memory if it exists
    generation, matchboxes = load()
    # start the game
    game_running = True
    while game_running:
        # OTHERWISE TIE
        winner = winning_player(board_state)
        if len(open_tiles) == 0 and winner == NO_ONE:
            learn(winner, matchboxes, actions, open_tiles)
            clear()
            print("=====TIE=====")
            break

        # MENACE MOVES
        # show board state before
        show_board(generation, board_state)
        sleep(DELAY)
        # generate a matchbox if it doesn't exist for this board state
        if board_string(board_state) not in matchboxes:
            matchboxes.update({
                board_string(board_state): [*open_tiles]
            })
        # generate a random bead if a matchbox is empty
        if not matchboxes[board_string(board_state)]:
            matchboxes.update({
                board_string(board_state): [choice(open_tiles)]
            })
        # menace picks a bead from the matchbox for the current state
        # and action is recorded for later backpropogation
        if type(matchboxes[board_string(board_state)]) == int:
            bead = randint(0, 8)
        else:
            bead = choice(matchboxes[board_string(board_state)])
        actions.append((bead, board_string(board_state)))
        # remove from open_tiles
        open_tiles.remove(bead)
        # menace updates board state with its move
        board_state[bead] = MENACE
        # show decision
        show_board(generation, board_state)

        # CHECK IF MENACE WON
        winner = winning_player(board_state)
        if winner == MENACE:
            learn(winner, matchboxes, actions, open_tiles)
            clear()
            print("===== MENACE WINS =====")
            break
        # OTHERWISE TIE
        winner = winning_player(board_state)
        if len(open_tiles) == 0 and winner == NO_ONE:
            learn(winner, matchboxes, actions, open_tiles)
            clear()
            print("=====TIE=====")
            break


        # PLAYER MOVES
        # validate and retrieve player input
        # (must be int and in open_tiles)
        valid_input = False
        while not valid_input:
            # display board state after MENACE move before player move
            show_board(generation, board_state)
            try:
                X = int(input("""
                1|2|3
                -+-+-
                4|5|6
                -+-+-
                7|8|9
                """))
                X -= 1  # correct offset
            except:
                exit()
            if X not in open_tiles:
                continue
            else:
                valid_input = True
        # remove from open_tiles
        open_tiles.remove(X)
        # update board state with player move
        board_state[X] = PLAYER

        # CHECK IF MENACE LOST
        winner = winning_player(board_state)
        if winner == PLAYER:
            learn(winner, matchboxes, actions, open_tiles)
            clear()
            print("===== MENACE LOSES =====")
            break
        # OTHERWISE TIE
        winner = winning_player(board_state)
        if len(open_tiles) == 0 and winner == NO_ONE:
            learn(winner, matchboxes, actions, open_tiles)
            clear()
            print("=====TIE=====")
            break

    # store any learned info from the game
    save(generation + 1, matchboxes)


if __name__ == '__main__':
    main()
