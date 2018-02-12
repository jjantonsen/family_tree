Family Tree API v0.9

A simple API for storing, editing and visualizing your family tree.

- Storage is done using MongoDB (currently supports only one single family tree)
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

Deleting a person from the database:
```
client.delete_person(12) # Delete the person with database ID 12. All links to other individials (and their links to this person) will also be deleted
```

Print the family tree:
```
client = family_tree.print_tree() # Returns the family tree in .pdf-format (pdf, png, ps and jpg available)
```

Individuals are handled as Person objects.

Features to be added in the future:
- Editing of database info through the FamilyTreeClient
- Multiple family trees
- Exporting database contents to other formats such as Excel, SQL ..


NOTE: This is a toy project created merely for the purpose of own learning and usage.

Written by Jørgen Antonsen, 2018
