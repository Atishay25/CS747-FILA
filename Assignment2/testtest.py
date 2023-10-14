def to_rep(x):
    ball = x//4096 + 1
    x = x%4096
    r = x//256 + 1
    x = x % 256
    b2 = x//16 + 1
    x = x%16
    b1 = x+1
    return (b1-1)*512 + (b2-1)*32 + (r-1)*2 + (ball-1)

while 1:
    uska = int(input())
    print(to_rep(uska))
    