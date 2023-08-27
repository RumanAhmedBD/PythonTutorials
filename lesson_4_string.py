#String Operation

#Slicing
str_var = "Hello World"
print("the first index is ", str_var[0])

#print 2nd index to 4th index
print(str_var[2:5])

#print 1st index to 5th index
print(str_var[0:5])
print(str_var[:5])

#print 4th index to last index
print(str_var[4:])


#String Modification
#Make a string upper case
print(str_var.upper())

#Make a string lower case
print(str_var.lower())

#Strip
#It removes any leading and following whitespace
str_var2 = "userid| |password|address"
print(str_var2)
print(str_var2.strip())

#Replace
print(str_var2.replace("Hello", "Hi"))

#Split
print(str_var2.split("|"))



var = "My name is Ruman"