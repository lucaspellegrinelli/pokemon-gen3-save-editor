import sys

from saveeditor.saveeditor import set_pokemon_levels

if __name__ == "__main__":
    input_path = sys.argv[1]
    new_sav = set_pokemon_levels(input_path, 100)

    out_path = input_path.split(".")[0] + "_new.sav"
    with open(out_path, "wb") as f:
        f.write(new_sav)
