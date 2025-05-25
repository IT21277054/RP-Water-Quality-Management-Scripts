import pandas as pd
import time
import logging
import struct
from datetime import datetime
from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from threading import Thread

import time

for i in range(5):
    print(f"Starting SCADA system{'.' * (i + 1)}", end="\r", flush=True)
    time.sleep(0.5) 
print("\n")  
print("\n=======================================================================")

print("      ___           ___           ___           ___           ___     ")
print("     /\  \         /\  \         /\  \         /\  \         /\  \    ")
print("    /::\  \       /::\  \       /::\  \       /::\  \       /::\  \   ")
print("   /:/\ \  \     /:/\:\  \     /:/\:\  \     /:/\:\  \     /:/\:\  \  ")
print("  _\:\~\ \  \   /:/  \:\  \   /::\~\:\  \   /:/  \:\__\   /::\~\:\  \ ")
print(" /\ \:\ \ \__\ /:/__/ \:\__\ /:/\:\ \:\__\ /:/__/ \:|__| /:/\:\ \:\__\\")
print(" \:\ \:\ \/__/ \:\  \  \/__/ \/__\:\/:/  / \:\  \ /:/  / \/__\:\/:/  /")
print("  \:\ \:\__\    \:\  \            \::/  /   \:\  /:/  /       \::/  / ")
print("   \:\/:/  /     \:\  \           /:/  /     \:\/:/  /        /:/  /  ")
print("    \::/  /       \:\__\         /:/  /       \::/  /        /:/  /   ")
print("     \/__/         \/__/         \/__/         \/__/         \/__/    ")
print("=======================================================================")
print(" SCADA MODBUS SERVER - DATA INTEGRATION ")
print("=======================================================================\n")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)

EXCEL_FILE = "Sample.xlsx"
REGISTER_SIZE = 100
TAG_ID_TO_REGISTER = {5001: 0, 5002: 2, 5003: 4, 5004: 6, 5005: 8, 5006: 10}

store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [0] * 100),
    co=ModbusSequentialDataBlock(0, [0] * 100),
    hr=ModbusSequentialDataBlock(0, [0] * REGISTER_SIZE),
    ir=ModbusSequentialDataBlock(0, [0] * 100)
)

context = ModbusServerContext(slaves=store, single=True)

def update_registers():
    while True:
        try:
            df = pd.read_excel(EXCEL_FILE, engine="openpyxl")
            logging.info("Loaded Data from Excel: %s", df.head())

            for _, row in df.iterrows():
                tag_id = int(row['TagID'])
                value = float(row['Value']) if pd.notna(row['Value']) else 0.0

                if tag_id in TAG_ID_TO_REGISTER:
                    register_index = TAG_ID_TO_REGISTER[tag_id]
                    registers = list(struct.unpack("<HH", struct.pack("<f", value))) 
                    context[0].setValues(3, register_index, registers)

                    logging.info("Sent 1 Record: TagID %d -> Stored at Register %d (Value: %.2f)", tag_id, register_index, value)

                    time.sleep(1)
                else:
                    logging.warning("TagID %d is not mapped, skipping...", tag_id)

        except Exception as e:
            logging.error("Error processing data: %s", e)
            time.sleep(10)  


server_thread = Thread(target=StartTcpServer, args=(context,), kwargs={"address": ("0.0.0.0", 5020)})
server_thread.daemon = True
server_thread.start()


update_thread = Thread(target=update_registers)
update_thread.daemon = True
update_thread.start()

while True:
    time.sleep(1)
