import glob
print(glob.glob("**/fields.json", recursive=True))
print(glob.glob("**/*.csv", recursive=True))
