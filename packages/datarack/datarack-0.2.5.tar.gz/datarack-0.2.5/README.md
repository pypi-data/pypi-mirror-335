
# Documentation

Welcome to DataRack, a lightweight python module for organizing data, storing it, and reading it. DataRack is useful because of its extensive ways of manipulating data, extremely easy to use functions, and compatibility with CSV files. It stores data in .txt files, and stores the data in a very readable and well organized format. The module is well documented, rigerously tested, and very fast. Take a look at all of the current features of the module:

- [Installing and Importing](#installing-and-importing)
- [Data Nodes](#datanodes)
- [Creating Files](#creating-files)
- [Adding DataNodes](#adding-datanodes)
- [Deleting DataNodes](#deleting-datanodes)
- [Replacing DataNodes](#replacing-datanodes)
- [Reading DataNodes](#reading-datanodes)
- [Filtering](#filtering)
- [Other](#other)
- [CSV Tools](#csv-tools)


## Installing and Importing

Luckily, installing DataRack is extremely simple. You can also directly download the files from the Github repository (not recommended). No dependancies are required!

```bash
pip install datarack
```

To import it into your python project, use:
```python
from datarack import *
```

## DataNodes

DataNodes are a type of data, taylored towards your project. They each have their own set of "categories":

```python
# Creates a DataNode with categories: "Name" and "Age"
my_datanode = DataNode(["Name", "Age"])
```

If you ever need to see the categories:
```python
# Prints out the categories and ID
my_datanode.display_data()
```


## Creating Files

Creating files in DataRack is extremely simple

```python
# Creates a file named "DataFile"
create_file("DataFile.txt")
```

`create_file()` takes 2 parameters:
1. name (String)
2. location (String) *Optional, if not specified will be set to the project directory*

`clear_file()` does the same thing. 

```python
# Clears the file, and creates it if it doesn't find it
clear_file("DataFile.txt")
```

Both functions will auto-create a file if they don't find one. Additionally, files created using the module will have a << DataRack File, Do Not Manually Edit >> header. Files used by this module must have this header, and shouldn't be manually edited.

## Adding DataNodes

DataNodes can be added to a file using a few different methods. To push one to a file, you can use the add_node() function

```python
# Creates a DataNode
person = DataNode(["Name", "Age", "Gender"])

create_file("PEOPLE.txt")

add_node(person, "Default", ["Bob", "57", "Male"], "test.txt")
add_node(person, "Default", ["Marie", "25", "Female"], "test.txt")
```

The file will look like this:

```text
<< DataRack File, Do Not Manually Edit >>

ID: Default
NAME: Bob
AGE: 57
GENDER: Male

ID: Default
NAME: Marie
AGE: 25
GENDER: Female
```

`add_node()` takes 5 parameters:
1. datanode (DataNode)
2. ID (String) - A "tag" associated with the data that makes it easier to access
3. values (List) - All of the data for each category, must be same length as datanode.categories
5. name (String)
6. location (String) *Optional, if not specified will be set to the project directory*

**Similarly, `insert_node()` allows you to insert a chunk of data somewhere in a file, using an index**

`insert_node()` takes 6 parameters:
1. datanode (DataNode)
2. index (Int) - The index, each DataNode gets an index based on where it is located 
3. ID (String) - A "tag" associated with the data that makes it easier to access
4. values (List) - All of the data for each category, must be same length as datanode.categories
5. name (String)
6. location (String) *Optional, if not specified will be set to the project directory*

```python
# Creates a DataNode
person = DataNode(["Name", "Age", "Gender"])

create_file("PEOPLE.txt")

add_node(person, "Default", ["Bob", "57", "Male"], "test.txt")
add_node(person, "Default", ["Marie", "25", "Female"], "test.txt")

# inserts node in between "Bob" and "Marie"
insert_node(person, 1, "Default", ["Mark", 15, "Male"], "test.txt")
```

## Deleting DataNodes

DataRack supports many ways of removing DataNodes from a text file:

```python
# Creates a DataNode
person = DataNode(["Name", "Age", "Gender"])

create_file("PEOPLE.txt")

add_node(person, "Default", ["Bob", "57", "Male"], "test.txt")
add_node(person, "Default", ["Marie", "25", "Female"], "test.txt")

# removes DataNode with index 1 (second chunk of data in the file)
remove_node(person, 1, "test.txt")
```

`remove_node()` takes 4 parameters:
1. datanode (DataNode)
2. index (Int) - The index, each DataNode gets an index based on where it is located 
3. name (String)
4. location (String) *Optional, if not specified will be set to the project directory*

**Alternatively, you can remove nodes by their ID**

`remove_by_id()` takes 4 parameters:
1. datanode (DataNode)
2. ID (String) - The ID of the DataNodes you want to remove
3. name (String)
4. location (String) *Optional, if not specified will be set to the project directory*

`remove_by_id()` will only remove the first DataNode it finds. To remove all DataNodes with the specified ID, use `remove_all_by_id()` *Same Parameters*

## Replacing DataNodes

If you want to replace a node, you can do so in multiple different ways:

```python
# Creates a DataNode
person = DataNode(["Name", "Age", "Gender"])

create_file("PEOPLE.txt")

add_node(person, "Default", ["Bob", "57", "Male"], "test.txt")
add_node(person, "Default", ["Marie", "25", "Female"], "test.txt")

# replaces DataNode with index 1
replace_node(person, 1, "New ID", ["New name", "New age", "New gender"], "test.txt")
```

`replace_node()` takes 6 parameters:
1. datanode (DataNode)
2. index (Int) - The index, each DataNode gets an index based on where it is located
3. ID (String) - The new ID
4. values (List) - The new values
5. name (String)
6. location (String) *Optional, if not specified will be set to the project directory*

**Alternatively, you can replace nodes by their ID**

`replace_by_id()` takes 7 parameters:
1. datanode (DataNode)
2. index (Int) - The index, each DataNode gets an index based on where it is located
3. ID (String) - The ID of the DataNode you want to replace
4. newID (String) - The new ID
5. values (List) - The new values
6. name (String)
7. location (String) *Optional, if not specified will be set to the project directory*

`replace_by_id()` will only replace the first DataNode it finds. To replace all DataNodes with the specified ID, use `replace_all_by_id()` *Same Parameters*

## Reading DataNodes

Once you have a file filled with data, you can read the data using the various functions of the library:

`read_node()` takes 4 parameters:
1. datanode (DataNode)
2. index (Int) - The index, each DataNode gets an index based on where it is located
3. name (String)
4. location (String) *Optional, if not specified will be set to the project directory*

Returns: A list containing the ID (index 0), and the values

`read_by_id()` takes 4 parameters:
1. datanode (DataNode)
2. ID (String) - The ID of the DataNode
3. name (String)
4. location (String) *Optional, if not specified will be set to the project directory*

Returns: A list containing the ID (index 0), and the values

`read_by_id()` will only return the first DataNode it finds. To return all DataNodes with the specified ID, use `read_all_by_id()` *Same Parameters, and returns a nested list containing all DataNodes it finds*

If you do not want to search using an ID or index, and want every DataNode, use `read_all()`:

`read_all()` takes 3 parameters:
1. datanode (DataNode)
2. name (String)
3. location (String) *Optional, if not specified will be set to the project directory*

Returns: A nested list containing the ID (index 0), and the values of every DataNode in the file

## Filtering

DataRack handles filtering with a single, multi-use function called `find_node()`

`find_node()` takes 6 parameters:
1. datanode (DataNode)
2. ID (String) - If you want to filter by a specific ID, put that ID here. If you want to ignore ID filtering, set it to "#"
3. values (List) - The values the DataNode(s) must have, set any values you wan't to ignore to "#"
4. findAll (Bool) - Set to True if you want it to return a nested list of all found items. Set to False if you only want to the first found item
5. name (String)
6. location (String) *Optional, if not specified will be set to the project directory*

Returns: 
- FindAll == True: A nested list of all the IDs and values of all DataNodes found
- FindAll == False: A list containing the ID and values of the first DataNode found

```python
# Creates a DataNode
person = DataNode(["Name", "Age", "Gender"])

create_file("PEOPLE.txt")

add_node(person, "Default", ["Bob", "57", "Male"], "test.txt")
add_node(person, "Default", ["Marie", "25", "Female"], "test.txt")
add_node(person, "Default", ["Jerry", "18", "Male"], "test.txt")

# Prints the values and ID of "Bob" and "Jerry"
print(find_node(person, "#", ["#", "#", "Male"], True, "test.txt"))

# Prints the values and ID of "Jerry"
print(find_node(person, "#", ["#", "18", "Male"], True, "test.txt"))
```

## Other

These are 2 functions which usually aren't useful, but may be needed in some cases:

`get_idx_from_id()` takes 4 parameters:
1. datanode (DataNode)
2. ID (String) - The ID of the DataNode
3. name (String)
4. location (String) *Optional, if not specified will be set to the project directory*

Returns: index of first DataNode in file with specified ID (Int)

`get_all_idx_from_id()` takes 4 parameters:
1. datanode (DataNode)
2. ID (String) - The ID of the DataNodes
3. name (String)
4. location (String) *Optional, if not specified will be set to the project directory*

Returns: list of indexes of all DataNodes in file with the specified ID

## CSV Tools

CSV files are widely used, and DataRack supports easy conversion of these files:

### CSV to Text

First, you need to create a DataNode object from the columns of the CSV file:

`csv_to_node()` takes 2 parameters:
1. name (String) *THIS IS THE FILE NAME OF THE **CSV** FILE*
2. location (String) *Optional, if not specified will be set to the project directory*

Returns: A DataNode object, with categories set to the columns of the CSV file

Once you have the DataNode object, you can use it to convert the file:

`csv_to_text()` takes 6 parameters:
1. datanode (DataNode)
2. ID (String) - The ID that all DataNodes added to the text file will be given
3. csv_name (String) - The file name of the CSV file
4. name (String) - The name of the text file
5. csv_location (String) *Optional, if not specified will be set to the project directory*
6. location (String) *Optional, if not specified will be set to the project directory*

```python
# Creates DataNode from CSV file
node = csv_to_node("tutorial.csv")

# Create text file to hold the data
create_file("tutorial.txt")

# Import CSV data into text file
csv_to_text(node, "Default", "tutorial.csv", "tutorial.txt")
```

### Text to CSV

Text to CSV is even easier, and uses a single function:

`text_to_csv()` takes 6 parameters:
1. datanode (DataNode)
2. csv_name (String) - The file name of the CSV file
3. name (String) - The name of the text file
4. csv_location (String) *Optional, if not specified will be set to the project directory*
5. location (String) *Optional, if not specified will be set to the project directory*

```python
# Creates a DataNode
person = DataNode(["Name", "Age", "Gender"])

create_file("PEOPLE.txt")

add_node(person, "Default", ["Bob", "57", "Male"], "test.txt")
add_node(person, "Default", ["Marie", "25", "Female"], "test.txt")
add_node(person, "Default", ["Jerry", "18", "Male"], "test.txt")

# Fill CSV file with data from text file
text_to_csv(person, "PEOPLE.csv", "PEOPLE.txt")
```

**The first column will include the IDs**

That is every current function in the DataRack library! We hope you find this module useful!

### Function List

**File Creation**
- create_file()
- clear_file()

**Adding Nodes**
- add_node()
- insert_node()

**Removing Nodes**
- remove_node()
- remove_by_id()
- remove_all_by_id()

**Replacing Nodes**
- replace_node()
- replace_by_id()
- replace_all_by_id()

**Reading Nodes**
- read_node()
- read_by_id()
- read_all_by_id()
- read_all()

**Filtering Nodes**
- find_node()

**Misc**

- get_idx_from_id()
- get_all_idx_from_id()

**CSV Conversion**

- csv_to_node()
- csv_to_text()
- text_to_csv()

**Remember: all functions in this module are also documented with docstrings. If you ever need help, use help(function name) in your python project**