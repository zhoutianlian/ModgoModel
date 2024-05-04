import math
def for_distribution(num,mx,mn,md):
    flag=0
    beg=mn+0.0
    step=(0.0+mx-mn)/(0.0+num)
    D=[]
    if mx-md==md-mn:
        a=1.96*2/(mx-mn)
        b=1.96-a*mx
        while  round(beg)<=round(mx):
            D.append(a*beg+b)
            beg+=step
    else:
        if md-mn>mx-md:
            md=mn+mx-md
            flag=1
        a=float(2*md-mx-mn)/float((mn-md)*(mx-md))
        b=1-a*md
        c=math.log(math.pow(math.e,1.96),(a*mx+b))
        # c=1.96/math.log((a*mx+b),math.e)

        while  round(beg)<=round(mx):
            #print c*math.log(a*beg+b,math.e)
            D.append( c*math.log(a*beg+b,math.e))
            beg+=step
    f=[]
    for e in D:
        a=1/(math.pow(2*math.pi,0.5))*math.pow(math.e,(-e*e/2))*100
        f.append(a)
    if flag==1:

        f=list(reversed(f))
    # for e in f:
    #     print(e)
    return f
# for_distribution(50,5000,-2000,-1000)