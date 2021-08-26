# Converts the dictionary to a list of tuples
# takes a file containing a dictionary in the form of a text file
# and converts it to a list of tuples

def convert_dict(str_dictionary):
    """
    Gets a file string and converts all curly braclets to
    brackets
    """
    # get the file
    file = open(str_dictionary, 'r')
    # get the file string
    str_dictionary = file.read()
    # close the file
    file.close()
    
    new_string = str_dictionary.replace("{", "[")
    new_string = new_string.replace("}", "]")
    new_string = new_string.replace(", ", "), (")
    new_string = new_string.replace("[ ", "[(")
    new_string = new_string.replace(" ],", ")],")
    new_string = new_string.replace("\": ", "**")
    new_string = new_string.replace(": ", ", ")
    new_string = new_string.replace("**", "\": ")
    return new_string
        
    

# test
if __name__ == '__main__':
    print(convert_dict('infoset_to_action.txt'))