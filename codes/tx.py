from unetpy import UnetSocket

s = UnetSocket('localhost', 1101)
s.send('hello!', 0)
s.close()