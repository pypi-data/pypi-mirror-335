import time
import random

def delay_timer(minutes):
    total_time = 0 
    excuses = [
        "That went by fast! You deserve 5 more minutes.",
        "You can't stop now! You're in the middle of something (probably).",
        "Studies show that short breaks boost productivity... take another one!",
        "One more round won't hurt. Right?",    
        "You should grab a snack before you start working. Go on!",
        "Your brain is still warming up. Give it a little longer.",
        "You were just about to have a great idea! Stay put.",
        "Look, if you start now, you might actually be TOO productive.",
        "Alright, maybe it's time... but are you REALLY ready?",
    ]
    user_bool = False
    while total_time < minutes + 20:
        print(f"Procrastinating for {minutes} minutes...")
        time.sleep(minutes * 60)  
        total_time += minutes

        if total_time >= minutes:
            excuse = random.choice(excuses)
            print(excuse)

            user_input = input("Do you want to extend? (yes/no): ").strip().lower()
            if user_input not in ["yes", "y"]:
                user_bool = True
                print("Fine, be responsible. Go do your work.")
                break

            minutes = 5
    if not user_bool:
        print("Alright, you REALLY should start now. Maybe.")

# Example usage:
if __name__ == "__main__":
    minutes = int(input("How long do you want to procrastinate (in minutes)? "))
    delay_timer(minutes)
