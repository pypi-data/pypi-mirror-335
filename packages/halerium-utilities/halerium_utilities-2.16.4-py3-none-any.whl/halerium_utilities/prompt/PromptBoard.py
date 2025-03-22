from halerium_utilities.board.navigator import BoardNavigator
from halerium_utilities.board.board import Board
from halerium_utilities.collab.collab_board import CollabBoard
from halerium_utilities.logging.exceptions import (
    BoardConnectionError, CardTypeError, ElementTypeError, PromptChainError)


# class PromptBoard(BoardNavigator):
#
#     def __init__(self, board, collab=True):
#
#         self.collab = bool(collab)
#         if self.collab:
#             self.board = CollabBoard(board)
#         else:
#             self.board = Board(board)
#
#     def set_note_element_title(self, id: str, title: str, follow_link=True):
#         element = self.path_elements[id]
#         if element.type != "note":
#             raise ElementTypeError(f"id {id} does not belong to a note element.")
#
#         if follow_link and (card_id := self.get_linked_card(id)):
#             self.board
#             self.cards[card_id].type_specific
#         else:
#             return element.type_specific.title
