from json import dump, load
from os import makedirs
from os.path import join, exists
from typing import Optional as Op

from anpm import aliaFolder
from requests import get
from requests.exceptions import ConnectionError

ygo_folder = join(aliaFolder, "Yu-Gi-Oh")
makedirs(ygo_folder, exist_ok=True)


def get_dump_return(data_url, file_path, ignore_exist=False):
    def get_return():
        data_ = get(data_url).json()
        dump(data_, open(file_path, "w"), indent=2)
        return data_

    def load_return():
        return load(open(file_path))

    if ignore_exist and exists(file_path):
        data = load_return()

    else:
        try:
            data = get_return()
        except ConnectionError:
            data = load_return()

    return data


card_info: list[dict] = \
    get_dump_return("https://db.ygoprodeck.com/api/v7/cardinfo.php",
                    join(ygo_folder, "cards.json"), True)["data"]
card_info_by_name = {c["name"]: c for c in card_info}

card_sets: dict = get_dump_return(
    "https://db.ygoprodeck.com/api/v7/cardsets.php", join(ygo_folder, "sets.json"), True)
card_sets_by_name = {s["set_name"]: s for s in card_sets}


def forceReload():
    global card_info, card_info_by_name, card_sets, card_sets_by_name

    card_info = get_dump_return(
        "https://db.ygoprodeck.com/api/v7/cardinfo.php", join(ygo_folder, "cards.json"))["data"]
    card_info_by_name = {c["name"]: c for c in card_info}

    card_sets = get_dump_return(
        "https://db.ygoprodeck.com/api/v7/cardsets.php", join(ygo_folder, "sets.json"))
    card_sets_by_name = {s["set_name"]: s for s in card_sets}


class Card:
    # noinspection SpellCheckingInspection
    def __init__(self, raw_dict: dict):
        self.rawDict: dict = raw_dict

        #

        self._id: int = raw_dict["id"]
        self._name: str = raw_dict["name"]
        self._type: str = raw_dict["type"]
        self._humanReadableCardType: str = raw_dict["humanReadableCardType"]
        self._frameType: str = raw_dict["frameType"]
        self._desc: str = raw_dict["desc"]
        self._race: str = raw_dict["race"]
        self._ygoprodeck_url: str = raw_dict["ygoprodeck_url"]
        self._card_images: list[dict[str]] = raw_dict["card_images"]
        self._card_prices: list = raw_dict["card_prices"]

        self._archetype: Op[str] = raw_dict.get("archetype")
        self._card_sets: Op[list] = raw_dict.get("card_sets")
        self._typeline: Op[list[str]] = raw_dict.get("typeline")
        self._atk: Op[int] = raw_dict.get("atk")
        self._def: Op[int] = raw_dict.get("def")
        self._level: Op[int] = raw_dict.get("level")
        self._attribute: Op[str] = raw_dict.get("attribute")
        self._linkval: Op[int] = raw_dict.get("linkval")
        self._linkmarkers: Op[list] = raw_dict.get("linkmarkers")
        self._pend_desc: Op[str] = raw_dict.get("pend_desc")
        self._monster_desc: Op[str] = raw_dict.get("monster_desc")
        self._scale: Op[int] = raw_dict.get("scale")
        self._banlist_info: Op[dict] = raw_dict.get("banlist_info")

        #

        self.name: str = self._name
        self.id: int = self._id
        self.type: str = self._type

        #

        self.earliestReleaseDate: Op[str] = self.get_earliest_date()
        self.croppedImages: list[str] = [
            i["image_url_cropped"] for i in self._card_images]

    def __repr__(self):
        return f"{type(self).__name__}({self.name})"

    def get_earliest_date(self):
        sets = self._card_sets
        if not sets:
            return
        return card_sets_by_name[sets[0]["set_name"]]["tcg_date"]


cardDatabase: list[Card] = [Card(c) for c in card_info]


def get_unique_values():
    from time import time

    path = join(ygo_folder, "unique_values.json")

    if not exists(path):
        value_ranges = {}

        x = 0
        len_card_info = len(card_info)

        start_time = time()

        for c in cardDatabase:
            x += 1
            print(f"{x / len_card_info * 100:.2f}%")

            for k, v in c.__dict__.items():
                if not k.startswith("_") or k.startswith("__"):
                    continue

                if k not in value_ranges.keys():
                    value_ranges[k] = []
                if v not in value_ranges[k]:
                    value_ranges[k].append(v)

        end_time = time()
        elapsed_time = end_time - start_time

        print(f"Finished in {elapsed_time:.2f} seconds!")

        # noinspection SpellCheckingInspection
        dump({k: v for k, v in value_ranges.items() if k not in [
            "_desc",
            "_ygoprodeck_url",
            "_card_images",
            "_card_prices",
            "_card_sets",
            "_card_prices",
            "_pend_desc",
            "_monster_desc",
        ]}, open(path, "w"), indent=2)

    value_ranges = load(open(path))

    return value_ranges


__all__ = ["card_info", "card_sets", "cardDatabase", "get_unique_values"]


def main():
    from collections import defaultdict
    from anpm import default

    archetypes = get_unique_values()["_archetype"]
    archetypes = sorted(
        [a for a in archetypes if isinstance(a, str)], key=lambda a: a.lower())

    targets = ["A-to-Z", "ABC"]
    targets = ["Galaxy", "Galaxy-Eyes", "Tachyon"]

    foundCards = []

    for c in cardDatabase:
        if c._archetype in targets:
            foundCards.append(c)

    longestKeys = defaultdict(int)

    for c in foundCards:
        for k, v in c.__dict__.items():
            v_len = len(str(v))
            if v_len > longestKeys[k]:
                longestKeys[k] = v_len

    foundCards = sorted(foundCards, key=lambda c: default(c._level, -2))

    def get_ljust_string(c, k): return f"{c.__dict__[k]}".ljust(
        longestKeys[k], " ")
    gljs = get_ljust_string

    format_c = lambda c, keys=["_name"]: " | ".join(map(str, [gljs(c, k) for k in c.__dict__.keys() if k in keys]))

    print(*[format_c(c, ["_name", "_atk", "_def", "_level"]) for c in foundCards], sep="\n")


if __name__ == '__main__':
    main()
