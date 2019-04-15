keywords = ['borrow', 'Bye']
string = 'I would like to borrow some books'
word = []

if any([word in string for word in keywords]):
    
    print word
print 'end'

matches = [word for word in keywords if word in string]
print matches