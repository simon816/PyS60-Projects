#m_number = magic number
import random
alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\t'

def encode(string,m_number,output='',ignore='false', alpha=alphabet):
    for n in range(len(string)):
        m_number=m_number+1
        print 'm_number='+str(m_number)+'(encode)'
        current=string[n:n+1]
        print '\tcurrent='+current
        if alpha.find(current)>=0 or ignore=='true':
            alpha+=alphabet
            shift1=alpha.find(current)+m_number
            shift2=alpha.find(current)+1+m_number
            output+=alpha[shift1:shift2]
        else:
            try:
                if int(current) in range(0,10):
                    output+=current
                    print '\t'+current+' is a number'
            except:
                output+=chr(ord(current)+100)
    return output


def decode(string,m_number,output='', alpha=alphabet):
    for n in range(len(string)):
        m_number=m_number+1#-(len(alphabet)-1)
        print 'm_number='+str(m_number)
        current=string[n:n+1]
        print '\tcurrent='+current
        if alpha.find(current)>=0:
            #alpha+=alphabet
            shift1=alpha.find(current)-m_number+1
            shift2=alpha.find(current)+2-m_number
            output+=alpha[shift1:shift2]
        else:
            try:
                if int(current) in range(0,10):
                    output+=current
                    print '\t'+current+' is a number'
            except:
                en_char=string[n:n+1]
                de_char=ord(char)-100
                output+=chr(de_char)
    return output

def decodestring(string,alphabet):
    numOfLetters=int(float(string[:1]))
    begin=numOfLetters+1
    numRepOfLetters=alphabet.find(string[1:2])+1
    print 'letter shift number representation='+str(numRepOfLetters)
    magic=int(float(numRepOfLetters))
    print 'magic='+str(magic)
    return decode(str(string[begin:]),magic)

def encodestring(string, alphabet):
    rand=random.randint(1,len(alphabet)-1)
    shift=encode(str(rand), rand, '', 'true')
    print 'hidden shift='+shift
    print 'rand='+str(rand)
    append=str(len(str(rand)))+shift
    return encode(string, rand, append)

e=encodestring('12189', alphabet)
print e
d=decodestring(e,alphabet)
print d