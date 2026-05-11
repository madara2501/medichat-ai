import pandas as pd
import os
from datetime import datetime

EXCEL_FILE = "admin view data.xlsx"


def save_chat_excel(user_id, email, user_msg, bot_msg):

    data = {
        "User ID": user_id,
        "Email": email,
        "User Message": user_msg,
        "Bot Reply": bot_msg,
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if os.path.exists(EXCEL_FILE):

        df = pd.read_excel(EXCEL_FILE)

        df = pd.concat(
            [df, pd.DataFrame([data])],
            ignore_index=True
        )

    else:
        df = pd.DataFrame([data])

    # Sort by Email and Time
    df = df.sort_values(
        by=["Email", "Time"]
    )

    df.to_excel(EXCEL_FILE, index=False)

