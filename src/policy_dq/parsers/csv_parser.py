import csv
from typing import List, Dict


def load_csv(path: str) -> List[Dict]:

    with open(path) as f:

        reader = csv.DictReader(f)

        return list(reader)