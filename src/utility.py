import os, re, lzf
from bs4 import BeautifulSoup as soup

def load(filename: str) -> (str, soup):
    """Takes a filename as input. Seperates text metadata from compressed XML"""
    with open(filename, 'rb') as f:

        raw_data = f.readlines()

        # discover previous data size
        tgt = next(i for i,s in enumerate(raw_data) if s.decode().startswith('Data'))
        data_size = int(raw_data[tgt].strip().decode('utf-8').replace('DataSize:=', ''))

        meta_data = ''
        compressed_data = b''

        # discover beginning of compression and store meta data
        compression_start = 0
        for i, line in enumerate(raw_data):
            try:
                meta_data += line.decode('utf-8')
            except UnicodeDecodeError:
                compression_start = i
                break

        # extract compressed data
        for line in raw_data[compression_start:]:
            compressed_data += line

        # decompress
        save_data = lzf.decompress(compressed_data, data_size).decode('utf-8')

        return meta_data, save_data

def save(filename, meta_data, save_data):

    data_size = len(save_data)
    compressed_data = lzf.compress(save_data)
    save_data_size = len(compressed_data)
    meta_data = update_meta_data(meta_data, data_size, save_data_size)

    with open(filename, 'wb+') as f:
        f.write(meta_data.encode('utf-8'))
        f.write(compressed_data)
    print(f'Data Size: {data_size}, SaveDataSize: {save_data_size}')

def update_meta_data(meta_data, data_size, save_data_size):
    # find/update DataSize and SaveDataSize 
    meta_data = re.sub('\sDataSize:=\d+\s', f'\nDataSize:={data_size}\n', meta_data)
    meta_data = re.sub('\sSaveDataSize:=\d+\s', f'\nSaveDataSize:={save_data_size}\n', meta_data)
    return meta_data


def parse(data):
    """
    """
    xml = soup(data, 'lxml-xml')
    characters = xml('pc')
    return xml

