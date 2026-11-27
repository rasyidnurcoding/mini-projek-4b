import csv

FILE_CSV = "jumlah-ruang-kelas-menurut-kondisi-semua-wilayah-sd-mi-sederajat-1-kabupaten-2023,2024-ASC.csv"
KOLOM_WAJIB = ["Periode", "Provinsi", "Kode Provinsi", "Kota/Kab", "Kode Kota/Kab", "Status Sekolah", "Baik", "Rusak Ringan", "Rusak Sedang", "Rusak Berat", "Jumlah"]

def baca_dataset():
    data = []
    jumlah_error = 0

    try:
        with open(FILE_CSV, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                print("Error: Dataset tidak memiliki header.")

            elif not all(kolom in reader.fieldnames for kolom in KOLOM_WAJIB):
                kolom_hilang = [kolom for kolom in KOLOM_WAJIB if kolom not in reader.fieldnames]
                print("Error: Kolom berikut tidak ditemukan:")
                for kolom in kolom_hilang:
                    print(f"- {kolom}")

            else:
                for nomor_baris, row in enumerate(reader, start=2):
                    try:
                        if not row["Provinsi"].strip() or not row["Kota/Kab"].strip():
                            raise ValueError("Provinsi atau Kota/Kab kosong")

                        if row["Status Sekolah"].strip() != "Negeri dan Swasta":
                            continue

                        baik         = konversi_angka(row["Baik"])
                        rusak_ringan = konversi_angka(row["Rusak Ringan"])
                        rusak_sedang = konversi_angka(row["Rusak Sedang"])
                        rusak_berat  = konversi_angka(row["Rusak Berat"])
                        jumlah       = konversi_angka(row["Jumlah"])

                        if min(baik, rusak_ringan, rusak_sedang, rusak_berat, jumlah) < 0:
                            raise ValueError("Terdapat nilai negatif pada data ruang kelas")

                        total_rusak             = rusak_ringan + rusak_sedang + rusak_berat
                        row["Baik"]             = baik
                        row["Rusak Ringan"]     = rusak_ringan
                        row["Rusak Sedang"]     = rusak_sedang
                        row["Rusak Berat"]      = rusak_berat
                        row["Jumlah"]           = jumlah
                        row["Status_Kerusakan"] = klasifikasi_kerusakan(total_rusak, jumlah)

                        data.append(row)

                    except Exception:
                        jumlah_error += 1
                        continue

                if len(data) == 0:
                    print("\nERROR: Dataset kosong atau tidak memiliki data valid.")
                    return None

                print("\nDataset berhasil dimuat.")
                print(f"Jumlah data kabupaten/kota valid : {len(data)}")

                if jumlah_error > 0:
                    print(f"Jumlah baris dilewati/tidak valid : {jumlah_error}")

                return data

    except FileNotFoundError:
        print("\nERROR: File CSV tidak ditemukan.")
        print("Pastikan file Python dan file CSV berada dalam satu folder.")
        return None

    except UnicodeDecodeError:
        print("\nERROR: Format encoding file CSV tidak dapat dibaca.")
        return None

def konversi_angka(nilai):
    teks = str(nilai).strip()
    if teks == "":
        return 0.0
    if teks.count(".") == 1 and len(teks.split(".")[1]) == 3:
        teks = teks.replace(".", "")
    return float(teks)

def klasifikasi_kerusakan(total_rusak, jumlah_kelas):
    if jumlah_kelas <= 0 or total_rusak <= 0:
        return "Aman"

    persen_rusak = (total_rusak / jumlah_kelas) * 100
    if persen_rusak   > 25:
        return "Kritis"
    elif persen_rusak > 10:
        return "Perlu Perhatian"
    else:
        return "Ringan"

def format_angka(nilai):
    return f"{nilai:,.1f}"

def format_rupiah(nilai):
    return f"Rp {nilai:,.0f}"

def login():
    peran = {"1": "Mahasiswa", "2": "Dosen", "3": "Masyarakat Umum"}

    print("\nPILIH PERAN PENGGUNA")
    for kode, nama_peran in peran.items():
        print(f"{kode}. {nama_peran}")

    while True:
        pilihan = input("Masuk sebagai (1-3): ").strip()
        if pilihan in peran:
            print(f"\nBerhasil masuk sebagai {peran[pilihan]}. Selamat datang!\n")
            return peran[pilihan]
        print("\nPilihan tidak valid. Silakan pilih 1, 2, atau 3.\n")

def daftar_provinsi(data):
    daftar       = []
    daftar_kunci = []

    for row in data:
        key     = row["Provinsi"].strip().lower()
        tampil = row["Provinsi"].strip().title()

        if key and key not in daftar_kunci:
            daftar_kunci.append(key)
            daftar.append((key, tampil))

    return daftar

def pilih_provinsi(data, pesan="Pilih nomor provinsi"):
    daftar = daftar_provinsi(data)

    print("\nDAFTAR PROVINSI:")
    for idx, (_, tampil) in enumerate(daftar, start=1):
        print(f"{idx:2}. {tampil}")

    while True:
        pilihan = input(f"\n{pesan} (1-{len(daftar)}): ").strip()
        if pilihan.isdigit():
            nomor = int(pilihan)
            if 1 <= nomor <= len(daftar):
                return daftar[nomor - 1]
        print(f"Pilihan tidak valid. Masukkan angka 1 sampai {len(daftar)}.")

def cari_data_provinsi(data, key_provinsi):
    return [row for row in data if row["Provinsi"].strip().lower() == key_provinsi]

def hitung_total(data_provinsi):
    total = {
        "Baik": 0.0,
        "Rusak Ringan": 0.0,
        "Rusak Sedang": 0.0,
        "Rusak Berat": 0.0,
        "Jumlah": 0.0}

    for row in data_provinsi:
        for kolom in total:
            total[kolom] += row[kolom]

    return total

def tampilkan_total(nama_provinsi, total):
    total_rusak = total["Rusak Ringan"] + total["Rusak Sedang"] + total["Rusak Berat"]
    status = klasifikasi_kerusakan(total_rusak, total["Jumlah"])

    print(f"\nHASIL DATA PROVINSI {nama_provinsi.upper()}")
    print(f"Ruang Kelas Baik     : {format_angka(total['Baik'])}")
    print(f"Rusak Ringan         : {format_angka(total['Rusak Ringan'])}")
    print(f"Rusak Sedang         : {format_angka(total['Rusak Sedang'])}")
    print(f"Rusak Berat          : {format_angka(total['Rusak Berat'])}")
    print(f"Total Ruang Kelas    : {format_angka(total['Jumlah'])}")
    print(f"Status Kerusakan     : {status}")

def menu_peringatan(data):
    print("\nMENU PERINGATAN KERUSAKAN")

    key_prov, nama_prov = pilih_provinsi(data, "Pilih nomor provinsi")
    data_provinsi = cari_data_provinsi(data, key_prov)

    if not data_provinsi:
        print("Data provinsi tidak ditemukan.")
        return

    total = hitung_total(data_provinsi)
    tampilkan_total(nama_prov, total)

    print("\nDAFTAR KABUPATEN/KOTA DENGAN KERUSAKAN")
    print(f"{'Kab/Kota':30} | {'Ringan':10} | {'Sedang':10} | {'Berat':10} | {'Status':16}")
    print("-" * 89)

    jumlah_wilayah_rusak = 0

    for row in data_provinsi:
        total_rusak = row["Rusak Ringan"] + row["Rusak Sedang"] + row["Rusak Berat"]
        if total_rusak > 0:
            jumlah_wilayah_rusak += 1
            print(f"{row['Kota/Kab']:30} | {format_angka(row['Rusak Ringan']):>10} | {format_angka(row['Rusak Sedang']):>10} | {format_angka(row['Rusak Berat']):>10} | "
                f"{row['Status_Kerusakan']:16}")

    print(f"\nJumlah kabupaten/kota dengan kerusakan: {jumlah_wilayah_rusak}")
    if jumlah_wilayah_rusak == 0:
        print("Tidak terdapat kerusakan ruang kelas.")

def menu_perbandingan(data):
    print("\nMENU PERBANDINGAN 2 PROVINSI")

    key1, prov1 = pilih_provinsi(data, "Pilih nomor provinsi pertama")
    key2, prov2 = pilih_provinsi(data, "Pilih nomor provinsi kedua")

    if key1 == key2:
        print("\nPeringatan: Provinsi yang dipilih sama.")
        print("Pilih dua provinsi yang berbeda.")
        return

    data1 = cari_data_provinsi(data, key1)
    data2 = cari_data_provinsi(data, key2)

    if not data1 or not data2:
        print("Data provinsi tidak ditemukan.")
        return

    total1 = hitung_total(data1)
    total2 = hitung_total(data2)

    print("\nHASIL PERBANDINGAN PROVINSI")
    print(f"{'Kategori':20} | {prov1:25} | {prov2:25}")
    print("-" * 77)

    for kolom in ["Baik", "Rusak Ringan", "Rusak Sedang", "Rusak Berat", "Jumlah"]:
        print(f"{kolom:20} | {format_angka(total1[kolom]):>25} | {format_angka(total2[kolom]):>25}")

    total_kerusakan1 = total1["Rusak Ringan"] + total1["Rusak Sedang"] + total1["Rusak Berat"]
    total_kerusakan2 = total2["Rusak Ringan"] + total2["Rusak Sedang"] + total2["Rusak Berat"]

    print("\nANALISIS PERBANDINGAN")
    for label, val1, val2 in [
        ("ruang kelas rusak berat", total1["Rusak Berat"], total2["Rusak Berat"]),
        ("jumlah ruang kelas", total1["Jumlah"], total2["Jumlah"]),
        ("total kerusakan ruang kelas", total_kerusakan1, total_kerusakan2),]:

        if val1 > val2:
            print(f"{prov1} memiliki {label} lebih banyak.")
        elif val1 < val2:
            print(f"{prov2} memiliki {label} lebih banyak.")
        else:
            print(f"{label.capitalize()} kedua provinsi sama.")

def input_biaya(pesan):
    while True:
        try:
            biaya = float(input(pesan))
            if biaya < 0:
                print("Peringatan: Biaya tidak boleh negatif.")
                continue
            return biaya
        except ValueError:
            print("Input tidak valid. Masukkan angka biaya.")

def menu_anggaran(data):
    print("\nMENU ANGGARAN BIAYA")

    key_prov, nama_prov = pilih_provinsi(data, "Pilih nomor provinsi")
    data_provinsi = cari_data_provinsi(data, key_prov)

    if not data_provinsi:
        print("Data provinsi tidak ditemukan.")
        return

    total = hitung_total(data_provinsi)

    print(f"\nDATA KERUSAKAN RUANG KELAS - {nama_prov.upper()}")
    print(f"Rusak Ringan : {format_angka(total['Rusak Ringan'])}")
    print(f"Rusak Sedang : {format_angka(total['Rusak Sedang'])}")
    print(f"Rusak Berat  : {format_angka(total['Rusak Berat'])}")

    print("\nINPUT ESTIMASI BIAYA PERBAIKAN")
    biaya_ringan = input_biaya("Biaya rusak ringan per ruang : Rp ")
    biaya_sedang = input_biaya("Biaya rusak sedang per ruang : Rp ")
    biaya_berat = input_biaya("Biaya rusak berat per ruang  : Rp ")

    rincian = [
        ("Rusak Ringan", total["Rusak Ringan"], biaya_ringan),
        ("Rusak Sedang", total["Rusak Sedang"], biaya_sedang),
        ("Rusak Berat", total["Rusak Berat"], biaya_berat),]

    total_anggaran = sum(jumlah * biaya for _, jumlah, biaya in rincian)

    print("\nRINCIAN ESTIMASI ANGGARAN")
    print(f"{'Kategori':20} | {'Jumlah Ruang':15} | {'Biaya per Ruang':20} | {'Total Biaya':20}")
    print("-" * 85)

    for kategori, jumlah, biaya in rincian:
        subtotal = jumlah * biaya
        print(f"{kategori:20} | {format_angka(jumlah):>15} | {format_rupiah(biaya):>20} | {format_rupiah(subtotal):>20}")

    print(f"\nTOTAL ESTIMASI ANGGARAN: {format_rupiah(total_anggaran)}")

def menu_utama(data):
    while True:
        print("\nSISTEM ANALISIS KONDISI RUANG KELAS")
        print("1. Menu Peringatan Kerusakan")
        print("2. Menu Perbandingan 2 Provinsi")
        print("3. Menu Anggaran Biaya")
        print("4. Keluar")

        pilihan = input("\nPilih menu (1-4): ").strip()

        if pilihan == "1":
            menu_peringatan(data)
        elif pilihan == "2":
            menu_perbandingan(data)
        elif pilihan == "3":
            menu_anggaran(data)
        elif pilihan == "4":
            print("\nTerima kasih telah menggunakan program.")
            break
        else:
            print("\nPilihan menu tidak valid.")
            print("Silakan pilih menu 1 sampai 4.")

def main():
    print("PROGRAM ANALISIS KONDISI RUANG KELAS SD/MI")
    if login():
        data = baca_dataset()
        if data is not None:
            menu_utama(data)

if __name__ == "__main__":
    main()