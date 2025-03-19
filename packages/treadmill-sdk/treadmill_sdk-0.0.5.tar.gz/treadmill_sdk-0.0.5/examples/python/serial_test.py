# from asyncio import sleep
import serial

serial_port_name = "/dev/cu.usbmodem212201"
port = serial.Serial(serial_port_name, 115200, dsrdtr=True, timeout=1)
print(port)


# GET_SENSOR_CONFIG
data = b"BRNC\x02\x0c\x02\x00\x01\x03\x00\x10\x04[\xee"
# GET_DEVICE_INFO
data2 = b"BRNC\x02\x0c\x02\x00\x01\x03\x00\x10\x01\x9b\xed"
port.write(data) # recv ends with 'x03u\xb6'
port.write(data2)
port.write(data)
# print(f'send: {data}')

# sleep(0.1)

# read response
response = port.read(2000)
print("response:", response)

response = port.read(2000)
print("response:", response)

port.flushInput()
port.flushOutput()
port.close()
