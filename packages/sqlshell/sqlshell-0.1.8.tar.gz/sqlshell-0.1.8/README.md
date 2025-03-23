# SQLShell

<div align="center">

![SQLShell Interface](sqlshell_logo.png)

**A modern SQL REPL interface for seamless querying of Excel, Parquet, and SQLite databases**

![SQLShell Interface](sqlshell_demo.png)

</div>

## 🚀 Key Features

- **Interactive SQL Interface** - Rich syntax highlighting for enhanced query writing
- **DuckDB Integration** - Built-in support for local DuckDB database (pool.db)
- **Multi-Format Support** - Import and query Excel (.xlsx, .xls) and CSV files effortlessly
- **Modern UI** - Clean, tabular results display with intuitive controls
- **Productivity Tools** - Streamlined workflow with keyboard shortcuts (e.g., Ctrl+Enter for query execution)

## 📦 Installation

### Linux Setup with Virtual Environment

```bash
# Create and activate virtual environment
python3 -m venv ~/.venv/sqlshell
source ~/.venv/sqlshell/bin/activate

# Install SQLShell
pip install sqlshell

# Configure shell alias
echo 'alias sqls="~/.venv/sqlshell/bin/sqls"' >> ~/.bashrc  # or ~/.zshrc for Zsh
source ~/.bashrc  # or source ~/.zshrc
```

### Windows Quick Start
SQLShell is immediately available via the `sqls` command after installation:
```bash
pip install sqlshell
```

## 🎯 Getting Started

1. **Launch the Application**
   ```bash
   sqls
   ```

2. **Database Connection**
   - SQLShell automatically connects to a local DuckDB database named 'pool.db'

3. **Working with Excel Files**
   - Click "Browse Excel" to select your file
   - File contents are loaded as 'imported_data' table
   - Query using standard SQL syntax

4. **Query Execution**
   - Enter SQL in the editor
   - Execute using Ctrl+Enter or the "Execute" button
   - View results in the structured output panel

## 📝 Query Examples

### Basic Join Operation
```sql
SELECT *
FROM sample_sales_data cd
INNER JOIN product_catalog pc ON pc.productid = cd.productid
LIMIT 3;
```

### Multi-Statement Queries
```sql
-- Create a temporary view
CREATE OR REPLACE TEMPORARY VIEW test_v AS
SELECT *
FROM sample_sales_data cd
INNER JOIN product_catalog pc ON pc.productid = cd.productid;

-- Query the view
SELECT DISTINCT productid
FROM test_v;
```

## 💡 Pro Tips

- Use temporary views for complex query organization
- Leverage keyboard shortcuts for efficient workflow
- Explore the multi-format support for various data sources