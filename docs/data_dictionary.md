# Data dictionary

Source file: `data/raw/mxmh_survey_results.csv` (736 respondents, 33 columns), an online "Music & Mental Health" survey.
Cleaned file: `data/processed/mxmh_clean.csv` (produced by `src/mxmh/data.py`).

| Column (raw) | Type | Meaning | Handling |
|---|---|---|---|
| Timestamp | datetime | Submission time | dropped |
| Age | int | Age in years (10-89) | kept; `age_group` added (<18, 18-24, 25-34, 35+) |
| Primary streaming service | categorical | Main service used | one-hot in the "categorical" feature set |
| Hours per day | float | Daily listening hours | values > 16 set to NaN |
| While working | Yes/No | Listens while working | 1/0 |
| Instrumentalist | Yes/No | Plays an instrument | 1/0 |
| Composer | Yes/No | Composes music | 1/0 |
| Fav genre | categorical | Favourite genre | one-hot; groups < 20 collapsed |
| Exploratory | Yes/No | Actively explores new artists/genres | 1/0 |
| Foreign languages | Yes/No | Listens to non-native-language music | 1/0 |
| BPM | float | Tempo of favourite genre | outside 40-250 set to NaN; `bpm_missing` flag added |
| Frequency [genre] x16 | ordinal | Never / Rarely / Sometimes / Very frequently | `freq_<genre>` = 0..3 |
| Anxiety, Depression, Insomnia, OCD | int 0-10 | Self-rated severity | targets; `<target>_high` = score >= 7 |
| Music effects | categorical | Self-reported effect of music (Improve / No effect / Worsen) | **excluded from features** (outcome of listening) |
| Permissions | text | Consent text | dropped (constant) |

Derived: `genre_diversity` (number of genres listened to "Sometimes" or more), `bpm_missing`, `age_group`, `<target>_high`.
