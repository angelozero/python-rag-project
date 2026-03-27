import sys
import os
from src.service.database import create_db
from src.service.rag import rag_execute

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def main():
    # create_db()
    rag_execute()


if __name__ == "__main__":
    main()
