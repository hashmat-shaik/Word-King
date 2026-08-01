import random
import math
import asyncio
import os
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import PromptSession
from gensim.models import KeyedVectors


model_path = '/Users/hashmatshaik/Documents/GameDev/Word_King/Word-King/word2vec-google-news-300.gz'
cached_model_path = '/Users/hashmatshaik/Documents/GameDev/Word_King/Word-King/word2vec-google-news-300.kv'
word_file_path = '/Users/hashmatshaik/Documents/GameDev/Word_King/Word-King/word_list_5000.txt'

# Hi, I'm Hashmat Shaik

player_scores = {}
sanitized_vocab = {}
common_words = set()

def score_cal(model, target_word, guess):
  if guess not in sanitized_vocab:
        return None
  guess_sim = model.similarity(sanitized_vocab[target_word], sanitized_vocab[guess])
  return calculate_score(guess_sim)

def calculate_score(sim, threshold=0.3):
  k = 10
  mean = 0.35
  return round((100/(1 + math.exp(-1*k*(sim - mean)))))

def print_scoreboard(scores_dict):
  top_5 = sorted(scores_dict.items(), key=lambda item: item[1], reverse=True)[:5]

  rank_w, word_w, score_w = 4, 16, 5
  border = f"+{'-'*(rank_w+2)}+{'-'*(word_w+2)}+{'-'*(score_w+2)}+"

  print()
  print("--- Current Standings ---")
  print(border)
  print(f"| {'Rank':<{rank_w}} | {'Word':<{word_w}} | {'Score':>{score_w}} |")
  print(border)
  for rank, (word, score) in enumerate(top_5, 1):
    print(f"| {rank:<{rank_w}} | {word:<{word_w}} | {score:>{score_w}} |")
  print(border)

if os.path.exists(cached_model_path):
    print(f"Loading cached model from '{cached_model_path}'...")
    model = KeyedVectors.load(cached_model_path, mmap='r')
    print("Model loaded successfully (from cache).")
else:
    print(f"No cache found. Loading Word2Vec model from '{model_path}'...")
    model = KeyedVectors.load_word2vec_format(model_path, binary=True)
    print("Model loaded successfully.")
    print(f"Saving cache to '{cached_model_path}' for faster startup next time...")
    model.save(cached_model_path)
    print("Cache saved.")


for original_key in model.index_to_key:
    
    # 1. Reject n-grams (underscores)
    if '_' in original_key:
        continue
        
    # 2. Reject numbers, symbols, and punctuation
    if not original_key.isalpha():
        continue
        
    # 3. Normalize to lowercase for player input
    clean_guess = original_key.lower()
    
    # 4. Handle Case Collisions (The Critical Thinking Step)
    if clean_guess not in sanitized_vocab:
        sanitized_vocab[clean_guess] = original_key


with open(word_file_path, "r") as file:
    for word in file:
      common_words.add(word.strip())

playable_words = [x.lower() for x in common_words if x.lower() in sanitized_vocab]

async def timer_task(target_word, hints_done):
    revealed = ['_'] * len(target_word)
    unrevealed_indices = list(range(len(target_word)))
    
    try:
      while unrevealed_indices:
          
        # Yield control back to the main loop for a set interval
        # (This allows the user to keep typing guesses)
        await asyncio.sleep(15) 
        
        idx = random.choice(unrevealed_indices)
        unrevealed_indices.remove(idx)
        revealed[idx] = target_word[idx]
        
        print(f"\n[Hint]: {' '.join(revealed)}")
      print("\n[Time's up!] No more hints.")
      hints_done.set()
    except asyncio.CancelledError:
      pass

async def game_loop():
    session = PromptSession()
    
    target_word = random.choice(playable_words)
    hints_done = asyncio.Event()
    timer = asyncio.create_task(timer_task(target_word, hints_done))
    
    with patch_stdout():
        print("=== Round Started! Guess the word. ===")
      
        while True:
          guess_task = asyncio.create_task(session.prompt_async("Enter your guess: "))
          hints_task = asyncio.create_task(hints_done.wait())

          done, pending = await asyncio.wait(
              {guess_task, hints_task}, return_when=asyncio.FIRST_COMPLETED
          )

          if hints_task in done:
            guess_task.cancel()
            print(f"\nGame over! The word was '{target_word}'.")
            break

          hints_task.cancel()
          user_guess = guess_task.result()
          
          if user_guess == "exit":
            print(f"The word was {target_word}. Better luck next time!")
            break
          if user_guess == target_word:
            print(f"\n🎉 You win!")
            break
            
          result = score_cal(model, target_word, user_guess)
          if result is None:
            print(f"'{user_guess}' isn't a recognized word. Try another.")
          else:
            player_scores[user_guess] = result
            print_scoreboard(player_scores)
                
    timer.cancel()

# Execute the asynchronous program
if __name__ == "__main__":
    asyncio.run(game_loop())