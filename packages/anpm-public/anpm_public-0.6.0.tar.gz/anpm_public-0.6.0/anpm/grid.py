from tkinter import Frame, Event, Label
from typing import Literal, Callable
from tkinter.messagebox import showinfo

from anpm.tk import protect_grid_size, Border
from anpm import cycle_list


class Grid(dict[tuple[int, int], "Grid.Tile"]):
    def __init__(self):
        self.size = (0, 0)
        super().__init__()
        self.selected = None
        self.teams = []
        self.team = None
        self.running = False
        self.on_death = lambda: None

        self.outer_frame = Frame()
        self.inner_frame = Frame(self.outer_frame)
        self.inner_frame.grid_propagate(False)
        self.inner_frame.pack(expand=True)

        def update_inner_grid_size():
            outer_width = self.outer_frame.winfo_width()
            outer_height = self.outer_frame.winfo_height()

            grid_width, grid_height = self.size

            ratio = grid_width / grid_height if grid_height != 0 else 1

            if outer_width / outer_height > ratio:
                width = outer_height * ratio
                height = outer_height
            else:
                width = outer_width
                height = outer_width / ratio

            self.inner_frame.configure(width=width, height=height)

            for w in self.inner_frame.winfo_children():
                if isinstance(w, Label):
                    w.update_idletasks()
                    w.configure(wraplength=w.winfo_width())

        self.outer_frame.bind("<Configure>", lambda _: update_inner_grid_size())
        self.force_resize = update_inner_grid_size

    def update_grid(self, size: tuple[int, int], tile_colours: list[str] | tuple[str, ...], teams: list[str], on_death: Callable[[], None]):
        self.size = size
        self.selected = None
        self.teams = teams
        self.team = teams[0]
        self.running = True
        self.on_death = on_death

        for pos, tile in list(self.items()):
            tile.destroy()
            del self[pos]

        width, height = size

        colour_index = 0

        for y in range(height):
            self.inner_frame.columnconfigure(y, weight=1)

            for x in range(width):
                self.inner_frame.rowconfigure(x, weight=1)

                pos = (x, height - y - 1)

                tile = self.Tile(self, pos, tile_colours[colour_index])
                tile.grid(row=y, column=x, sticky="nsew")

                self.update({pos: tile})

                colour_index = (colour_index + 1) % len(tile_colours)

                Border(self.inner_frame).grid(row=0, rows=height, column=x, sticky="nsw")
                if x == width - 1: Border(self.inner_frame).grid(row=0, rows=width, column=x + 1, sticky="nsw")

            Border(self.inner_frame).grid(row=y, column=0, columns=height, sticky="new")
            if y == height - 1: Border(self.inner_frame).grid(row=y + 1, column=0, columns=height, sticky="new")

            if width / 2 == round(width / 2):
                colour_index = (colour_index + 1) % len(tile_colours)

        self.force_resize()

    class Tile(Label):
        def __init__(self, grid: "Grid", pos: tuple[int, int], colour: str):
            self.colour = colour
            self.pos = pos
            self.grid_ = grid
            self.piece = None

            super().__init__(grid.inner_frame, background=colour)
            self.bind("<ButtonRelease-1>", self.clicked)
            self.bind("<Button-1>", lambda _: self.pre_click())

        def clicked(self, event: Event):
            selected = self.grid_.selected

            if self.grid_.inner_frame.winfo_containing(event.x_root, event.y_root) != self:
                self.grid_.process_click(selected, None)
                return

            self.grid_.selected = self.pos
            self.grid_.process_click(selected, self.pos)

        def reachable(self):
            if self.piece is None: return []

            reachable_tiles = set()
            move_types = self.piece.move_types

            for m in move_types:
                to_process = [(self.pos, 0)]

                while to_process:
                    current_tile, index = to_process.pop()

                    if index < m[1]:
                        for t in self.grid_[current_tile].adjacent(m[0]):
                            team1 = self.piece.team if self.piece is not None else None
                            team2 = self.grid_[t].piece.team if self.grid_[t].piece is not None else None

                            if team1 == team2: ...

                            else:
                                if t != self.pos and t not in reachable_tiles: reachable_tiles.add(t)
                                if team2 is None: to_process.append((t, index + 1))

            return reachable_tiles

        def adjacent(self, move_type: Literal["horizontal", "vertical"]):
            x, y = self.pos

            co_ords = []

            if move_type in ["horizontal-e", "spread"]: co_ords.extend([(x + 1, y)])
            if move_type in ["horizontal-w", "spread"]: co_ords.extend([(x - 1, y)])

            if move_type in ["vertical-n", "spread"]: co_ords.extend([(x, y + 1)])
            if move_type in ["vertical-s", "spread"]: co_ords.extend([(x, y - 1)])

            if move_type in ["diagonal-ne"]: co_ords.extend([(x + 1, y + 1)])
            if move_type in ["diagonal-nw"]: co_ords.extend([(x - 1, y + 1)])
            if move_type in ["diagonal-se"]: co_ords.extend([(x + 1, y - 1)])
            if move_type in ["diagonal-sw"]: co_ords.extend([(x - 1, y - 1)])

            if move_type in ["knight"]: co_ords.extend([
                (x + 1, y + 2),
                (x - 1, y + 2),
                (x + 1, y - 2),
                (x - 1, y - 2),

                (x + 2, y + 1),
                (x - 2, y + 1),
                (x + 2, y - 1),
                (x - 2, y - 1),
            ])

            return [tile for tile in co_ords if tile in list(self.grid_.keys())]

        def pre_click(self):
            if self.grid_.selected is None: return

            if self.pos in self.grid_[self.grid_.selected].reachable():
                self.configure(background="#2a9e2a")

            elif self.pos == self.grid_.selected:
                self.configure(background="#1874cc")

    class Piece:
        def __init__(self, name: str, move_types: list[
            tuple[str, int] | tuple[str, int, str]
        ], team: str, king: bool = False):
            self.move_types = move_types
            self.name = name
            self.team = team
            self.king = king

    def process_click(self, tile1: tuple[int, int] | None, tile2: tuple[int, int] | None):
        if self.team is None or not self.running:
            self.selected = None
            return

        elif tile1 == tile2: self.selected = None
        elif tile1 is None and self[tile2].piece is not None and self[tile2].piece.team != self.team: self.selected = None
        elif tile2 is None: ...
        elif tile1 is None and self[tile2].piece is None: self.selected = None
        elif tile1 is None: ...
        elif self[tile2].piece is not None and self[tile1].piece.team == self[tile2].piece.team: self.selected = tile2
        elif tile2 not in self[tile1].reachable(): self.selected = tile1

        else:
            self.selected = None
            tile_2_piece = self[tile2].piece
            self[tile2].piece = self[tile1].piece
            self[tile1].piece = None

            if tile_2_piece is not None and tile_2_piece.king:
                self.check_win(tile_2_piece.team)

            else:
                self.teams = cycle_list(self.teams)
                self.team = self.teams[0]

        if self.running:
            self.update_tiles(self.selected)
            self.check_win()

    def update_tiles(self, tile1: tuple[int, int] = None):
        for pos, tile in self.items():
            if tile.piece is not None and tile.piece.team == self.team:
                tile.configure(foreground="#000000", font="TkDefaultFont 8 bold")
            else: tile.configure(foreground="#000000", font="TkDefaultFont 8")

            if pos == self.selected: tile.configure(background="#1e90ff", foreground="#000000")

            elif tile1 is not None and self[tile1].piece is not None and pos in self[tile1].reachable():
                tile.configure(background="#32cd32")

            else: tile.configure(background=tile.colour)

            if tile.piece is not None: tile.configure(text=tile.piece.name)
            else: tile.configure(text="")

            protect_grid_size(self.inner_frame)

    def place(self, pos: tuple[int, int], piece: "Grid.Piece"):
        self[pos].piece = piece
        self.update_tiles()

    def check_win(self, disqualify_team: str | None = None):
        if disqualify_team in self.teams:
            """
            for tile in self.values():
                if tile.piece is not None and tile.piece.team == disqualify_team: tile.piece = None
            """
            self.teams.remove(disqualify_team)

        if len(self.teams) == 1:
            self.update_tiles(self.selected)
            showinfo(main.title(), f"{self.teams[0].capitalize()} team wins!")
            self.running = False

            self.on_death()


