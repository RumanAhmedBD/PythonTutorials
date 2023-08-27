
myvar = 1
my_var = 2
_my_var = 'test'
MYVAR = 10.2
MY_VAR = 'my capital var'
myVar = 34
my_var2 = 67

print('the var is ', myvar)
print('the var is ', my_var)
print('the var is ', _my_var)
print('the var is ', MYVAR)
print('the var is ', MY_VAR)
print('the var is ', myVar)
print('the var is ', my_var2)


#block 1
var1 = 1
var2 = 2
var3 = 3
#block 2
var1, var2, var3 = 1, 2, 3

#block 1 and tow are same
print(var1, var2, var3)


var1 = var2 = var3 = 1
print(var1, var2, var3)


x = 'Python is awesome'
print(x)

a = 'Python '
b = 'is '
c = 'awesome'

print(a+b+c)
#print(a+' '+ b + ' ' + c)


my_age2 = 10
my_age = 15.2
#print(my_age+my_age2)
title = 'My age is '
print(title+str(my_age))


#my_string_age = str(my_age)
#print(my_string_age, type(my_string_age))

print(str(my_age), ' is a ' ,type(str(my_age)))


# You have two var, sum those and save the value to a variable called sum

var1 = 1
var2 = 2
sum = var1 + var2

var1 = 10
var2 = 20 
sum = var1 + var2

var1 = 10
var2 = 20 
sum = var1 + var2

var1 = 30
var2 = 50
sum = var1 + var2

var1 = 100
var2 = 200
sum = var1 + var2

var1 = 10
var2 = 20 
sum = var1 + var2


#write a function called sum, which will take two arguments and sum it 
def sum(var1, var2):
    var_sum = var1 + var2
    print(var_sum)

sum(2,3)
sum(10,20)


