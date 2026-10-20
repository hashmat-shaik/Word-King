# 👑 Word King

A terminal word-guessing game powered by **Word2Vec**. A secret word is picked at random, and every guess is scored by how *semantically close* it is to the target, not by spelling. Use the scores as clues to close in on the word before the hints run out.

---

## 🎮 How It Works

1. The game picks a secret word from a list of 5,000 common English words.
2. You type guesses. Each valid guess gets a **score from 0 to 100** based on how similar its meaning is to the secret word (using cosine similarity between Word2Vec vectors).
3. A **Current Standings** table shows your top 5 guesses so far, so you can see which direction you're heading.
4. Every **15 seconds** a random letter of the secret word is revealed (e.g. `_ a _ e`).
5. You win by guessing the word. If every letter gets revealed before you do, the round is over.

```
=== Round Started! Guess the word. ===
Enter your guess: ocean

--- Current Standings ---
+------+------------------+-------+
| Rank | Word             | Score |
+------+------------------+-------+
| 1    | ocean            |    71 |
+------+------------------+-------+

[Hint]: _ _ _ _ e _
```

*(Example output only. Scores depend on the secret word.)*

### Scoring

Similarity is passed through a sigmoid curve so that scores are easy to read:

```
score = round(100 / (1 + e^(-10 × (similarity - 0.35))))
```

| Cosine similarity | Approx. score |
| --- | --- |
| 0.20 | 18 |
| 0.35 | 50 |
| 0.50 | 82 |

### Commands

| Input | Result |
| --- | --- |
| Any word | Scores your guess against the secret word |
| `exit` | Ends the round and reveals the word |

> Guesses should be typed in **lowercase**. Words that aren't in the model's vocabulary, or that contain digits, underscores, or spaces, are rejected as unrecognized.

## 🛠 Tech Stack

| Area | Technology |
| --- | --- |
| Language | Python 3 |
| Word embeddings | [Gensim](https://radimrehurek.com/gensim/) `KeyedVectors` with the pretrained **Google News 300-dimensional Word2Vec** model |
| Terminal input | [prompt_toolkit](https://python-prompt-toolkit.readthedocs.io/) (async prompt, so hints can print while you type) |
| Concurrency | `asyncio` (a background timer task reveals hints while you play) |

## 📁 Project Structure

```
Word-King/
├── Wordking.py            # The whole game
├── word_list_5000.txt     # 5,000 common words used as possible secret words
└── .gitignore             # Ignores venv, model files (*.gz, *.kv, *.npy), caches
```

The pretrained model is **not included** in the repository because of its size (it's git-ignored). You need to download it separately; see below.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or newer
- Several GB of free RAM and disk space for the Word2Vec model (the Google News vectors are roughly 1.6 GB compressed and take several GB in memory on first load)

### 1. Clone and install dependencies

```bash
git clone https://github.com/<your-username>/Word-King.git
cd Word-King

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install gensim prompt_toolkit
```

### 2. Get the Word2Vec model

The game expects the file `word2vec-google-news-300.gz` in the project folder. One way to get it is through Gensim's downloader:

```bash
python -c "import gensim.downloader as api; api.load('word2vec-google-news-300')"
```

This downloads the model into `~/gensim-data/word2vec-google-news-300/`. Copy `word2vec-google-news-300.gz` from there into the project folder:

```bash
cp ~/gensim-data/word2vec-google-news-300/word2vec-google-news-300.gz .
```

### 3. Play

```bash
python Wordking.py
```

On the first run the game loads the `.gz` file and saves a fast-loading cache (`word2vec-google-news-300.kv`). Later runs load from the cache and start much faster.

## ⚙️ Under the Hood

- **Vocabulary cleanup:** the Google News model contains phrases, numbers, and mixed-case tokens. The game keeps only purely alphabetic single words and maps lowercase forms back to the model's original keys.
- **Playable words:** secret words are the entries of `word_list_5000.txt` that also exist in the cleaned vocabulary.
- **Hints:** a background `asyncio` task wakes every 15 seconds and reveals one more random letter. `prompt_toolkit`'s `patch_stdout` keeps hint output from garbling the line you're typing.
- **Fast startup:** the first load saves a `.kv` cache that later runs open with memory mapping.

## 🗺 Ideas for the Future

- Play multiple rounds with a running total
- Case-insensitive guesses and whitespace trimming
- A `requirements.txt` for one-step setup
- Difficulty levels (hint speed, word length)
- Show all guesses in a round, not just the top 5
- Daily word mode

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to open an issue or submit a pull request.

## 📄 License

Copyright 2026 Hashmat Shaik

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.



> **Note:** the Google News Word2Vec vectors are distributed separately under their own terms. Check their license before redistributing them.
