import os
from dotenv import load_dotenv
from algosdk import mnemonic

load_dotenv()
phrase = os.getenv("ALGORAND_FACILITATOR_MNEMONIC", "")
words = phrase.strip().split()

if len(words) >= 24:
    first_24 = " ".join(words[:24])
    try:
        from algosdk.wordlist import word_list_raw
        word_list = word_list_raw().strip().split()
        
        correct_mnemonic = None
        for w in word_list:
            candidate = first_24 + " " + w
            try:
                mnemonic.to_private_key(candidate)
                correct_mnemonic = candidate
                break
            except Exception:
                continue
                
        if correct_mnemonic:
            print("Successfully found correct checksum word!")
            print(f"Original 25th word: {words[24]}")
            print(f"Correct 25th word: {w}")
        else:
            print("Could not find a valid 25th word. Are the first 24 words correct?")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Not enough words in mnemonic to compute checksum.")