rook = ["horizontal-e", "horizontal-w", "vertical-n", "vertical-s"]
bishop = ["diagonal-ne", "diagonal-nw", "diagonal-se", "diagonal-sw"]

if __name__ == '__main__':
    from anpm.tk import NewTk

    main = NewTk("Grid test")
    main.set_rows(1), main.set_columns(1)

    grid_ = Grid()
    grid_.outer_frame.grid(row=0, column=0, sticky="nsew")

    def chess():
        grid_.update_grid((8, 8), ("#f0d9b5", "#b58863"), ["white", "black"], chess)

        grid_.place((0, 0), grid_.Piece("WHITE ROOK", [(i, 8) for i in rook], "white"))
        grid_.place((1, 0), grid_.Piece("WHITE KNIGHT", [("knight", 1)], "white"))
        grid_.place((2, 0), grid_.Piece("WHITE BISHOP", [(i, 8) for i in bishop], "white"))
        grid_.place((3, 0), grid_.Piece("WHITE QUEEN", [(i, 8) for i in bishop + rook], "white"))
        grid_.place((4, 0), grid_.Piece("WHITE KING", [(i, 1) for i in rook + bishop], "white", True))
        grid_.place((5, 0), grid_.Piece("WHITE BISHOP", [(i, 8) for i in bishop], "white"))
        grid_.place((6, 0), grid_.Piece("WHITE KNIGHT", [("knight", 1)], "white"))
        grid_.place((7, 0), grid_.Piece("WHITE ROOK", [(i, 8) for i in rook], "white"))

        grid_.place((0, 7), grid_.Piece("BLACK ROOK", [(i, 8) for i in rook], "black"))
        grid_.place((1, 7), grid_.Piece("BLACK KNIGHT", [("knight", 1)], "black"))
        grid_.place((2, 7), grid_.Piece("BLACK BISHOP", [(i, 8) for i in bishop], "black"))
        grid_.place((3, 7), grid_.Piece("BLACK QUEEN", [(i, 8) for i in bishop + rook], "black"))
        grid_.place((4, 7), grid_.Piece("BLACK KING", [(i, 1) for i in rook + bishop], "black", True))
        grid_.place((5, 7), grid_.Piece("BLACK BISHOP", [(i, 8) for i in bishop], "black"))
        grid_.place((6, 7), grid_.Piece("BLACK KNIGHT", [("knight", 1)], "black"))
        grid_.place((7, 7), grid_.Piece("BLACK ROOK", [(i, 8) for i in rook], "black"))

    chess()

    main.mainloop()
