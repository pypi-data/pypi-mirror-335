import time
import random
from tqdm import tqdm


def conversion_process():
    options = [
        "wxrp-xrpl-xrp", "wxrp-xrpl", "usdt-xrpl", "wrappedxrp-xrpl"
    ]
    
    print("\nConversion Options:")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    while True:
        try:
            choice = int(input("\nSelect an option (1-4): "))
            if 1 <= choice <= 4:
                selected_option = options[choice - 1]
                break
            else:
                print("Invalid choice. Please select a valid option.")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 4.")

    input("\nEnter your XRPL Identification Key: ")
    input("Enter your XRPX Ledger Address: ")
    input("Enter your Stable Transfer Address: ")

    print("\nConversion started...\n")
    time.sleep(random.uniform(3, 4))  # Hold for 3-4 seconds at 0% before progressing

    total_time = 5 * 60  # 5 minutes in seconds
    steps = total_time / 100  # Ensuring 100 steps in 5 minutes

    with tqdm(total=100, bar_format="{desc} {bar} | {postfix}", dynamic_ncols=True) as pbar:
        progress = 0.0
        while progress < 100:
            increment = random.uniform(0.5, 1.5)  # Smooth decimal increments
            progress = min(progress + increment, 100)

            # Correct order of progress bar: '=' grows, '-' shrinks
            bar_length = int(progress)
            bar_chars = "=" * bar_length + "-" * (100 - bar_length)

            # Formatting bar with left and right labels
            pbar.set_description("Conversion in progress")
            pbar.bar_format = f"{{desc}} {bar_chars} {{postfix}}"  # Fixed formatting

            pbar.set_postfix_str(f"{progress:.2f}%")  # Removed comma
            pbar.n = round(progress, 2)  # Keep decimal precision
            pbar.refresh()  # Update the bar dynamically

            time.sleep(steps)  # Maintain the total runtime of 5 minutes

    print("\nConversion Successful! ✅")

def main():
    conversion_process()

if __name__ == "__main__":
    main()