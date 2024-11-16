"""
Create the assignments and send out the emails.
"""
import json
import random
from time import time

from mail_sender import send_emails

JSON_FILE = "history.json"
FAMILIES_FILE = "families.json"

FamiliesType = list[list[dict[str, str]]]


def load_families() -> FamiliesType:
    families: FamiliesType = None
    with open("families.json") as file:
        families = json.load(file)
    return families


def generate_members_list(families: FamiliesType) -> list[tuple[int, str]]:
    members = [(family_index, person["Name"])
               for family_index, family in enumerate(families)
               for person in family]
    return members


def load_history(members: list[tuple[int, str]]) -> dict[str, list[str]]:
    history: dict[str, list[str]] = {}
    try:
        with open(JSON_FILE, "rt") as read_file:
            history = json.load(read_file)
    except FileNotFoundError:
        with open(JSON_FILE, "wt") as file:
            blank_history = {person: [] for _, person in members}
            json.dump(blank_history, file, indent=4)

        with open(JSON_FILE, "rt") as read_file:
            history = json.load(read_file)
    return history


def make_assignments(
        members: list[tuple[int, str]],
        history: dict[str, list[str]]
        ) -> list[tuple[str, str]]:
    people_assigned: list[str] = []  # [person1, person2, person3...]
    assignments: list[tuple[str, str]] = []  # {person1: assignment1}

    for family_index, name in members:
        hat = [option_name for option_index, option_name in members
               if option_index != family_index
               and option_name not in history[name]
               and option_name not in people_assigned]

        assignment = random.choice(hat)
        assignments.append((name, assignment))
        people_assigned.append(assignment)
        history[name].append(assignment)

    # write the history
    with open(JSON_FILE, "wt") as file:
        json.dump(history, file, indent=4)

    for giver, receiver in assignments:
        print(giver, "->", receiver)
    return assignments


if __name__ == "__main__":
    families = load_families()
    members = generate_members_list(families)
    history = load_history(members)

    # This is my really intelligent way of avoiding a stalemate issue where
    # the random choices end with a person not having any valid assignment
    # options. If that happens, then we just retry making the assignments 😅
    start = time()
    assignments = None
    while time() - start < 2:  # Only try for 2 seconds
        try:
            assignments = make_assignments(members, history)
            break
        except IndexError:
            ...

    if not assignments:
        raise Exception("Stalemate error while making assingments. "
                        "There aren't any valid compinations left.\n"
                        "Please delete the history file, or clear "
                        "out a few of the oldest entries")

    send_emails(assignments)
