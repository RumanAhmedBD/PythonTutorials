#Global variable 
#Local variable

g_var = 12 #global variable

def sum():
    global func_var
    func_var = 10 #local variable
    print("The g_var is ", g_var)
    print("The Func var is ", func_var)

sum()
print(func_var)



'''
g_var = 4

def sum(var1, var2):
    result = var1+var2
    print("result before sum", result)
    g_var = 5
    print("the var from func", g_var)

sum(5, 5)
print("The var is ", g_var)
'''

'''
#Casting
int_var = 4
print(int_var, type(int_var))

#int --> float
float_var = float(int_var)
print(float_var, type(float_var))

#int-->string
str_var = str(int_var)
print(str_var, type(str_var))
'''