import csv
import re
from collections import defaultdict

class Dragon:
    def __init__(self, name, level, stars, types):
        self.name = name.strip()
        # be resilient if level/stars are empty
        self.level = int(level) if str(level).strip() else 0
        self.stars = int(stars) if str(stars).strip() else 0

        # Robust splitting: accept | , / ; as separators and trim whitespace
        self.types = []
        if types is not None:
            parts = re.split(r'\s*(?:\||/|;|,)\s*', types)
            self.types = [p.strip() for p in parts if p.strip()]

    def __repr__(self):
        return f"{self.name} (Lv {self.level}, {self.stars}*, {', '.join(self.types)})"


def load_dragons(filename):
    dragons = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            # skip empty rows
            if not row.get("Dragon Name", "").strip():
                continue
            dragons.append(Dragon(
                name=row.get("Dragon Name", "").strip(),
                level=row.get("Level", "").strip(),
                stars=row.get("Stars", "").strip(),
                types=row.get("Type(s)", "").strip()
            ))
    return dragons


# Your ranking (keep this as you like)
HABITAT_RANKING = {
    "Legend": 1,
    "Soul": 2,
    "Pure": 3,
    "Primal": 4,
    "Dream": 5,
    "War": 6,
    "Happiness": 7,
    "Beauty": 8,
    "Wind": 9,
    "Chaos": 10,
    "Magic": 11,
    "Light": 12,
    "Dark": 13,
    "Metal": 14,
    "Ice": 15,
    "Electric": 16,
    "Nature": 17,
    "Sea": 18,
    "Flame": 19,
    "Terra": 20,
}

# Prepare lowercase lookup + canonical name map so matching is case-insensitive
RANKING_LOWER = {k.lower(): v for k, v in HABITAT_RANKING.items()}
CANONICAL_NAME = {k.lower(): k for k in HABITAT_RANKING.keys()}

# Aliases (map other type names to existing ones)
TYPE_ALIASES = {
    "time": "legend",   # Treat "Time" like "Legend"
    # add more aliases here if needed
}

def best_habitat(dragon):
    """Return (canonical_habitat_name, rank) for the best type, or (None, None)."""
    best_type_lower = None
    best_rank = None
    for t in dragon.types:
        t_norm = t.strip().lower()
        # apply alias if exists
        t_norm = TYPE_ALIASES.get(t_norm, t_norm)

        rank = RANKING_LOWER.get(t_norm)
        if rank is None:
            continue
        if best_rank is None or rank < best_rank:
            best_rank = rank
            best_type_lower = t_norm
    if best_type_lower is None:
        return None, None
    return CANONICAL_NAME[best_type_lower], best_rank

def dragon_sort_key(dragon):
    """Return numeric rank (lower is better). Unranked => large number so they fall to the end."""
    _, rank = best_habitat(dragon)
    return rank if rank is not None else 999


def habitat_sort_key(item):
    """Sort HABITAT_RANKING.items() by rank (helper used for ordered iteration)."""
    habitat, rank = item
    return rank


def sortbyhabitat(dragons, output_file="sorted_dragons.txt"):
    # Sort by dragon habitat rank (best type)
    dragons_sorted = sorted(dragons, key=dragon_sort_key)

    # Group by best habitat type
    grouped = {}
    unsorted = []
    for d in dragons_sorted:
        best_type, rank = best_habitat(d)
        if best_type is None:
            unsorted.append(d)
        else:
            grouped.setdefault(best_type, []).append(d)

    # Write to file (UTF-8)
    with open(output_file, "w", encoding="utf-8") as f:

        f.write("How your dragons should be organized\n")
        f.write(f"Total dragons: {len(dragons)}\n\n")

        for habitat, rank in sorted(HABITAT_RANKING.items(), key=habitat_sort_key):
            if habitat in grouped:
                dragons_in_group = grouped[habitat]
                count = len(dragons_in_group)
                # grammar: "1 dragon" vs "N dragons"
                header = f"{habitat} Habitats ({count} dragon):" if count == 1 else f"{habitat} Habitats ({count} dragons):"
                f.write(f"\n{header}\n")
                for d in dragons_in_group:
                    f.write(f"  {d}\n")

        if unsorted:
            count = len(unsorted)
            header = f"Unsorted Dragons ({count} dragon):" if count == 1 else f"Unsorted Dragons ({count} dragons):"
            f.write(f"\n{header}\n")
            for d in unsorted:
                f.write(f"  {d}\n")

    print(f"Dragons sorted and saved to {output_file}")


