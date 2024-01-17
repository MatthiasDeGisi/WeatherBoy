import os

os.system("curl -o output.txt https://www.wunderground.com/dashboard/pws/IGABRI5")

with open("output.txt", 'r', errors='replace') as f:
    darren = f.read()

os.system("curl -o output.txt https://www.wunderground.com/dashboard/pws/IEXTEN1")
    
with open("output.txt", 'r', errors='replace') as f:
    brandon = f.read()
    
if "goldstar" in darren and "goldstar" in brandon:
    print("Both Win!")
elif "goldstar" in darren:
    print("Darren Wins!")
elif "goldstar" in brandon:
    print("Brandon Wins!")
else:
    ("Womp Womp!")
    
with open("output.txt", 'w') as f:
    pass