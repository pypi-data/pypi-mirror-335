import csv
import os
import json

def modify():
    os.makedirs("data", exist_ok=True)
    
    while True:
        filename = input("Enter the filename to modify:").lower() + ".csv"
        filepath = os.path.join("data", filename)
        
        if not os.path.exists(filepath):
            print("Error: File does not exist! Try again or type 'exit' to cancel.")
            continue
        
        while True:
            with open(filepath, mode='a+', newline='') as file:
                file.seek(0)
                reader = csv.reader(file)
                data = list(reader)
                
                if not data:
                    print("Error: File is empty!")
                    return
                
                print("Choose an option:")
                print("1. Add a new row")
                print("2. Add a new column")
                print("3. Delete a row")
                print("4. Delete a column")
                print("5. Modify particular data")
                print("6. Exit")
                choice = input("Enter choice (1/2/3/4/5/6): ").strip()
                
                if choice == '1':
                    while True:
                        new_id = str(len(data))  # Assign new ID based on last row count
                        new_row = [new_id] + [input(f"Enter data for {col}: ") for col in data[0][1:]]
                        data.append(new_row)
                        more_rows = input("Do you want to add another row? (y/n): ").lower()
                        if more_rows in ['n', 'exit']:
                            break
                elif choice == '2':
                    new_col_name = input("Enter new column name: ")
                    data[0].append(new_col_name)
                    for row in data[1:]:
                        row.append(input(f"Enter data for {new_col_name} (Row {row[0]}): "))
                elif choice == '3':
                    row_id = input("Enter row ID to delete: ")
                    data = [row for row in data if not (row[0].replace(".", "").isdigit() and float(row[0]) == float(row_id))]
                elif choice == '4':
                    col_name = input("Enter column name to delete: ")
                    if col_name in data[0]:
                        col_index = data[0].index(col_name)
                        for row in data:
                            del row[col_index]
                    else:
                        print("Error: Column not found!")
                elif choice == '5':
                    row_id = input("Enter row ID to modify: ")
                    col_name = input("Enter column name to modify: ")
                    
                    if col_name not in data[0]:
                        print("Error: Column not found! Adding column...")
                        data[0].append(col_name)
                        for row in data[1:]:
                            row.append("")
                    
                    row_found = False
                    for row in data[1:]:
                        if row[0] == row_id:
                            row_found = True
                            col_index = data[0].index(col_name)
                            new_value = input(f"Enter new value for row {row_id}, column {col_name}: ")
                            row[col_index] = new_value
                            break
                    
                    if not row_found:
                        print("Error: Row not found! Adding new row...")
                        new_row = [row_id] + ["" for _ in data[0][1:]]
                        data.append(new_row)
                else:
                    print("Modify method has been exited!")
                    break
            
            with open(filepath, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(data)
            
            while True:
                show_table = input("Do you want to see the updated table? (y/n): ").lower()
                if show_table in ['y', 'yes']:
                    print(json.dumps([dict(zip(data[0], row)) for row in data[1:]], indent=4))
                elif show_table in ['n', 'exit']:
                    return

