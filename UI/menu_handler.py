class MenuHandler:
    """Handles menu display and user input validation"""

    @staticmethod
    def display_menu():
        """Display the main application menu"""
        print("\n" + "="*60)
        print("  Welcome to Agentic Pathshala - Your AI Learning Coach")
        print("="*60)
        print("1. Assigned Assignment")
        print("2. Available Assignements")
        print("3. Assessment")
        
        print("4. Exit")
        print("="*60)

    @staticmethod
    def get_choice():
        """Get and validate user menu choice"""
        choice = input("\nEnter your choice (1-4): ").strip()
        if not MenuHandler.validate_choice(choice):
            return 0
        return choice

    @staticmethod
    def validate_choice(choice):
        """Validate menu choice"""
        if not choice.isdigit():
            return False
    
        valid_choices = [str(i) for i in range(1, 5)]
        return choice in valid_choices

    @staticmethod
    def handle_invalid_choice():
        """Handle invalid menu choice"""
        print("Invalid choice. Please enter 1-4.")