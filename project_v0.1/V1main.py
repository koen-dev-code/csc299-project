# graph_pkm/main.py

from Ptests.database import GraphDatabase

def main():
    """
    Main function to initialize the database, create a note,
    and confirm its creation.
    """
    db = None
    try:
        # 1. Initialize our GraphDatabase
        print("Initializing database connection...")
        db = GraphDatabase()

        # 2. Call the add_note method with some sample text
        note_content = "This is my first note in the Graph-Powered Second Brain!"
        print(f"Creating a new note with content: '{note_content}'")
        new_note_uuid = db.add_note(note_content)

        # 3. Print a confirmation message with the new note's UUID
        if new_note_uuid:
            print(f"\nSuccess! Note created with UUID: {new_note_uuid}")
        else:
            print("\nError: Failed to create the note.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # 4. Ensure the database connection is closed properly
        if db:
            print("Closing database connection...")
            db.close()

if __name__ == "__main__":
    main() 