import os

import chess
import chess.engine
import pyglet
import engine
import threading
import numpy as np
import re


def rgbtohex(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'


board = chess.Board()

window = pyglet.window.Window(1000, 1000)
square_size = 100
selected_square = None
piece_moves = []
endgame_label = pyglet.text.Label('',
                                  font_size=36,
                                  x=100, y=window.height-100)

image_files = {
    (chess.WHITE, chess.PAWN): 'images/whitePawn.png',
    (chess.WHITE, chess.ROOK): 'images/whiteRook.png',
    (chess.WHITE, chess.KNIGHT): 'images/whiteKnight.png',
    (chess.WHITE, chess.BISHOP): 'images/whiteBishop.png',
    (chess.WHITE, chess.QUEEN): 'images/whiteQueen.png',
    (chess.WHITE, chess.KING): 'images/whiteKing.png',
    (chess.BLACK, chess.PAWN): 'images/blackPawn.png',
    (chess.BLACK, chess.ROOK): 'images/blackRook.png',
    (chess.BLACK, chess.KNIGHT): 'images/blackKnight.png',
    (chess.BLACK, chess.BISHOP): 'images/blackBishop.png',
    (chess.BLACK, chess.QUEEN): 'images/blackQueen.png',
    (chess.BLACK, chess.KING): 'images/blackKing.png',
}


def check_game_over():
    outcome = board.outcome()
    if outcome is None:
        endgame_label.text = ''
    elif outcome.winner is None:
        endgame_label.text = 'Game ends in draw'
    elif outcome.winner == chess.WHITE:
        endgame_label.text = 'White wins'
    elif outcome.winner == chess.BLACK:
        endgame_label.text = 'Black wins'


@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == pyglet.window.mouse.LEFT:
        global selected_square
        clicked_square = chess.square(int(x / 100), int(y / 100))
        clicked_piece = board.piece_at(clicked_square)
        if clicked_piece is not None and clicked_piece.color == board.turn:
            selected_square = clicked_square
        else:
            possible_moves = list(filter(lambda move: (move.to_square == clicked_square), piece_moves))
            if len(possible_moves) > 0:
                board.push(possible_moves[0])
                check_game_over()
                #print(engine.convert_board_to_input(board))
                window.dispatch_event('on_draw')
                window.flip()
                if endgame_label.text == '':
                    board.push(engine.get_move(engine.test_net, board))
                check_game_over()
                selected_square = None
                #print(engine.convert_board_to_input(board))

'''
data_1 = np.zeros((1, 8, 8, 7))
data_half = np.zeros((1, 8, 8, 7))
data_0 = np.zeros((1, 8, 8, 7))
white_boards = np.zeros((1, 8, 8, 7))
black_boards = np.zeros((1, 8, 8, 7))

stockfish = chess.engine.SimpleEngine.popen_uci(
    "/home/adam/Downloads/stockfish_15_linux_x64_avx2/stockfish_15_x64_avx2")


def run_engine_move():
    global board
    move = stockfish.play(board, chess.engine.Limit(time=0.1))
    board.push(move.move)

    board_array = np.array([engine.convert_board_to_input(board)])

    print("before", engine.convert_board_to_input(board))
    if board.turn == chess.BLACK:
        np.append(black_boards, board_array, axis=0)
        print("after", black_boards[-1])
    else:
        np.append(white_boards, board_array, axis=0)
        print("after", white_boards[-1])

    if board.is_game_over():
        outcome = board.outcome()
        if outcome is None:
            np.append(data_half, black_boards, axis=0)
            np.append(data_half, white_boards, axis=0)
        elif outcome == chess.BLACK:
            np.append(data_1, black_boards, axis=0)
            np.append(data_0, white_boards, axis=0)
        else:
            np.append(data_0, black_boards, axis=0)
            np.append(data_1, white_boards, axis=0)

        board = chess.Board()
        print(data_1, data_half, data_0)
'''

epoch = 0
engine_count = 10
engine_x = 0
engine_y = 1
engines = []
engine_wins = []

checkpoints = os.listdir("checkpoints")
if len(checkpoints) == 0:
    for i in range(engine_count):
        engines.append(engine.make_model())
        engine_wins.append(0)
else:
    max_num = 0
    latest = checkpoints[0]
    for checkpoint in checkpoints:
        checkpoint_num = re.findall(r"(\d+)", checkpoint)[0]
        if checkpoint_num > max_num:
            max_num = checkpoint_num
            checkpoint
    new_net = engine.make_model()
    new_net.load_weights(latest)
    engines = [latest]
    for _ in range(engine_count - 1):
        engines.append(engine.make_model(new_net))


def run_engine_move():
    global engine_x
    global engine_y
    global board
    global engine_wins
    global engines
    global epoch

    if board.turn == chess.WHITE:
        board.push(engine.get_move(engines[engine_x], board))
    else:
        board.push(engine.get_move(engines[engine_y], board))

    if board.is_game_over():
        epoch += 1
        outcome = board.outcome()
        print(engine_x, engine_y)
        if outcome == chess.BLACK:
            engine_wins[engine_x] -= 1
            engine_wins[engine_y] += 1
        elif outcome == chess.WHITE:
            engine_wins[engine_y] -= 1
            engine_wins[engine_x] += 1
        engine_y += 1
        if engine_y >= engine_count:
            engine_x += 1
            engine_y = engine_x + 1
            if engine_x >= engine_count-1:
                print("finished thing")
                winner_i = np.argmax(np.array(engine_wins))
                winner = engines[winner_i]
                engines = [winner]
                winner.save_weights("checkpoints/cp-{epoch:06d}.ckpt".format(epoch=epoch))
                for j in range(engine_count-1):
                    engines.append(engine.make_model(winner))
                for j in range(engine_count):
                    if engine_wins[j] != 0:
                        print("fuck yea")
                    engine_wins[j] = 0
                engine_x = 0
                engine_y = 0
        print(engine_wins)
        board = chess.Board()


@window.event
def on_draw():

    run_engine_move()

    window.clear()
    endgame_label.draw()
    for x in range(8):
        for y in range(8):
            all_moves = board.legal_moves
            global piece_moves
            piece_moves = list(filter(lambda move: (move.from_square == selected_square), all_moves))
            current_move = chess.Move(selected_square, chess.square(x, y))
            last_move = None
            current_square = chess.square(x, y)
            if board.turn == chess.WHITE and board.halfmove_clock > 0:
                last_move = board.peek()
            color = ()
            if selected_square is not None and selected_square == chess.square(x, y):
                color = (218, 196, 49)
            elif selected_square is not None and current_move in piece_moves:
                if x % 2 == y % 2:
                    color = (248, 239, 134)
                else:
                    color = (248, 236, 90)
            elif(last_move is not None and
                 (last_move.from_square == current_square or last_move.to_square == current_square)):
                if x % 2 == y % 2:
                    color = (int(248/2), 239, 134)
                else:
                    color = (int(248/2), 236, 90)
            else:
                if x % 2 == y % 2:
                    color = (255, 207, 159)
                else:
                    color = (210, 140, 69)
            square = pyglet.shapes.Rectangle(x=x*square_size, y=y*square_size, width=square_size, height=square_size,
                                             color=color)
            square.draw()
            current_piece = board.piece_at(chess.square(x, y))
            if current_piece is not None:
                piece_sprite = pyglet.sprite.Sprite(pyglet.image.load(
                    image_files[(current_piece.color, current_piece.piece_type)]
                ))
                piece_sprite.scale = square_size / piece_sprite.width
                piece_sprite.x = x * square_size
                piece_sprite.y = y * square_size
                piece_sprite.draw()


class CustomLoop(pyglet.app.EventLoop):
    def idle(self):
        dt = self.clock.update_time()
        self.clock.call_scheduled_functions(dt)

        # Redraw all windows
        for currentWindow in pyglet.app.windows:
            currentWindow.switch_to()
            currentWindow.dispatch_event('on_draw')
            currentWindow.flip()
            currentWindow._legacy_invalid = False

        # no timout (sleep-time between idle()-calls)
        return 0


pyglet.app.event_loop = CustomLoop()
pyglet.app.run() # locks the thread


