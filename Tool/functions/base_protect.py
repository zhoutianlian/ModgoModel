##ZXW
import numpy as np
def BaseProtect(a1,a2,a3,b1,b2,b3):
    if type(a1)==np.float64:
        a1=a1.item()
    if type(a2)==np.float64:
        a2=a2.item()
    if type(a3)==np.float64:
        a3=a3.item()
    if type(b1)==np.float64:
        b1=b1.item()
    if type(b2)==np.float64:
        b2=b2.item()
    if type(b3)==np.float64:
        b3=b3.item()
    if type(a1)==int:
        a1=float(a1)
    if type(a2)==int:
        a2=float(a2)
    if type(a3)==int:
        a3=float(a3)
    if type(b1)==int:
        b1=float(b1)
    if type(b2)==int:
        b2=float(b2)
    if type(b3)==int:
        b3=float(b3)
    if type(a1)!=float or type(b1)!=float or type(a2)!=float or type(b2)!=float or type(a3)!=float or type(b3)!=float:
        raise("Wrong when use BaseProtect Function")
    total=a1*a1+a2*a2+a3*a3+b1*b1+b2*b2+b3*b3
    a=a1*a1+a2*a2+a3*a3
    b=b1*b1+b2*b2+b3*b3

    return [max(a1,round(a/total*a1+b/total*b1,2)),max(a2,round(a/total*a2+b/total*b2,2)),max(a3,round(a/total*a3+b/total*b3,2))]