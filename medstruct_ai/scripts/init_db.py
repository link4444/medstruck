from medstruct_ai.db.database import init_db


def main() -> None:
    init_db()
    print("Database initialized successfully.")


if __name__ == "__main__":
    main()
