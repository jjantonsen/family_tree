# -*- coding: utf-8 -*-
"""

Classes and functions for creating a family tree,
a network of Persons that includes life information
about the individual Persons

TODO:
- Write export functions (excel, other formats)
- Finish incomplete/unwritten functions
- Prevent 'illegal' input, e.g.:
  * referencing to non-existing database IDs
  * repeating database IDs in a list
  * adding children that already has children
- Overall bug testing

IDEAS:
Implementation of drawing the family tree using dot:
- consider having a timeline graph on the side of the tree,
  optionally as an add-on. shape=plaintext, listing generations,
  e.g. 1st, 2nd, 3rd ..

Author:
    Jørgen Antonsen

Date: 2017-12-07
    

"""

import datetime
import pymongo
import json
import os
from subprocess import check_call

DB_NAME = "family_tree"
COLLECTION = "my_family_tree"
CLIENT = pymongo.MongoClient()[DB_NAME]


class Person():
    """
    Class that holds a person's information, including:
    - name and gender
    - closest relatives (links)
    - life details
    - database details
    """
    # Name and gender
    first_name = ""
    middle_name = ""
    last_name = ""
    gender = ""

    # Closest relatives
    mother = -1 # database ID
    father = -1 # same 
    spouses = [] # list of same type of link
    children = [] # same

    # Life details
    birth_date = None
    death_date = None
    birth_place = ""
    death_place = ""
    occupation = "" # 'main' occupation
    life_story = ""
    
    # Database details
    database_ID = -1
    comment = ""
    add_date = None
    version = 0
    last_change_date = None
    

    def setup(self, first_name, middle_name, last_name, gender, mother, father, spouses, children, birth_date, death_date, birth_place, death_place, occupation, life_story, comment, collection=COLLECTION):
        """ set the attributes of the Person """
        assert self.version == 0, "The person has already been initialized"

        self.collection = collection

        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.gender = gender
        
        self.mother = mother
        self.father = father
        self.spouses = spouses
        self.children = children
        
        self.birth_date = birth_date
        self.death_date = death_date
        self.birth_place = birth_place
        self.death_place = death_place
        self.occupation = occupation
        self.life_story = life_story
        
        self.database_ID = self.__get_db_id()
        self.comment = comment
        self.add_date = datetime.datetime.now()
        self.__update()


    def from_db_data(self, first_name, middle_name, last_name, gender, mother, father, spouses, children, birth_date, death_date, birth_place, death_place, occupation, life_story, database_id, comment, add_date, version, last_change_date, _id='', collection=COLLECTION):
        """
        Loads the data from a database entry (unpacked dict)
        Example call: Person.from_db_data(**db_query_dict)
        """
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.gender = gender
        
        self.mother = mother
        self.father = father
        self.spouses = spouses
        self.children = children
        
        self.birth_date = birth_date
        self.death_date = death_date
        self.birth_place = birth_place
        self.death_place = death_place
        self.occupation = occupation
        self.life_story = life_story
        
        self.database_ID = database_id
        self.comment = comment
        self.add_date = add_date
        self.version = version
        self.last_change_date = last_change_date

        self.collection = collection


    def delete(self):
        """ Deletes person from database """
        failure_msg = "Was not able to delete the person from database"
        # First remove the person from its relations' links
        self.__update_other_fields(append=False)

        # Then remove the person itself
        try:
            del_result = CLIENT[self.collection].delete_one({"database_id":self.database_ID})
            assert del_result.acknowledged, failure_msg
        except:
            raise Exception(failure_msg)


    def __update(self):
        self.version += 1
        self.last_change_date = datetime.datetime.now()

        
    def print_info(self, verbose="n"):
        """
        Prints person details in a readable format
        verbose = n : prints name, gender and birth dates
        verbose = l : location - includes birth and death place
        verbose = i : info - includes occupation and life information
        verbose = f : family - includes names of closest family members
        verbose = d : database - includes database details
        verbose = * : print all available information, equivalent to "nlifd"

        Example: verbose = "nlf", includes name, gender, location and family
        """
        assert isinstance(verbose, str), "Parameter verbose must be of type str"
        if verbose == "*":
            verbose = "nlifd"

        if "n" in verbose:
            # Name
            print("First name: {}".format(self.first_name))
            print("Middle name: {}".format(self.middle_name))
            print("Last name: {}".format(self.last_name))
            
            # Gender
            print("Gender: {}".format(self.gender))

            # Dates
            if isinstance(self.birth_date, datetime.datetime):
                print(self.birth_date.strftime("Birth date: %Y-%m-%d"))
            else:
                print("Birth date:")
            if isinstance(self.death_date, datetime.datetime):
                print(self.death_date.strftime("Death date: %Y-%m-%d"))
            else:
                print("Death date:")

        if "l" in verbose:
            # Birth and death places
            print("Birth place: {}".format(self.birth_place))
            print("Death place: {}".format(self.death_place))
        
        if "i" in verbose:
            # Information
            print("Occupation: {}".format(self.occupation))
            print("Life story: {}".format(self.life_story))

        if "f" in verbose:
            # Family members
            print("Mother: {}".format(self.__get_and_summarize_person(self.mother)))
            print("Father: {}".format(self.__get_and_summarize_person(self.father)))
            for spouse in self.spouses:
                print("Spouse: {}".format(self.__get_and_summarize_person(spouse)))
            for child in self.children:
                print("Child: {}".format(self.__get_and_summarize_person(child)))
        
        if "d" in verbose:
            # Database details
            print("Comment: {}".format(self.comment))
            print("Database ID: {}".format(self.database_ID))
            print("Version: {}".format(self.version))
            print(self.add_date.strftime("Add date: %Y-%m-%d"))
            print(self.last_change_date.strftime("Last change date: %Y-%m-%d"))


    def __get_and_summarize_person(self, db_id):
        """
        Return a one-line string with name, birth and death year of a person 
        in the database with database id db_id
        """
        if db_id == -1:
            return ""

        person = CLIENT[self.collection].find_one({"database_id": db_id})
        if person is None:
            print("Person with database id {} not found".format(db_id))
            return ""
        else:
            first_name = person["first_name"]
            middle_name = person["middle_name"]
            if middle_name != "":
                middle_name = " " + middle_name
            last_name = person["last_name"]
            birth_date = person["birth_date"]
            death_date = person["death_date"]
            if birth_date is None:
                if death_date is None:
                    date_str = ""
                else:
                    date_str = "- {}".format(death_date.year)
            else:
                if death_date is None:
                    date_str = "{} - ".format(birth_date.year)
                else:
                    date_str = "{} - {}".format(birth_date.year, death_date.year)

        return "{}{} {} {}".format(first_name, middle_name, last_name, date_str)


    def __get_db_id(self):
        """
        Returns a new database id,
        equal to the largest existing id + 1
        """
        try:
            return CLIENT[self.collection].find_one(sort=[("database_id",-1)])["database_id"]+1
        except: # Database does not exist
            return 1


    def add_to_db(self):
        """
        Stores person to database
        """
        assert self.version > 0, "Person not initialized"

        # Name and gender
        db_doc={
            "database_id":self.database_ID,
            "first_name":self.first_name,
            "middle_name":self.middle_name,
            "last_name":self.last_name,
            "gender":self.gender,
            "mother":self.mother,
            "father":self.father,
            "spouses":self.spouses,
            "children":self.children,
            "birth_date":self.birth_date,
            "death_date":self.death_date,
            "birth_place":self.birth_place,
            "death_place":self.death_place,
            "occupation":self.occupation,
            "life_story":self.life_story,
            "comment":self.comment,
            "add_date":self.add_date,
            "version":self.version,
            "last_change_date":self.last_change_date
        }
        CLIENT[self.collection].insert_one(db_doc)
        self.__update_other_fields(append=True)


    def __update_other_fields(self, append):
        """
        Updates the database entries of the Person's relations
        if append == True, the persons id is added to its relations
        if append == False, the persons id is removed from its relations
        """
        if self.mother != -1:
            self.__update_other_lists(self.mother, "children", append)

        if self.father != -1:
            self.__update_other_lists(self.father, "children", append)

        if isinstance(self.children, list) and self.children != []:
            self.__update_children(append) 

        if isinstance(self.children, list) and self.spouses != []:
            for spouses in self.spouses:
                self.__update_other_lists(spouses, "spouses", append)


    def __update_other_lists(self, other_db_id, link_field, append):
        """ Updates the other persons list of a Person's parent """
        other_data = CLIENT[self.collection].find_one({"database_id":other_db_id})
        relation_list = other_data[link_field]
        other_version = other_data["version"]
        if append:
            if self.database_ID not in relation_list:
                relation_list.append(self.database_ID)
        else:
            if self.database_ID in relation_list:
                relation_list.remove(self.database_ID)
        CLIENT[self.collection].update({"database_id": other_db_id},
                                   {"$set": {link_field: relation_list,
                                             "version": other_version+1,
                                             "last_change_date": datetime.datetime.now()}},
                                   upsert=False)

    
    def __update_children(self, append):
        if self.gender == "M":
            relation = "father"
        elif self.gender == "F":
            relation = "mother"
        else:
            print("Gender unknown, unable to register parent status for children")
            return 0
        
        if append:
            new_relation_value = self.database_ID
        else:
            new_relation_value = -1

        for child in self.children:
            child_version = CLIENT[self.collection].find_one({"database_id":child})["version"]
            CLIENT[self.collection].update({"database_id": child},
                                       {"$set":{relation: new_relation_value,
                                                "version": child_version+1,
                                                "last_change_date": datetime.datetime.now(),
                                                "last_change_date":datetime.datetime.now()}},
                                       upsert=False)


