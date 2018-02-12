Family Tree API v0.9

A simple API for storing, editing and visualizing your family tree.

- Storage is done using MongoDB (currently supports only one single family tree)
- Visualization is done using Dot graphs

All interaction with the family database is done through the FamilyTreeClient, which provides an interface for adding, deleting, searching and visualizing. 

Example of usage:
import family_tree
client = family_tree.FamilyTreeClient()
client.add_person() # You will be prompted to add details one by one

Individuals are handled as Person objects.

Features to be added in the future:
- Editing of database info through the FamilyTreeClient
- Multiple family trees
- Exporting database contents to other formats such as Excel, SQL ..


NOTE: This is a toy project created merely for the purpose of own learning and usage.

Written by Jørgen Antonsen, 2018
