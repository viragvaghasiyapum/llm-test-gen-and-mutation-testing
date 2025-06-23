from mutap.pipeline import run_pipeline

def main():
    print("Choose an option:")
    print("1. Run pipeline with zero shot prompt")
    print("2. Run pipeline with few shot prompt")
    choice = input("Enter choice: ").strip()

    user_input = input("Enter the number of problems to run (or press Enter for all): ").strip()
    limit = int(user_input) if user_input.isdigit() else None

    if choice == '1':
        run_pipeline(limit=limit, mode="zero_shot")
    elif choice == '2':
        run_pipeline(limit=limit, mode="few_shot")
        main()
    else:
        print("Invalid choice.")
    
    main()
if __name__ == '__main__':
    main()