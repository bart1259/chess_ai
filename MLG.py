import chess
import math

class MLGAgent:
    """
    Your agent class. Please rename this to {TeamName}Agent, and this file to {TeamName}.py
    """
    depth = 2
    previous_boards = []
    previous_board_2 = None
    previous_board_3 = None
    previous_board_4 = None

    cache = {}

    def __init__(self, is_white):
        """
        Constructor, initialize your fields here.
        :param is_white: Initializes the color of the agent.
        """
        self.is_white = is_white

    @staticmethod
    def get_team_name():
        """
        Report your team name. Used for scoring purposes.+
        """
        return "Mini Lunch Gang"

    def heuristic(self, board):
        """
        Determine whose favor the board is in, and by how much.
        Positive values favor white, negative values favor black.

        Modify this. It sucks. Consider incorporating board state.
        At present, this just sums the scores of all the pieces.

        :param board:
        :return: Returns the estimated utility of the board state.
        """

        # What will be returned
        value = 0

        # Try to checkmate
        # Try to check
        # Try to capture piece

        #Find white and black king
        white_king_pos = -1
        black_king_pos = -1

        for square in chess.SQUARES:
            if board.piece_at(square) is None:
                break
            if board.piece_at(square).symbol() == "K":
                white_king_pos = square
            elif board.piece_at(square).symbol() == "k":
                black_king_pos = square

        CENTRAL_CONTROL_WEIGHT = 8
        DEVELOPING_INTO_TERRITORY = 4
        DEFENDED_PER_PIECE = 0.16
        ATTACKED_PER_PIECE = 0.1
        PIECE_VALUE = 10

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is not None:
                is_white = not piece.symbol().islower()
                x = square % 8
                y = square // 8
                team_multiplier = 1 if is_white else -1

                # CENTRAL CONTROL
                dist_to_center = math.sqrt(((3.5 - x) * (3.5 - x)) + ((3.5 - y) * (3.5 - y)))
                # assign more points of pieces are in the center
                central_control = 1 / dist_to_center

                # More points to lower ranking pieces being closer to the middle
                value += CENTRAL_CONTROL_WEIGHT * central_control / get_piece_utility(piece)

                # FURTHER INTO ENEMY TERRITORY
                # More points to pieces being further into the board but not on the edges
                # side = 0.5 if (x == 0 or x == 7) else 1
                value += DEVELOPING_INTO_TERRITORY * (y - 3.5) * 0.3 if (x == 0 or x == 7) else 1

                # FACTOR IN HOW MANY PIECES DEFEND CURRENT SQUARE
                if is_white:
                    value += DEFENDED_PER_PIECE * len(board.attackers(chess.WHITE, square))
                    value -= ATTACKED_PER_PIECE * len(board.attackers(chess.BLACK, square))
                else:
                    value -= DEFENDED_PER_PIECE * len(board.attackers(chess.BLACK, square))
                    value += ATTACKED_PER_PIECE * len(board.attackers(chess.BLACK, square))

                # More points to pieces of higher value on the board
                value += PIECE_VALUE * get_piece_utility(piece)

        # Check for check
        if board.is_attacked_by(chess.BLACK, white_king_pos):
            if board.is_checkmate():
                value += -1000
        if board.is_attacked_by(chess.WHITE, black_king_pos):
            if board.is_checkmate():
                value += 1000

        # If this is a draw, value is 0 (same for both players)
        if board.can_claim_draw():
            value = 0

        if board == self.previous_board_2 or board == self.previous_board_3 or board == self.previous_board_4:
            value /= 2

        self.previous_board_4 = self.previous_board_3
        self.previous_board_3 = self.previous_board_2
        self.previous_board_2 = board

        # Implemnt anti draw system
        # for prev_board in self.previous_boards:
        #     if board == prev_board:
        #         value *= abs(random.random())
        # self.previous_boards.append(board)

        return value

    def make_move(self, board):
        """
        Determine the next move to make, given the current board.
        :param board: The chess board
        :return: The selected move
        """
        global_score = -1e8 if self.is_white else 1e8
        chosen_move = None

        for move in board.legal_moves:
            board.push(move)

            local_score = self.minimax(board, self.depth - 1, not self.is_white, -1e8, 1e8)
            self.cache[hash_board(board, self.depth - 1, not self.is_white)] = local_score

            if self.is_white and local_score > global_score:
                global_score = local_score
                chosen_move = move
            elif not self.is_white and local_score < global_score:
                global_score = local_score
                chosen_move = move

            board.pop()

        return chosen_move

    def minimax(self, board, depth, is_maxing_white, alpha, beta):
        """
        Minimax implementation with alpha-beta pruning.

        Source: https://github.com/devinalvaro/yachess

        :param board: Chess board
        :param depth: Remaining search depth
        :param is_maxing_white: Whose score are we maxing?
        :param alpha: Alpha-beta pruning value
        :param beta: Alpha-beta pruning value
        :return: The utility of the board state
        """
        # Check if board state is in cache
        if hash_board(board, depth, is_maxing_white) in self.cache:
            return self.cache[hash_board(board, depth, is_maxing_white)]

        # Check if game is over or we have reached maximum search depth.
        if depth == 0 or not board.legal_moves:
            self.cache[hash_board(board, depth, is_maxing_white)] = self.heuristic(board)
            return self.cache[hash_board(board, depth, is_maxing_white)]

        # General case
        best_score = -1e8 if is_maxing_white else 1e8
        for move in board.legal_moves:
            board.push(move)

            local_score = self.minimax(board, depth - 1, not is_maxing_white, alpha, beta)
            self.cache[hash_board(board, depth - 1, not is_maxing_white)] = local_score

            if is_maxing_white:
                best_score = max(best_score, local_score)
                alpha = max(alpha, best_score)
            else:
                best_score = min(best_score, local_score)
                beta = min(beta, best_score)

            board.pop()

            if beta <= alpha:
                break
        self.cache[hash_board(board, depth, is_maxing_white)] = best_score
        return self.cache[hash_board(board, depth, is_maxing_white)]


def hash_board(board, depth, is_maxing_white):
    """
    Get a representation of the system that we can cache.
    """
    return str(board) + ' ' + str(depth) + ' ' + str(is_maxing_white)


def get_piece_utility(piece):
    """
    Get the utility of a piece.
    :return: Returns the standard chess score for the piece, positive if white, negative if black.
    """
    piece_symbol = piece.symbol()
    is_white = not piece_symbol.islower()

    lower = piece_symbol.lower()

    score = 1 if is_white else -1

    if lower == 'p':
        score *= 1
    elif lower == 'n':
        score *= 3
    elif lower == 'b':
        score *= 3
    elif lower == 'r':
        score *= 5
    elif lower == 'q':
        score *= 9
    elif lower == 'k':
        score *= 1
    return score
