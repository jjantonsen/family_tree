# Family Tree API v0.9.2

A simple API for creating, editing and visualizing your family tree.

- Storage is done using MongoDB
- Visualization is done using Dot graphs

All interaction with the family database is done through the FamilyTreeClient, which provides an interface for adding, deleting, searching and visualizing. 

Adding a person to the database:
```
import family_tree
client = family_tree.FamilyTreeClient()
client.add_person() # You will be prompted to add details one by one
```
The individuals stored in the database are assigned a unique database ID, which allows to connect them to other people in the database. An individual in the database is linked only to its parents, spouses and children.

Query database for database id of a person
```
client.search_person() # You will be prompted to provide first and last name. A list of query results with database IDs is returned.
```

Print the information of a specific person stored in the database
```
client.print_person_info(2, "nl") # Print name, gender, birth and death dates, and location of the person with database ID 2
client.print_person_info(2, "*") # Print all information of the person, including closest relatives and database metadata
```

Deleting a person from the database:
```
client.delete_person(12) # Delete the person with database ID 12. All links to other individials (and their links to this person) will also be deleted
```

Print the family tree:
```
client.print_tree() # Returns the family tree in .pdf-format (pdf, png, ps and jpg available)
```
![Sample family tree:](https://github.com/jjantonsen/family_tree/blob/master/my_family_tree.png)


Individuals are handled as Person objects.

Features to be added in the future:
- Editing of database info through the FamilyTreeClient
- Exporting database contents to other formats such as Excel, SQL ..

New in version 0.9.2
- Added support for multiple family trees
- Allowed printing of person information through Person.print_info and FamilyTreeClient.print_person_info
- Generalization of object names in code, all code is now in English
- Bug fixes

NOTE: This is a toy project created merely for the purpose of own learning and usage.

Written by Jørgen Antonsen, 2018
