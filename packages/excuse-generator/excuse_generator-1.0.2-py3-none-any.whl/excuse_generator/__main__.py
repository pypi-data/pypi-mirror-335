import sys
from excuse_generator import generate_excuse, random_excuse, list_categories, help

def main():
    print("Welcome to the Software Engineer Excuse Generator!")
    print("Choose a category or type 'random' for a random excuse.")
    
    while True:
        print("\nCategories:", ", ".join(list_categories()))
        user_input = input("Enter a category (or 'random', 'exit' to quit): ").strip().lower()
        
        if user_input == "exit":
            print("Goodbye!")
            sys.exit(0)
        
        elif user_input == "random":
            print("Excuse:", random_excuse())
        
        elif user_input in list_categories():
            print("Excuse:", generate_excuse(user_input))
        
        else:
            print("Invalid category. Please try again.")

if __name__ == "__main__":
    main()
