Dragon-City-Habitat-Sorter

Do you play Dragon City?
Having trouble organizing your dragons into their best habitats?

Look no further! 🐉

This Python project helps you automatically sort your dragons into the most suitable habitats, while also keeping track of any overflow that doesn’t fit.

Features
- Takes a list of your dragons (name, level, stars, types).
- Sorts them by highest type.
- Matches them to their best potential habitats.
- Outputs a text file showing where each dragon belongs.
- Notes overflow dragons that couldn’t be placed in existing habitats.

Setup & Requirements
- Python 3.8+
- Libraries: csv, re (standard library, no extra install needed)

How to Use
1. Download the project files:
   dragon_sorter.py (main program)
   dragons.csv (your dragon list)
   habitats.csv (list of available habitats)
2. Fill in the spreadsheets:
   Open dragons.csv and enter your dragons’ details.
   Open habitats.csv and enter the habitats you own, with their capacity and elements.
3. Run the program:
   python main.py
4. Check results:
   Two text files are generated: sorted_dragons.txt and sorted_habitats.txt

Example
Input (dragons.csv):
  Name,Level,Stars,Types
  Legacy Dragon,25,0,Legend
  Air Dragon,1,1,Legend
  Hunter Dragon,40,5,"Legend, Nature"

Output (sorted_dragons.txt):
  Legend (3 Dragons):
    Legacy Dragon (Lv 25, 0*, Legend)
    Air Dragon (Lv 1, 1*, Legend)
    Hunter Dragon (Lv 40, 5*, Legend, Nature)

Output (sorted_habitats.txt):
  Legend (available spaces: 4)
    Legacy Dragon (Lv 25, 0*, Legend)
    Air Dragon (Lv 1, 1*, Legend)
    Hunter Dragon (Lv 40, 5*, Legend, Nature)

Future Improvements
- GUI for selecting dragons based on the in-game Dragon Book
- Maximize gold production
