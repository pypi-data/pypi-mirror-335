# NameScript (NS)

Bahasa pemrograman sederhana dengan sintaks bahasa Indonesia, ditranspilasi ke Python.

![NameScript Logo](https://akuzz.my.id/img-C/LogoNS.png)  <!-- Ganti dengan logo Anda -->

## Instalasi

```bash
pip install namescript
```

## Cara Menggunakan

1. Jalankan File Langsung
```bash
ns jalankan program.ns
```

2. Cek Versi
```bash
ns versi
```

## Sintaks Dasar

1. Menampilkan Teks
```python
tampilkan "Halo Dunia!"  // Output: Halo Dunia!
```

2. Variabel
```python
d_nama = "Budi"
tampilkan "Halo " <d_nama>  // Output: Halo Budi
```

3. Input Pengguna
```python
d_umur = masukan("Berapa umurmu? ")
tampilkan "Umurmu: " <d_umur>
```

4. Operasi Matematika
```python
d_hasil = (5 <t> 3) <a> 2  // (5 + 3) * 2 = 16
tampilkan "Hasil: " <d_hasil>
```

5. Komentar
```python
// Ini adalah komentar
```

## Contoh Program

`demo.ns`
```python
d_nama = masukan("Siapa namamu? ")
tampilkan "Selamat datang, " <d_nama> "!"

d_angka1 = 10
d_angka2 = 5
d_total = d_angka1 <t> d_angka2 <a> 3  // (10 + 5) * 3
tampilkan "Total: " <d_total>
```

Output:
```bash
Siapa namamu? Andi
Selamat datang, Andi!
Total: 45
```

## Roadmap Pengembangan

**TAHAP 1: BeginnerSyntax (✓ Selesai)**
- Variabel, input/output
- Operasi matematika dasar
- CLI sederhana

**TAHAP 2: DeepSyntax (Dalam Pengembangan)**
- Fungsi custom
- Percabangan jika
- Perulangan ulangi

**TAHAP 3: Integrasi Web**
- Generator HTML/PHP
- Dukungan sintaks web

**TAHAP 4: Package Manager**
- Sistem instalasi package
- Dukungan modul eksternal

**TAHAP 5: Versi Stabil**
- Optimasi performa
- Dokumentasi lengkap

## Berkontribusi

1. Fork repositori
2. Buat branch fitur (`git checkout -b fitur-baru`)
3. Commit perubahan (`git commit -m 'Tambahkan fitur'`)
4. Push ke branch (`git push origin fitur-baru`)
5. Buat Pull Request

## Lisensi

MIT
