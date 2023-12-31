from .utils.binutils import get_offseted, h2i, i2h, set_offseted
from .utils.pokemonutils import (calculate_hp_stat, calculate_other_stat,
                                 game_nature_id_to_name,
                                 get_pokemon_base_stats, get_pokemon_max_xp)
from .utils.savedatautils import (get_evs_chunk, get_growth_chunk,
                                  get_misc_chunk)


def calculate_section_checksum(section_data):
    section_checksum = 0
    for i in range(0, len(section_data), 4):
        section_checksum += h2i(" ".join(section_data[i : i + 4]))

    upper_16_bits = section_checksum >> 16
    lower_16_bits = section_checksum & 0xFFFF
    return (upper_16_bits + lower_16_bits) & 0xFFFF

def is_firered_or_leafgreen(save_data):
    As = 0x2000
    Bs = 0xF000
    l = 3968 + 2 + 2 + 4 + 4
    A_section_0 = save_data[As : As + l].hex().upper()
    B_section_0 = save_data[Bs : Bs + l].hex().upper()
    A_game_code = h2i(" ".join(get_offseted(A_section_0, 0xAC, 4)))
    B_game_code = h2i(" ".join(get_offseted(B_section_0, 0xAC, 4)))
    return A_game_code == 1 or B_game_code == 1


