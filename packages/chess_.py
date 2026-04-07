import chess

def checkmate_test(fen_string: str) -> bool:
    board = chess.Board()
    board.set_fen(fen_string)
    return board.is_checkmate()

def legal_moves_black(fen_string: str) -> list:
    board = chess.Board(fen_string)

    if board.turn != chess.BLACK:
        return []

    return [move.uci() for move in board.legal_moves]
