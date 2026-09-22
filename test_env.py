import os 
from dotenv import load_dotenv
load_dotenv()
print(os.getenv("MY_TEST_VALUE"))
