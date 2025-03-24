# Sheetsmart Python 
Sheetsmart is a Python library designed to simplify data handling and visualization from spreadsheets. It provides an intuitive interface for quick chart generation, data modification, and file management.

## Features

### Data Visualization
- **bar**  
  Generates a bar graph based on column data in the file.

- **bar5**  
  Creates a bar graph with exactly 5 bars for quick visualization.

- **biplot**  
  Displays a scatter plot comparing two datasets.
  **Usage:** `sheetsmart.biplot()`

### File Management
- **mkcopy**  
  Copies the file to the downloads directory for easy sharing or backup.

- **read**  
  Loads data from a file for analysis or processing.

- **write**  
  Saves modifications to a new file or exports data in another format.

### Data Modification
- **modify**  
  Provides options to:
  - Add or delete columns
  - Add or delete rows
  - Modify specific data entries

### User Feedback
- **feedback**  
  Allows users to submit suggestions for improving Sheetsmart.

## Getting Started

1. **Installation:**
   ```bash
   pip install sheetsmart
   ```

2. **Basic Usage Example:**
   ```python
   import sheetsmart

   # Load data
   data = sheetsmart.read()
   
   # Generate visualizations
   sheetsmart.bar()
   sheetsmart.bar5()
   sheetsmart.biplot()

   # Modify data
   sheetsmart.modify()

   # Save changes
   sheetsmart.write()

   # Copy file for sharing
   sheetsmart.mkcopy()

   # Provide feedback
   sheetsmart.feedback()
   ```

👨‍💻 **Developed by** [Bhuvanesh M](https://github.com/bhuvanesh-m-dev)

### 🌐 Connect with Me:

- **Portfolio**: [bhuvaneshm.in](https://bhuvaneshm.in/)
- **LinkedIn**: [linkedin.com/in/bhuvaneshm-developer](https://www.linkedin.com/in/bhuvaneshm-developer)
- **GitHub**: [github.com/bhuvanesh-m-dev](https://github.com/bhuvanesh-m-dev)
- **HackerRank**: [hackerrank.com/profile/bhuvaneshm\_dev](https://www.hackerrank.com/profile/bhuvaneshm_dev)
- **YouTube**: [youtube.com/@bhuvaneshm\_dev](https://www.youtube.com/@bhuvaneshm_dev)
- **LeetCode**: [leetcode.com/u/bhuvaneshm\_dev](https://leetcode.com/u/bhuvaneshm_dev/)
- **X (Twitter)**: [x.com/bhuvaneshm06](https://x.com/bhuvaneshm06)
- **Instagram**: [instagram.com/bhuvaneshm.developer](https://www.instagram.com/bhuvaneshm.developer)

