#table is a list with 3 in betweens

table =[[-1,-1,-1],[-1,-1,-1],[-1,-1,-1]]
printer = []


# 1 is x
# 0 is o
# -1 is blank



def tablestatus():
   for e in range(0, len(table)):
       if table[e][1] == table[e][2] and table[e][1]== table[e][3] and table[e][1] != -1:
           #print win
            return
       if table[1][e] == table[2][e] and table[1][e] == table[3][e] and table[e][1] != -1:
            #print win
            return 
   if table[1][1] == table[2][2] and table[1][1] == table[3][3] and table[e][1] != -1:
        return
   if table[3][1] == table[2][2] and table[3][1] == table[1][3] and table[e][1] != -1:
       return

def printable():
    for e in table:
        for i in e:
            if i ==














