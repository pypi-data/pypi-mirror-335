import os
import pandas as pd
import matplotlib.pyplot as plt

def bar():
    os.makedirs("data", exist_ok=True)
    
    filename = input("Enter the filename to analyze (without extension): ").lower() + ".csv"
    filepath = os.path.join("data", filename)
    
    if not os.path.exists(filepath):
        print("Error: File does not exist! Check the name of the file or use sheetsmart.write() to create a table.")
        return
    
    df = pd.read_csv(filepath)
    df.columns = [col.lower() for col in df.columns]  # Convert column names to lowercase
    
    while True:
        column_name = input("Enter the column name to analyze: ").strip().lower()
        
        if column_name in df.columns:
            break
        
        # Suggest a possible correct column name
        suggestions = [col for col in df.columns if column_name in col or col in column_name]
        if suggestions:
            print(f"Error: Column '{column_name}' not found in '{filename}'. You may refer '{suggestions[0]}'?")
        else:
            print(f"Error: Column '{column_name}' not found in '{filename}'. Use sheetsmart.modify() to add a new column.")
            return
    
    plt.figure(figsize=(10, 6))
    plt.hist(df[column_name], color='green', edgecolor='white')
    
    plt.xlabel("ID")
    plt.ylabel(column_name.capitalize())
    plt.title(f"Histogram(by SheetSmart) of {column_name.capitalize()}")
    plt.grid(True)
    plt.show()

