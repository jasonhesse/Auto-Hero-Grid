import argparse, requests, json, os, datetime

parser = argparse.ArgumentParser()
parser.add_argument('-path','-p',type=str,required=True,help="Required. STEAM_INSTALL/userdata/USER_ID/570/remote/cfg/hero_grid_config.json")
parser.print_help(); print(); args = parser.parse_args()

date_str = datetime.date.today().strftime(" %d-%m-%Y")
spec_url = 'https://stats.spectral.gg/lrg2/api/?pretty&league=imm_ranked_meta_last_7&mod=heroes-positions-position_'
spec_positions = {"Core Safelane":"1.1","Core Midlane":"1.2","Core Offlane":"1.3","Support":"0.0"}
rank_cutoffs = [100,95,90,85,80,75]; tiers = ["S","A","B","C","D"]

# open grid config and delete existing if desired
if os.path.isfile(args.path):
    try:
        with open(args.path) as f: grid_conf = json.load(f)
        grid_conf["configs"] = [c for c in grid_conf["configs"] if "S!" != c["config_name"][:2]]
        print("Grid config loaded.")
    except: print("Couldn't load the grid config."); quit()
else:
    grid_conf = {"version":3,"configs":[]}
    print("Creating new Grid Config file.")

# update the grid config with each position's data from spectral.gg
for pos_name,pos_endpoint in spec_positions.items():
    try: hero_data = json.loads(requests.get(spec_url+pos_endpoint).content)["result"][pos_endpoint]
    except: print("\nFailed to load data from spectral.gg"); quit()
    hero_ranks = [(data["rank"],hero_id) for hero_id,data in hero_data.items()]
    hero_ranks.sort(key=lambda x:-x[0])
    pos_conf = {"config_name": 'S! ' + pos_name + date_str,
                "categories": [{"category_name":tiers[i]+" tier - rank %s+"%rank_cutoffs[i+1],
                                "x_position":0, "y_position":i*120,"width":1000,"height":100,
                                "hero_ids":[id for rank,id in hero_ranks if rank_cutoffs[i] >= rank > rank_cutoffs[i+1]]}
                               for i in range(5)]}
    grid_conf["configs"].append(pos_conf)
    print("Processed",pos_name+'.')

# write grid conf
try:
    with open(args.path, "w") as f: print(json.dumps(grid_conf, indent=4), file=f)
    print("Grid Config has been written.")
except: print("Couldn't write the grid config.")