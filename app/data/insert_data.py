from app.db import get_dbSession, engine
# import csv
import pandas as pd
import os
from pathlib import Path

class DataIngest:
    comments_file = Path(__file__).parent / "comments.csv"
    subfeddits_file = Path(__file__).parent / "subfeddit.csv"
    
    def comments(self):
        data = pd.read_csv(self.comments_file)
        data.to_sql('comments', engine, if_exists='append', index=False)

    def subfeddits(self):
        data = pd.read_csv(self.subfeddits_file)
        data.to_sql('subfeddits', engine, if_exists='append', index=False)
