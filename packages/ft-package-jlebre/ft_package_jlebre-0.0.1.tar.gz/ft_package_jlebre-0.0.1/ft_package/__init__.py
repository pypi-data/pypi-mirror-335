def count_in_list(list, stri):
    counter = 0
    
    for word in list:
        if word == stri:
            counter += 1
    
    return counter