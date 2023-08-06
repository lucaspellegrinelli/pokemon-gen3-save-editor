import sys

from saveeditor.saveeditor import set_pokemon_levels

input_file = sys.argv[1]
output_file = f"{input_file}.new"

is_frlg = sys.argv[2] == "frlg"

with open(input_file, "rb") as f:
    data = f.read()
    new_data = set_pokemon_levels(data, is_frlg, 100)

with open(output_file, "wb") as f:
    f.write(new_data)
