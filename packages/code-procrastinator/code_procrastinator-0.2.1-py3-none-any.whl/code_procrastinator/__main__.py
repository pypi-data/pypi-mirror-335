import code_procrastinator.procrastinator as procrastinator

def main():
    # Test the excuse_wrapper decorator with add()
    @procrastinator.excuse_wrapper
    def add(x, y):
        return x + y
    print("Result from add():", add(1, 2))
    
    # Test the procrastinate function
    procrastinator.procrastinate(10, 3)
    
    # Test the reaffirm_program function using user input
    user_message = input("Enter a message to encourage the program: ")
    result = procrastinator.reaffirm_program(user_message)
    print("reaffirm_program returned:", result)

if __name__ == "__main__":
    main()
