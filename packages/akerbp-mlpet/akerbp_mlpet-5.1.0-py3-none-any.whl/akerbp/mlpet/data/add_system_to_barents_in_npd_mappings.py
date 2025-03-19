import pickle
from importlib.resources import path
from pathlib import Path

import akerbp.mlpet.data
from akerbp.mlpet.utilities import read_pickle

with path(akerbp.mlpet.data, "npd_fm_gp_sy_key_dic.pcl") as f:
    npd_mapping = read_pickle(f)

for key, val in npd_mapping.items():
    if val["LEVEL"] == "GROUP":
        if not isinstance(val["GRANDPARENT"], str):
            if key == "ADVENTDALEN":
                val["GRANDPARENT"] = "JURASSIC SY"
            elif key == "BILLEFJORDEN":
                val["GRANDPARENT"] = "DEVIONIAN SY"
            elif key == "BJARMELAND":
                val["GRANDPARENT"] = "PERMIAN SY"
            elif key == "GIPSDALEN":
                val["GRANDPARENT"] = "CARBONIFEROUS SY"
            elif key == "KAPP":
                val["GRANDPARENT"] = "TRIASSIC SY"
            elif key == "NYGRUNNEN":
                val["GRANDPARENT"] = "CRETACEOUS SY"
            elif key == "SASSENDALEN":
                val["GRANDPARENT"] = "TRIASSIC SY"
            elif key == "SOTBAKKEN":
                val["GRANDPARENT"] = "PALEOGENE SY"
            elif key == "TEMPELFJORDEN":
                val["GRANDPARENT"] = "PERMIAN SY"
            else:
                print(f"Will not change '{key}' ")

for val in npd_mapping.values():
    if val["LEVEL"] == "GROUP":
        if not isinstance(val["GRANDPARENT"], str):
            print(f"Still missing grandparent for {val['NAME']}")

for val in npd_mapping.values():
    if val["LEVEL"] == "GROUP" and isinstance(val["GRANDPARENT"], str):
        print(f"{val['NAME']} is in {val['GRANDPARENT']}")


for val in npd_mapping.values():
    if val["LEVEL"] == "FORMATION":
        if not isinstance(val["GRANDPARENT"], str):
            print(f"Missing grandparent for {val['NAME']}, with parent {val['PARENT']}")

for key, val in npd_mapping.items():
    if val["LEVEL"] == "FORMATION":
        if not isinstance(val["GRANDPARENT"], str):
            if val["PARENT"] == "ADVENTDALEN GP":
                val["GRANDPARENT"] = "JURASSIC SY"
            elif val["PARENT"] == "BILLEFJORDEN GP":
                val["GRANDPARENT"] = "DEVIONIAN SY"
            elif val["PARENT"] == "BJARMELAND GP":
                val["GRANDPARENT"] = "PERMIAN SY"
            elif val["PARENT"] == "GIPSDALEN GP":
                val["GRANDPARENT"] = "CARBONIFEROUS SY"
            elif val["PARENT"] in [
                "KAPP TOSCANA GP",
                "STORFJORDEN SUBGP",
                "REALGRUNNEN SUBGP",
            ]:
                val["GRANDPARENT"] = "TRIASSIC SY"
            elif val["PARENT"] == "NYGRUNNEN GP":
                val["GRANDPARENT"] = "CRETACEOUS SY"
            elif val["PARENT"] == "SASSENDALEN GP":
                val["GRANDPARENT"] = "TRIASSIC SY"
            elif val["PARENT"] == "SOTBAKKEN GP":
                val["GRANDPARENT"] = "PALEOGENE SY"  # we dont have a mapping for this
            elif val["PARENT"] == "TEMPELFJORDEN GP":
                val["GRANDPARENT"] = "PERMIAN SY"
            else:
                print(f"Will not change '{key}': {val['PARENT']}")

for val in npd_mapping.values():
    if val["LEVEL"] == "FORMATION":
        if not isinstance(val["GRANDPARENT"], str):
            print(f"Missing grandparent for {val['NAME']}, with parent {val['PARENT']}")

for val in npd_mapping.values():
    if val["LEVEL"] == "FORMATION" and isinstance(val["GRANDPARENT"], str):
        print(f"{val['NAME']} is in {val['GRANDPARENT']}")


with path(akerbp.mlpet.data, "npd_fm_gp_sy_key_dic.pcl") as f:
    outfile = Path(f).open("wb")
    pickle.dump(npd_mapping, outfile)
    outfile.close()
