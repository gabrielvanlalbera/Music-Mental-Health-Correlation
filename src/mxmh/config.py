"""Project-wide constants. Change them here, not inside notebooks."""

SEED = 42
TARGETS = ["Anxiety", "Depression", "Insomnia", "OCD"]
HIGH_THRESHOLD = 7  # a score >= 7 (on the 0-10 scale) is flagged "high"

FREQ_MAP = {"Never": 0, "Rarely": 1, "Sometimes": 2, "Very frequently": 3}
GENRES = [
    "Classical", "Country", "EDM", "Folk", "Gospel", "Hip hop", "Jazz", "K pop",
    "Latin", "Lofi", "Metal", "Pop", "R&B", "Rap", "Rock", "Video game music",
]
FREQ_COLS = [f"freq_{g}" for g in GENRES]
BINARY_COLS = ["While working", "Instrumentalist", "Composer", "Exploratory", "Foreign languages"]

BPM_RANGE = (40, 250)   # values outside are treated as data-entry errors
MAX_HOURS = 16          # more listening hours per day than this is implausible
AGE_BINS = [0, 17, 24, 34, 120]
AGE_LABELS = ["<18", "18-24", "25-34", "35+"]
MIN_GENRE_GROUP = 20    # genre groups smaller than this are never interpreted
