import argparse
import os
from default_cog import *


def setup(args: dict):
    name = args.get("name") or ""
    main = args.get("main") or ""
    cogs_folder = args.get("cog_folder")
    cog_dir = os.path.join(cogs_folder, name)
    print(f"""Creating the cog with these parameters :
Cog name: {name}
Main filename: {main}
Cogs folder: {cogs_folder}
Cog directory: {cog_dir}
""")
    if not name:
        raise ValueError("The name of the cog is invalid.")
    if not main or len(os.path.splitext(main)) < 1:
        raise ValueError("The main file name is invalid.")
    if not os.path.exists(cogs_folder):
        raise FileNotFoundError("Cogs folder does not exist.")

    print(f"Creating the directory '{cog_dir}'...")
    os.mkdir(cog_dir)

    with open(f"{os.path.join(cog_dir, 'cog.yml')}", "w") as yml_file:
        print(f"Creating 'cog.yml' to: '{os.path.join(cog_dir, 'cog.yml')}'")
        yml_file.write(YML_FILE.format(name=name, main=os.path.splitext(main)[0]))

    with open(f"{os.path.join(cog_dir, main)}", "w") as main_file:
        print(f"Creating the main file of '{name}' cog to: '{os.path.join(cog_dir, main)}'")
        main_file.write(COG_FILE.format(name=name))

    print(f"Cog '{name}' created with success !")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", "-N", type=str, help="The name of the cog.")
    parser.add_argument("--main", "-M", type=str, help="The main file of the cog.")
    parser.add_argument("--cog-folder", "-CF", type=str, default=DEFAULT_COGS_FOLDER,
                        help=f"The cogs folder. (Default value : {DEFAULT_COGS_FOLDER})")

    args = vars(parser.parse_args())
    setup(args)
