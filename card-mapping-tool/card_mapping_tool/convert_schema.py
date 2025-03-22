import json

tiles_data = {}
with open("tiles.json") as file:
    tiles_data = json.load(file)

deck_tiles_data = []
central_housing_color_mappings = {}

for k, v in tiles_data.items():
    if not v["tile_type"].endswith("CentralHousingUnitTile"):
        new_tile = {
            "className": v["tile_type"],
            "data": {"assetIdentifier": k, "sideConnectors": list(map(lambda x: x.upper(), v["connectors"]))},
        }
        deck_tiles_data.append(new_tile)
    else:
        color = v["tile_type"].split("CentralHousingUnitTile")[0].upper()
        central_housing_color_mappings[color] = k

with open("deck.json", "w") as file:
    json.dump(deck_tiles_data, file, indent=4)

with open("central_housing_asset_map.json", "w") as file:
    json.dump(central_housing_color_mappings, file, indent=4)
