def to_rep(x):
    ball = x//4096 + 1
    x = x%4096
    r = x//256 + 1
    x = x % 256
    b2 = x//16 + 1
    x = x%16
    b1 = x+1
    print(b1,b2,r,ball)

def to_num(x):
    b1,b2,r,ball = int(x[:2]), int(x[2:4]), int(x[4:6]), int(x[6])
    return (ball-1)*4096 + (r-1)*256 + (b2-1)*16 + (b1-1)
 
#n = int(input())
#to_rep(n)

state = input()
print(to_num(state))