class FamilyTreeClient():
    """
    Interaction with the family tree stored in the database,
    including adding, loading, deleting and querying persons.
    Also includes functionality for printing the family tree,
    and switching between trees.
    """
    def __init__(self, collection=COLLECTION):
        self.collection = collection
        try:
            self.db = CLIENT[collection]
            print("Current family tree: {}\nNumber of persons: {}"\
                  .format(self.collection, self.db.count()))
        except:
            raise Exception("Unable to open collection {}".format(self.collection))


    def change_tree(self, new_collection):
        """ Change current family tree """
        self.__init__(collection=new_collection)


    def list_family_trees(self):
        """ Print a list of the existing family trees """
        for collection in CLIENT.collection_names():
            print("{},\t{} persons".format(collection,
                                           CLIENT[collection].count()))


    def add_person(self):
        """ Add a person to the database """
        # Name and gender
        first_name = input("First name: ")
        middle_name = input("Middle name: ")
        last_name = input("Last name: ")
        gender = ""
        while not gender in ["M", "F"]:
            gender = input("Gender (M/F): ").upper()

        # Closest relatives
        print("Adding relatives (enter ? to run a database query):")
        mother = self.__add_relative(one=True, input_str="Mother database ID: ")
        father = self.__add_relative(one=True, input_str="Father database ID: ")
        spouses = self.__add_relative(one=False, input_str="Spouses database ID: ")
        children = self.__add_relative(one=False, input_str="Children database ID: ")

        # Life details
        birth_date = self.__get_date("Birth")
        death_date = self.__get_date("Death")
        birth_place = input("Birth place: ")
        death_place = input("Death place: ")
        occupation = input("Occupation: ")
        life_story = input("Life story: ")
        
        # Database details
        comment = input("Comments: ")
    
        person = Person()
        person.setup(first_name,
                     middle_name,
                     last_name,
                     gender,
                     mother,
                     father,
                     spouses,
                     children,
                     birth_date,
                     death_date,
                     birth_place,
                     death_place,
                     occupation,
                     life_story,
                     comment,
                     self.collection)
        person.add_to_db()
        print("Person added to database with database ID {}".format(person.database_ID))


    def change_person(self):
        """ TODO: Change one or more attributes of a person already in the database """
        user_input = self.__db_id_prompt()
        if user_input == "":
            self.__abort_query()
            return 0
        else:
            more_input = True
            if user_input == "?":
                self.search_person()
                user_input = self.__db_id_prompt()
            elif user_input == "":
                self.__abort_query()
                return 0
            person = self.load_person(user_input)
            self.__print_entry(person)
            

    def delete_person(self):
        """ Delete a person from the database """
        user_input = self.__db_id_prompt()
        if user_input == "":
            self.__abort_query()
        else:
            more_input = True
            while more_input:
                if user_input == "?": # Run database query
                    self.search_person()
                    user_input = self.__db_id_prompt()
                elif user_input == "": # Abort query
                    self.__abort_query()
                    more_input = False
                else: # Delete person from given database id
                    try:
                        db_id = int(user_input)
                    except:
                        raise ValueError("Input not valid: {}".format(user_input))

                    in_db = self.search_id(db_id, verbose=False)
                    print("Found person: {}".format(in_db))
                    if in_db: # Ask for confirmation, then delete
                        confirm = input("Delete person? (Y/N): ")
                        if confirm.upper() == "Y":
                            person = self.load_person(db_id)
                            person.delete()
                            more_input = False
                        else:
                            self.__abort_query()
                            more_input = False
                    else: # If entered database id did not exist
                        print("Database ID not found.")
                        user_input = self.__db_id_prompt()


    def load_person(self, db_id):
        """ Returns Person object of person in database with database_id == db_id"""
        results = self.db.find_one({"database_id":db_id})
        if results == None:
            print("Database ID {} not found".format(db_id))
            return None
        else:
            person = Person()
            person.from_db_data(**results, collection=self.collection)
            return person

            
    def print_person_info(self, db_id, verbose = "n"):
        """
        Prints person details in a readable format.
        For details, see Person.print_info

        verbose = n : prints name, gender and birth dates
        verbose = l : location - includes birth and death place
        verbose = i : info - includes occupation and life information
        verbose = f : family - includes names of closest family members
        verbose = d : database - includes database details
        verbose = * : print all available information, equivalent to "nlifd"

        Example: verbose = "nlf", includes name, gender, location and family
        """
        person = self.load_person(db_id)
        person.print_info(verbose)


    def __db_id_prompt(self):
        return input("Enter database id (enter ? to run a database query): ")


    def __abort_query(self):
        print("Aborting.")


    def __add_relative(self, one, input_str):
        """
        Add relatives of a person, supported by database queries
        if one == False, the relatives are returned as a list
        """
        relative_list = []
        user_input = input(input_str)
        if user_input == "": # No relatives to be registered
            if one:
                return -1
            else:
                return []
        else: # Add one or more relatives
            more_input = True
            while more_input:
                if user_input == "?": # Run database query
                    self.search_person()
                    user_input = input(input_str)
                elif user_input == "":
                    more_input = False
                else: # Register one or more relatives
                    print("Adding:")
                    in_db = self.search_id(int(user_input))
                    if in_db:
                        if one:
                            return int(user_input)
                        else:
                            relative_list.append(int(user_input))
                            user_input = input("Enter a database ID or ? to add another person to this list, or pass enter to continue: ")
                            if len(user_input) == 0:
                                return relative_list
                    else: # If entered database id did not exist
                        user_input = input(input_str)


    def search_id(self, db_id, verbose=True):
        """ Query database on database_id and return results """
        results = self.db.find_one({"database_id":db_id})
        if results == None:
            if verbose:
                print("Database ID {} not found".format(db_id))
            return False
        else:
            if verbose:
                self.__print_entry(results)
            return True


    def search_person(self):
        """
        Query database on name and return results.
        No input returns all persons in the database.
        """
        print("Running database query:")
        first_name = input("First name: ")
        last_name = input("Last name: ")
        results = self.db.find({"first_name":{"$regex":first_name},
                                "last_name":{"$regex":last_name}})
        for persons in results:
            self.__print_entry(persons)
    

    def __print_entry(self, entry):
        """ Prints short details of a person """
        if isinstance(entry["birth_date"], datetime.datetime):
            yob = " {} -".format(entry["birth_date"].year)
        else:
            yob = ""
        if isinstance(entry["death_date"], datetime.datetime):
            yod = " {}".format(entry["death_date"].year)
        else:
            yod = ""
        if entry["middle_name"] == "":
            middle_name = ""
        else:
            middle_name = "{} ".format(entry["middle_name"])
    
        print("{} {} {}{}\t{}{}".format(entry["database_id"],
                                      entry["first_name"],
                                      middle_name,
                                      entry["last_name"],
                                      yob,
                                      yod))


    def __get_date(self, head_str=""):
        """ Query user for date input, and parse """
        y = input(head_str+" year: ")
        m = input(head_str+" month: ")
        d = input(head_str+" day: ")
        try:
            return datetime.datetime(int(y),int(m),int(d))
        except:
            print("No date registered")
            return None
    

    def print_tree(self, output_format="pdf", filename=""):
        """
        Print the entire family tree.
        The variable output_format specifies the output format of the resulting graph.
        This function requires Dot to be installed on your computer.
        Valid output formats are pdf, png, jpg and ps.

        Assumptions (to simplify the code):
        - only male - female marriages
        - maximum one spouse per person
        """
        # Parse input
        out_ext = output_format.lower()
        format_list = ["pdf", "png", "jpg", "ps"]
        assert out_ext in format_list, "Illegal output format. output_format must be one of the following: {}".format(format_list)
        if filename == "":
            filename = self.collection
        else:
            assert filename.split(".")[-1] != out_ext, "filename must include correct file extension: .{}".format(out_ext)

        # Initialize the file
        fh = open("{}.gv".format(filename), "w")
        fh.write("graph G {\n")
        fh.write("\t splines = ortho;\n")

        max_id =  self.db.find_one(sort=[("database_id",-1)])["database_id"]
        printed = [] # list of nodes printed
        for db_id in [i+1 for i in range(max_id)]:
            person = self.load_person(db_id)
            
            if person is not None:
                # Make the node of the person
                fh.write("\t {}".format(self._print_node(person)))
                
                # Print its tree
                if isinstance(person.spouses, list) and len(person.spouses) > 0:
                    # Spouse exist: Print invisible node between spouses
                    if person.gender == "M":
                        inode_id_1 = "{}i1".format(db_id)
                        inode_id_2 = "{}i2".format(db_id)
                        fh.write("\t {{rank = same; p{}; p{}; p{};}}\n".format(db_id, inode_id_1, person.spouses[0]))
                    else:
                        inode_id_1 = "{}i1".format(person.spouses[0])
                        inode_id_2 = "{}i2".format(person.spouses[0])
                        
                    if inode_id_1 not in printed:
                        fh.write("\t {}".format(self._print_invisible_node(inode_id_1)))
                        printed.append(inode_id_1)

                    if person.gender == "M":
                        fh.write("\t {}".format(self._print_link(db_id, inode_id_1)))
                    else:
                        fh.write("\t {}".format(self._print_link(inode_id_1, db_id)))

                    # Spouse and children: Write invisible node with link to children
                    if isinstance(person.children, list) and len(person.children) > 0 and (inode_id_2 not in printed):
                        fh.write("\t {}".format(self._print_invisible_node(inode_id_2)))
                        printed.append(inode_id_2)
                    if person.gender == "M":
                        fh.write("\t {}".format(self._print_link(inode_id_1, inode_id_2)))
                        for child in person.children:
                            fh.write("\t {}".format(self._print_link(inode_id_2, child)))

                elif isinstance(person.children, list) and len(person.children) > 0:
                # No spouse, but children: Only print invisible note with link to children
                    inode_id_2 = "{}i1".format(db_id)
                    if inode_id_2 not in printed:
                        fh.write("\t {}".format(self._print_invisible_node(inode_id_2)))
                        printed.append(inode_id_2)
                    if person.gender == "M":
                        fh.write("\t {}".format(self._print_link(db_id, inode_id_2)))
                        for child in person.children:
                            fh.write("\t {}".format(self._print_link(inode_id_2, child)))

        # Close file
        fh.write("}\n")
        fh.close()

        # Convert to graph
        check_call(["dot",
                    "-T{}".format(out_ext),
                    "{}.gv".format(filename),
                    "-o",
                    "{}.{}".format(filename, out_ext)])

        print("Family tree exported to file {}.{}".format(filename, out_ext))
    

    def _print_node(self, person):
        """ Print the node of a Person in Dot format """
        if isinstance(person.death_date, datetime.datetime):
            death_year = person.death_date.year
        else:
            death_year = ""
        if isinstance(person.birth_date, datetime.datetime):
            birth_year = person.birth_date.year
        else:
            birth_year = ""
        return "p{} [shape=box, label=\"{} {}\\n{} - {}\"];\n".format(person.database_ID,
                                                                   person.first_name,
                                                                   person.last_name,
                                                                   birth_year,
                                                                   death_year)


    def _print_invisible_node(self, node_id):
        return "p{} [style=invis, label=\"\", width=0, height=0];\n".format(node_id)


    def _print_link(self, node_id_1, node_id_2):
        return "p{} -- p{};\n".format(node_id_1, node_id_2)

        
