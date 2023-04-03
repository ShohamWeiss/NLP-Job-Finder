import pandas as pd
import os
from datetime import datetime

df = pd.DataFrame(columns=["job_id","job_title", "location", "experience",
                           "education", "job_type", "job_description", "job_link"])

for file in os.listdir("scraped_data_2"):
    if file.endswith(".csv"):
        df = pd.concat([df, pd.read_csv(f"scraped_data_2/{file}")], ignore_index=True)

save_dir = f"combined_data_{datetime.now().strftime('%Y-%m-%d')}.csv"
df.to_csv(save_dir)
print(len(df))