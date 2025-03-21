from bondable.bond.threads import Threads
from bondable.bond.config import Config
from sqlalchemy.sql import text
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
  pass

    # with threads.get_db_session() as session:
    #     results = session.execute(text("SELECT thread_id, name FROM threads order by origin")).fetchall()
    #     for thread_id, name in results:
    #         threads.delete_thread(thread_id)
    #         print(f"Deleted thread {thread_id}")