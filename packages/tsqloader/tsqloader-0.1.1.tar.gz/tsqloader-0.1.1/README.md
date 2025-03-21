# tSQLoader

tSQLoader is a Python-based utility designed to simplify interactions with MSSQL databases using SQLAlchemy. This tool empowers users to manage and manipulate database records without requiring direct access to the production database or advanced SQL knowledge. It offers features such as seamless database connections, inserting or updating records using Pandas DataFrames, handling primary key conflicts gracefully, and verifying table existence. tSQLoader is particularly valuable for managing data pipelines, integrating data from various sources, and enabling a smoother, more accessible database interaction experience.

## Features

- Establishes a connection to SQL databases using SQLAlchemy.
- Writes Pandas DataFrames to SQL tables with support for primary key conflict resolution.
- Deletes conflicting rows in the database before inserting new data.
- Checks if a specified SQL table exists.

## Requirements

To use DatabaseHandler, ensure you have the following installed:

- Python 3.7 or higher
- SQLAlchemy
- Pandas
- A compatible SQL driver (right now, `pyodbc` for MSSQL)

## Installation and Local Development

### 1. Ensure you have the following installed:
   - [Python (version X.X.X)](https://www.python.org/downloads/)
   - [Git](https://git-scm.com/downloads)
   - Any additional tools or software required for your project.

### 2. Clone the repository:
```bash
git clone https://github.com/sb5m/tSQLoader.git
cd tsqloader
```
### 3. Create Virtual Environment
```bash
python -m venv .venv
```
Activate the virtual environment with:
```bash
. .venv\Scripts\activate
```
or
```bash
source .venv/bin/activate
```
### 4. Upgrade pip and install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
### 5. You are set. Package install can be performed with: 
```bash
pip install .
```

## PyPi Release

### Build

```bash
python -m build
```

### Upload

After pyproject.toml version bump...

```bash
twine upload dist/*
```

## Usage

### 1. Import and Initialize

Begin by importing the `DatabaseHandler` class and initializing it with your database connection details:

```python
from database_handler import DatabaseHandler

db_handler = DatabaseHandler(
    server="server_address",
    database="database_name",
    username="username",
    password="password"
)
```

### 2. Writing Data to Table

```python
import pandas as pd

# Create a sample DataFrame
data = {
    'id': [1, 2],
    'name': ['Alice', 'Bob']
}
df = pd.DataFrame(data)

# Write the DataFrame to the database
db_handler.write_to_db(df, table_name="sample_table", primary_keys=["id"])
```

## Prerequisites

Before using `tSQLoader`, you need to set up the required database and table. Use the following SQL script to create the table structure to replicate the table needed to execute the example above:

```sql
USE [SAMPLE_DB]
GO

/****** Table [dbo].[sample_table]   Script Date: 19.03.2025 ******/

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[sample_table](
    [id] [int] NOT NULL,
    [name] [varchar] (100) NULL
CONSTRAINT [PK_sample_table] PRIMARY KEY CLUSTERED
(
    [id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
```

## Contributing

Contributions are always welcome. If you’d like to improve the project, start by forking the repository and creating a new branch for your changes. Once your work is ready, push it to your fork and open a pull request. 

Thank you for helping make this project better!
