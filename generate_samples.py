from pathlib import Path
import random

SUBMISSIONS_DIR = "submissions"
NUM_DOCS = 25
LINES_PER_DOC = 1000

TOPIC_GROUPS = {
    "machine_learning": [
        "Machine learning enables systems to learn from data and improve automatically.",
        "Supervised learning uses labeled data to train predictive models.",
        "Neural networks simulate the human brain for pattern recognition.",
        "Reinforcement learning improves behaviour using rewards and penalties."
    ],
    "operating_systems": [
        "Operating systems manage hardware resources and system processes.",
        "Process scheduling determines the execution order of tasks.",
        "Memory management allocates and tracks system RAM usage.",
        "File systems organize and store data on storage devices."
    ],
    "networking": [
        "Computer networks enable communication between devices.",
        "TCP/IP is the foundational protocol suite of the internet.",
        "Routing determines the best path for data packets.",
        "Network security protects systems from unauthorized access."
    ],
    "geography": [
        "India is a country in South Asia with diverse landscapes.",
        "The Himalayas form the northern mountain boundary.",
        "Major rivers include the Ganges, Brahmaputra, and Yamuna.",
        "Indian culture includes languages, religions, and traditions."
    ],
    "astronomy": [
        "The solar system consists of the sun and orbiting planets.",
        "Earth is the third planet and supports life.",
        "Gas giants include Jupiter and Saturn.",
        "Galaxies contain billions of stars and cosmic structures."
    ]
}

Path(SUBMISSIONS_DIR).mkdir(exist_ok=True)

for i in range(1, NUM_DOCS + 1):
    if i <= 5:
        topic = "machine_learning"
    elif i <= 10:
        topic = "operating_systems"
    elif i <= 15:
        topic = "networking"
    elif i <= 20:
        topic = "geography"
    else:
        topic = "astronomy"

    lines = []
    for _ in range(LINES_PER_DOC):
        line = random.choice(TOPIC_GROUPS[topic])
        if random.random() < 0.2:
            line += f" Additional note {random.randint(1,9999)}."
        lines.append(line)

    file_path = Path(SUBMISSIONS_DIR) / f"sample_{i}.txt"
    file_path.write_text("\n".join(lines), encoding="utf-8")

print(f"✅ Generated {NUM_DOCS} documents with {LINES_PER_DOC} lines each in '{SUBMISSIONS_DIR}' folder!")
