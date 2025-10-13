from unetpy import UnetSocket

s = UnetSocket('localhost', 1102)
rx = s.receive()
print(f"from node {rx.from_}: {bytearray(rx.data).decode()}")
s.close()