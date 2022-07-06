import chess
import tensorflow as tf
import time
import numpy as np
import logging


def piece_to_array(piece_type):
    if piece_type is None:
        return np.array([1, 0, 0, 0, 0, 0, 0])
    elif piece_type == chess.PAWN:
        return np.array([0, 1, 0, 0, 0, 0, 0])
    elif piece_type == chess.ROOK:
        return np.array([0, 0, 1, 0, 0, 0, 0])
    elif piece_type == chess.KNIGHT:
        return np.array([0, 0, 0, 1, 0, 0, 0])
    elif piece_type == chess.BISHOP:
        return np.array([0, 0, 0, 0, 1, 0, 0])
    elif piece_type == chess.QUEEN:
        return np.array([0, 0, 0, 0, 0, 1, 0])
    elif piece_type == chess.KING:
        return np.array([0, 0, 0, 0, 0, 0, 1])
    print("fuck up in function piece_to_array")


def convert_board_to_input(in_board):
    board = in_board if in_board.turn == chess.WHITE else in_board.mirror()
    board_array = np.zeros((8, 8, 7))
    for x in range(8):
        for y in range(8):
            board_array[x][y] = piece_to_array(board.piece_type_at(chess.square(x, y)))
    return board_array


def make_model(base=None):
    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(8, 8, 7)),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    #print(model.layers[1].get_weights()[0])
    if base is not None:
        for layer, base_layer in zip(model.layers, base.layers):
            new_weights = []
            for piece in base_layer.get_weights():
                new_weights.append(piece + (np.random.randn(*piece.shape) * learning_rate))
            layer.set_weights(new_weights)
        #print(model.layers[1].get_weights()[0])
    model.compile(optimizer='adam',
                  loss=loss_fn,
                  metrics=['accuracy'])
    return model


learning_rate = 0.01

test_net = make_model()
#net2 = make_model(base=net1)


def get_move(net, board):
    # board_array = convert_board_to_input(board)
    board_list = []
    moves = list(board.legal_moves)
    for move in moves:
        new_board = board.copy()
        new_board.push(move)
        board_list.append(convert_board_to_input(new_board))
    board_array = np.array(board_list)
    guess = net.predict(board_array, verbose=0)
    move_index = np.argmax(guess)
    move = moves[move_index]
    return move
