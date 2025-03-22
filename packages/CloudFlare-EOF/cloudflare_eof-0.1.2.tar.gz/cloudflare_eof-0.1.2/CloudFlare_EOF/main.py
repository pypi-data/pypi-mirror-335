import urllib.parse
from bs4 import BeautifulSoup

# CloudFlare Email Obfuscation Fucker
# cf_email aka [email protected]
# Made by Elxss with Love :3 - 20/03/2025 WORKING
# https://github.io/Elxss

def decode_cf_email(html):
    """
    You Picked the wrong house, Fool !
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find(class_='__cf_email__')
        encoded = element['data-cfemail']

        key = int(encoded[:2], 16)
        decoded_bytes = []

        for i in range(2, len(encoded), 2):
            byte_value = int(encoded[i:i+2], 16) ^ key
            decoded_bytes.append(byte_value)

        safe_chars = bytes("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" "0123456789@*_+-./", 'utf-8')
        quoted = bytearray()

        for b in decoded_bytes:
            if b in safe_chars:
                quoted.append(b)
            else:
                hex_value = f'%{b:02X}'.encode()
                quoted.extend(hex_value)

        return urllib.parse.unquote(quoted.decode())
    
    except Exception as e:
        print(f"Error when decoding : {e}")
        return None


if __name__ == "__main__":
    html = '''<span class="__cf_email__" data-cfemail="aac5d8c3cfc4decbdec3c5c4eacfd9cfc584ccd8">[email protected]</span>'''
    print(decode_cf_email(html))