import binascii
import io
import os
import zipfile
import warnings
from .parser import parse_data_sector, parse_code_sector
try:
    from isobiscuit_engine import Engine
except:
    warnings.warn(
    "⚠️ Engine Warning: The optimized engine could not be loaded on your system. "
    "You are using a deprecated fallback version, which may be slower.",
    RuntimeWarning
)

    from .engine import Engine as Engine
from ..compiler.build import writeSectors
def hex_to_zipfile(zip):
    zip_bytes = binascii.unhexlify(zip)
    return io.BytesIO(zip_bytes)

def mount_zip_vfs(hex_string):
    zip_file = hex_to_zipfile(hex_string)  # Hex -> ZIP (In-Memory)
    
    return zip_file
        
def parse_biscuit(data_sector, code_sector, mem_sector, other_sector):
    data_sector = parse_data_sector(data_sector)
    code_sector = parse_code_sector(code_sector)
    return (data_sector, code_sector, mem_sector, other_sector)

def start_biscuit(biscuit_file, _data_sector, _code_sector, _mem_sector, _other_sector, _zip, debug=False):
    _zip = mount_zip_vfs(_zip)
    (data_sector, code_sector, mem_sector, other_sector) = parse_biscuit(_data_sector, _code_sector, _mem_sector, _other_sector)
    
    engine = Engine(data_sector, code_sector, {0: ""}, _zip, debug,)
    try:
        (zip) = engine.run()
    except KeyboardInterrupt:
        print("\n[INFO] Stopping Biscuit")
    
    save_biscuit(biscuit_file, _data_sector, _code_sector, _mem_sector, _other_sector, zip)
    _zip.close()
    zip.close()
def save_biscuit(biscuit_file, data_sector, code_sector, mem_sector, other_sector, _zip: io.BytesIO):
    zip = zipfile.ZipFile(_zip, "r", compression=zipfile.ZIP_DEFLATED)
    new_zip_bytes = io.BytesIO()
    with zipfile.ZipFile(new_zip_bytes, 'w', zipfile.ZIP_DEFLATED) as new_zip_file:
        for file_name in zip.namelist():
            file_data = zip.read(file_name)
            new_zip_file.writestr(file_name, file_data)

    new_zip_bytes.seek(0)
    new_zip_bytes_content = new_zip_bytes.read() 
    try:
        os.remove(biscuit_file)
    except:
        pass
    with open(biscuit_file, 'w+') as f:
        f.write("")
        f.write("bisc") #Magic Bytes
        f.write(str(binascii.unhexlify('0001').decode("utf-8"))) # Version
        f.write(str(binascii.unhexlify('00000000000000000000').decode("utf-8"))) # Zero Bytes

    writeSectors(biscuit_file[:-8], data_sector, code_sector, mem_sector, other_sector)
    
    with open(biscuit_file, "ab") as f:
        f.write(new_zip_bytes_content)
    

    
    