def set_pokemon_levels(save_data, new_level=100):
    is_frlg = is_firered_or_leafgreen(save_data)
    print("is_frlg", is_frlg)

    A_section_start = 0x3000
    A_section_end = A_section_start + 0xFFC + 4

    B_section_start = 0x10000
    B_section_end = B_section_start + 0xFFC + 4

    A_section_contents = save_data[A_section_start:A_section_end].hex().upper()
    B_section_contents = save_data[B_section_start:B_section_end].hex().upper()

    A_section_save_idx = get_offseted(A_section_contents, 0xFFC, 4)
    B_section_save_idx = get_offseted(B_section_contents, 0xFFC, 4)

    A_idx = h2i(" ".join(A_section_save_idx))
    B_idx = h2i(" ".join(B_section_save_idx))

    A_idx = A_idx if A_idx < 9999 else -1
    B_idx = B_idx if B_idx < 9999 else -1

    section_start = A_section_start
    section_end = A_section_end
    if A_idx < B_idx:
        print("Section start:", B_section_start)
        section_start = B_section_start
        section_end = B_section_end
    else:
        print("Section start:", A_section_start)

    section_contents = save_data[section_start:section_end].hex().upper()

    section_data = get_offseted(section_contents, 0, 3968)
    section_id = get_offseted(section_contents, 0xFF4, 2)
    section_checksum = get_offseted(section_contents, 0xFF6, 2)
    section_signature = get_offseted(section_contents, 0xFF8, 4)

    assert section_id == ["01", "00"]
    assert section_signature == ["25", "20", "01", "08"]
    assert calculate_section_checksum(section_data) == h2i(" ".join(section_checksum))

    TEAM_SIZE_OFFSET = 0x34 if is_frlg else 0x234
    TEAM_LIST_OFFSET = 0x38 if is_frlg else 0x238

    pokemon_count = h2i(" ".join(section_data[TEAM_SIZE_OFFSET : TEAM_SIZE_OFFSET + 4]))
    team_pokemon_list_data = section_data[TEAM_LIST_OFFSET : TEAM_LIST_OFFSET + 600]
    mod_team_pokemon_list_data = team_pokemon_list_data.copy()

    for pokemon_index in range(pokemon_count):
        pokemon_data = team_pokemon_list_data[
            pokemon_index * 100 : (pokemon_index + 1) * 100
        ]

        personality = " ".join(pokemon_data[0:4])
        orig_trainer_id = " ".join(pokemon_data[4:8])
        read_checksum = " ".join(pokemon_data[28:30])
        data = " ".join(pokemon_data[32:80])
        # level = " ".join(pokemon_data[84:85])
        pokerus = " ".join(pokemon_data[85:86])
        # curr_hp = " ".join(pokemon_data[86:88])
        # total_hp = " ".join(pokemon_data[88:90])
        # attack = " ".join(pokemon_data[90:92])
        # defense = " ".join(pokemon_data[92:94])
        # speed = " ".join(pokemon_data[94:96])
        # sp_attack = " ".join(pokemon_data[96:98])
        # sp_defense = " ".join(pokemon_data[98:100])

        substructure_order = h2i(personality) % 24
        decrypt_key = h2i(orig_trainer_id) ^ h2i(personality)

        decrypted_data = ""
        data_chunks = data.split(" ")
        for i in range(0, len(data_chunks), 4):
            local_chunk = " ".join(data_chunks[i : i + 4])
            local_value = decrypt_key ^ h2i(local_chunk)
            decrypted_data += i2h(local_value) + " "

        decrypted_data = decrypted_data.strip()
        decrypted_bytes = decrypted_data.split(" ")

        checksum_parcels = []
        for i in range(0, len(decrypted_bytes), 2):
            val = h2i(f"{decrypted_bytes[i]} {decrypted_bytes[i + 1]}")
            checksum_parcels.append(val)

        checksum = sum(checksum_parcels) & 0xFFFF

        assert checksum == h2i(read_checksum)

        gci = get_growth_chunk(substructure_order)
        growth_chunk = decrypted_data.split(" ")[gci * 12 : (gci + 1) * 12]

        eci = get_evs_chunk(substructure_order)
        evs_chunk = decrypted_data.split(" ")[eci * 12 : (eci + 1) * 12]

        mci = get_misc_chunk(substructure_order)
        misc_chunk = decrypted_data.split(" ")[mci * 12 : (mci + 1) * 12]

        species = h2i(" ".join(growth_chunk[0:2]))
        if species > 251:
            species -= 25

        # item = " ".join(growth_chunk[2:4])
        # xp = h2i(" ".join(growth_chunk[4:8]))

        hp_ev = h2i(" ".join(evs_chunk[0:1]))
        atk_ev = h2i(" ".join(evs_chunk[1:2]))
        def_ev = h2i(" ".join(evs_chunk[2:3]))
        spe_ev = h2i(" ".join(evs_chunk[3:4]))
        spa_ev = h2i(" ".join(evs_chunk[4:5]))
        spd_ev = h2i(" ".join(evs_chunk[5:6]))

        ivs_bytes = " ".join(misc_chunk[4:8])
        ivs_val = h2i(ivs_bytes)
        ivs_bits = "{:032b}".format(ivs_val)

        hp_iv = int(ivs_bits[-5:], 2)
        atk_iv = int(ivs_bits[-10:-5], 2)
        def_iv = int(ivs_bits[-15:-10], 2)
        spe_iv = int(ivs_bits[-20:-15], 2)
        spa_iv = int(ivs_bits[-25:-20], 2)
        spd_iv = int(ivs_bits[-30:-25], 2)

        # print()
        # print(" --- Pokemon Stats --- ")
        # print("Species\t\t", species)
        # print("Experience\t", xp)
        # print("Level\t\t", h2i(level))
        # print("HPt\t\t", f"{h2i(curr_hp)}/{h2i(total_hp)} \t\t({hp_ev} EV, {hp_iv} IV)")
        # print("Attack\t\t", f"{h2i(attack)} \t\t({atk_ev} EV, {atk_iv} IV)")
        # print("Defense\t\t", f"{h2i(defense)} \t\t({def_ev} EV, {def_iv} IV)")
        # print("Speed\t\t", f"{h2i(speed)} \t\t({spe_ev} EV, {spe_iv} IV)")
        # print("Sp. Attack\t", f"{h2i(sp_attack)} \t\t({spa_ev} EV, {spa_iv} IV)")
        # print("Sp. Defense\t", f"{h2i(sp_defense)} \t\t({spd_ev} EV, {spd_iv} IV)")
        # print()

        nature = h2i(personality) % 25
        nature_name = game_nature_id_to_name(nature)

        (
            base_hp,
            base_atk,
            base_def,
            base_spe,
            base_spa,
            base_spd,
        ) = get_pokemon_base_stats(species)

        new_xp = get_pokemon_max_xp(species)

        new_hp = calculate_hp_stat(base_hp, hp_iv, hp_ev, new_level)
        new_atk = calculate_other_stat(
            "attack", base_atk, atk_iv, atk_ev, new_level, nature_name
        )
        new_def = calculate_other_stat(
            "defense", base_def, def_iv, def_ev, new_level, nature_name
        )
        new_spe = calculate_other_stat(
            "speed", base_spe, spe_iv, spe_ev, new_level, nature_name
        )
        new_spa = calculate_other_stat(
            "special-attack", base_spa, spa_iv, spa_ev, new_level, nature_name
        )
        new_spd = calculate_other_stat(
            "special-defense", base_spd, spd_iv, spd_ev, new_level, nature_name
        )

        # print(" --- New Pokemon Stats --- ")
        # print("Species\t\t", species)
        # print("Experience\t", new_xp)
        # print("Level\t\t", 100)
        # print("HP\t\t", f"{new_hp}/{new_hp} \t\t({hp_ev} EV, {hp_iv} IV)")
        # print("Attack\t\t", f"{new_atk} \t\t({atk_ev} EV, {atk_iv} IV)")
        # print("Defense\t\t", f"{new_def} \t\t({def_ev} EV, {def_iv} IV)")
        # print("Speed\t\t", f"{new_spe} \t\t({spe_ev} EV, {spe_iv} IV)")
        # print("Sp. Attack\t", f"{new_spa} \t\t({spa_ev} EV, {spa_iv} IV)")
        # print("Sp. Defense\t", f"{new_spd} \t\t({spd_ev} EV, {spd_iv} IV)")
        # print()

        xpi = gci * 6 + 2
        nxp_b = i2h(new_xp).split(" ")
        nxp_0 = h2i(" ".join(nxp_b[0:2]))
        nxp_1 = h2i(" ".join(nxp_b[2:4]))

        encrypted_nxp = new_xp ^ decrypt_key

        checksum_parcels[xpi + 0] = nxp_0
        checksum_parcels[xpi + 1] = nxp_1
        new_checksum = sum(checksum_parcels) % (0xFFFF + 1)

        new_stats_hexes = " ".join(
            [
                i2h(new_level, 2),
                pokerus,
                i2h(new_hp, 4),
                i2h(new_hp, 4),
                i2h(new_atk, 4),
                i2h(new_def, 4),
                i2h(new_spe, 4),
                i2h(new_spa, 4),
                i2h(new_spd, 4),
            ]
        )

        mod_pokemon_data = pokemon_data.copy()

        mod_pokemon_data[28 : 28 + 2] = i2h(new_checksum, 4).split(" ")
        print("New Checksum Hex:", i2h(new_checksum, 4))

        xp_loc = 32 + gci * 12 + 4
        mod_pokemon_data[xp_loc : xp_loc + 4] = i2h(encrypted_nxp).split(" ")
        print("New XP Hex:", i2h(encrypted_nxp))

        mod_pokemon_data[84:100] = new_stats_hexes.split(" ")
        print("New Stats Hex:", new_stats_hexes)

        mod_team_pokemon_list_data[
            pokemon_index * 100 : (pokemon_index + 1) * 100
        ] = mod_pokemon_data

    mod_section_data = section_data.copy()
    mod_section_data[
        TEAM_LIST_OFFSET : TEAM_LIST_OFFSET + 600
    ] = mod_team_pokemon_list_data
    new_section_checksum = i2h(calculate_section_checksum(mod_section_data), 4).split(
        " "
    )
    print("\nNew Section Checksum:", " ".join(new_section_checksum))

    mod_section_contents = section_contents[:]
    mod_section_contents = set_offseted(mod_section_contents, 0, mod_section_data)
    mod_section_contents = set_offseted(
        mod_section_contents, 0xFF6, new_section_checksum
    )

    mod_section_contents_bytes = bytes.fromhex(mod_section_contents)

    mod_save_data = bytearray(save_data[:])
    mod_save_data[section_start:section_end] = mod_section_contents_bytes

    return mod_save_data
