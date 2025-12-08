import pandas as pd

def making_dataframe_in_correct_format(df):

    # Remove first column (index 0)
    df = df.drop(df.columns[0], axis=1)

    # Step 1: Set first row as header
    df.columns = df.iloc[0]

    # Step 2: Remove the first row from data
    df = df[1:]

    # Step 3: Reset index
    df = df.reset_index(drop=True)

    # Function to convert column names to int if possible
    def convert_to_int(col):
        try:
            # Try to convert to float first, then int
            return int(float(col))
        except:
            # If fails (non-numeric), keep original name
            return col

    # Apply to all columns
    df.columns = [convert_to_int(c) for c in df.columns]


    # Keep all columns except the last one
    df = df.iloc[:, :-1]

    return df