def load_habitats(filename):
    habitats = []
    with open(filename, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Accept either "Avaliable Spaces" or "Available Spaces" just in case
            spaces_key = "Avaliable Spaces" if "Avaliable Spaces" in row else "Available Spaces"
            habitats.append({
                "habitat": row["Habitat"].strip(),
                "level": int(row["Level"]),
                "quantity": int(row["Quantity"]),
                "spaces_per_habitat": int(row.get(spaces_key, 0))  # note spelling in CSV
            })
    return habitats


def total_spaces_by_habitat(habitats):
    combined = {}
    for h in habitats:
        name = h["habitat"]
        if name in ("Divine", "Rainbow"):  # skip these
            continue
        total_spaces = h["quantity"] * h["spaces_per_habitat"]
        combined.setdefault(name, 0)
        combined[name] += total_spaces
    return combined


def organize_dragons_into_habitats(dragons, habitats, output_file="organized_habitats.txt"):
    """
    Place dragons into THEIR BEST habitat first (based on HABITAT_RANKING).
    For each habitat (in ranking order) we:
      - compute total available spaces (sum quantity * spaces_per_habitat)
      - place dragons whose best_habitat == that habitat, up to available spaces
      - list any overflow for that habitat (with a blank line before Overflow)
    At the end we report totals and list unplaced dragons (no matching habitat).
    """
    # combined: habitat -> total available slots (summed across rows)
    combined = total_spaces_by_habitat(habitats)

    # group dragons by their best habitat
    grouped = defaultdict(list)
    unsorted = []  # dragons with no ranked habitat
    for d in dragons:
        best_type, _ = best_habitat(d)
        if best_type is None:
            unsorted.append(d)
        else:
            grouped[best_type].append(d)

    total_placed = 0
    total_not_placed = 0

    # helper: sort dragons within a habitat by strength (level desc, stars desc, name)
    def sort_dragon_strength(dragon):
        # negative for descending
        return (-dragon.level, -dragon.stars, dragon.name.lower())

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("How your dragons should be placed into habitats\n")
        f.write(f"Total dragons: {len(dragons)}\n\n")

        # iterate habitats in your ranking order
        for habitat, _rank in sorted(HABITAT_RANKING.items(), key=habitat_sort_key):
            # total spaces for this habitat (0 if not present)
            spaces = combined.get(habitat, 0)
            dragons_for = grouped.get(habitat, [])

            # only print a habitat header if there's something relevant:
            # either dragons exist for it OR there are available spaces (so you can see spaces)
            if not dragons_for and spaces == 0:
                continue

            # sort dragons by strength so best ones fill spaces first
            dragons_for_sorted = sorted(dragons_for, key=sort_dragon_strength)

            placed = dragons_for_sorted[:spaces]
            overflow = dragons_for_sorted[spaces:]

            f.write(f"\n{habitat} (available spaces: {spaces})\n")
            for d in placed:
                f.write(f"  {d}\n")

            if overflow:
                f.write("\n")  # blank line before Overflow (as you requested)
                f.write(f"Overflow ({len(overflow)} dragons didn’t fit):\n")
                for d in overflow:
                    f.write(f"    {d}\n")

            total_placed += len(placed)
            total_not_placed += len(overflow)

        # add unsorted (no matching habitat) to not placed totals and list them
        if unsorted:
            total_not_placed += len(unsorted)

        f.write(f"\nTotal dragons placed: {total_placed}\n")
        f.write(f"Total dragons not placed: {total_not_placed}\n")

        if unsorted:
            f.write("\nUnplaced Dragons (no matching habitat):\n")
            for d in unsorted:
                f.write(f"  {d}\n")

    print(f"Dragons organized and saved to {output_file}")


# --- run ---
if __name__ == "__main__":
    dragons = load_dragons("dragons.csv")
    habitats = load_habitats("habitats.csv")

    sortbyhabitat(dragons, "sorted_dragons.txt")
    organize_dragons_into_habitats(dragons, habitats, "organized_habitats.txt")
