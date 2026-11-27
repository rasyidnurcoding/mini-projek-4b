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
                            raise  ValueError("Provinsi atau Kota/Kab kosong")

                        if row["Status Sekolah"].strip() not in ["Negeri dan Swasta", "Negeri", "Swasta"]:
                            continue

                        baik         = konversi_angka(row["Baik"])
                        rusak_ringan = konversi_angka(row["Rusak Ringan"])
                        rusak_sedang = konversi_angka(row["Rusak Sedang"])
                        rusak_berat  = konversi_angka(row["Rusak Berat"])
                        jumlah       = konversi_angka(row["Jumlah"])

                        if min(baik, rusak_ringan, rusak_sedang, rusak_berat, jumlah) < 0:
                            raise ValueError("Terdapat nilai negatif pada data ruang kelas")

                        total_rusak = rusak_ringan + rusak_sedang + rusak_berat
                        persen_rusak = (total_rusak / jumlah) * 100 if jumlah > 0 else 0.0

                        row["Baik"]             = baik
                        row["Rusak Ringan"]     = rusak_ringan
                        row["Rusak Sedang"]     = rusak_sedang
                        row["Rusak Berat"]      = rusak_berat
                        row["Jumlah"]           = jumlah
                        row["Status_Kerusakan"] = klasifikasi_kerusakan(total_rusak, jumlah)
                        row["Persen_Rusak"]     = persen_rusak  

                        data.append(row)

                    except(ValueError):
                        jumlah_error += 1
                        continue

                if len(data) == 0:
                    print("\nERROR: Dataset kosong atau tidak memiliki data valid.")
                else:
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
    elif "." in teks:
        teks = teks.replace(".", "")
    return float(teks)

def klasifikasi_kerusakan(total_rusak, jumlah_kelas):
    if jumlah_kelas <= 0 or total_rusak <= 0:
        return "Aman"

    persen_rusak = (total_rusak / jumlah_kelas) * 100
    if persen_rusak > 25:
        return "Kritis"
    elif persen_rusak > 10:
        return "Perlu Perhatian"
    else:
        return "Ringan"

def format_angka(nilai):
    return f"{nilai:,.0f}"

def login():
    pengguna = {"1": "Mahasiswa", "2": "Dosen", "3": "Masyarakat Umum"}

    print("\nPILIH PENGGUNA")
    for kode, nama_pengguna in pengguna.items():
        print(f"{kode}. {nama_pengguna}")

    while True:
        pilihan = input("Masuk sebagai (1-3): ").strip()
        if pilihan in pengguna:
            print(f"\nBerhasil masuk sebagai {pengguna[pilihan]}. Selamat datang!\n")
            return pengguna[pilihan]
        print("\nPilihan tidak valid. Silakan pilih 1, 2, atau 3.\n")

def daftar_provinsi(data):
    daftar = []
    daftar_kunci = []

    for row in data:
        key = row["Provinsi"].strip().lower()
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
        "Jumlah": 0.0,}

    for row in data_provinsi:
        for kolom in total:
            total[kolom] += row[kolom]

    return total

def tampilkan_total(nama_provinsi, total):
    total_rusak = total["Rusak Ringan"] + total["Rusak Sedang"] + total["Rusak Berat"]
    status      = klasifikasi_kerusakan(total_rusak, total["Jumlah"])

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
    print(f"{'Kab/Kota':30} | {'Ringan':10} | {'Sedang':10} | {'Berat':10} | {'% Rusak':10} | {'Status':16}")
    print("-" * 102)

    jumlah_wilayah_rusak = 0

    for row in data_provinsi:
        total_rusak = row["Rusak Ringan"] + row["Rusak Sedang"] + row["Rusak Berat"]
        if total_rusak > 0:
            jumlah_wilayah_rusak += 1
            print(f"{row['Kota/Kab']:30} | {format_angka(row['Rusak Ringan']):>10} | {format_angka(row['Rusak Sedang']):>10} | {format_angka(row['Rusak Berat']):>10} | {row['Persen_Rusak']:9.2f}% | {row['Status_Kerusakan']:16}")

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

def menu_rangking_provinsi(data):
    opsi_kondisi = {
        "1": "Baik",
        "2": "Rusak Ringan",
        "3": "Rusak Sedang",
        "4": "Rusak Berat",}

    while True:
        print("\nMENU RANGKING KONDISI RUANG KELAS PER PROVINSI")
        print("1. Baik")
        print("2. Rusak Ringan")
        print("3. Rusak Sedang")
        print("4. Rusak Berat")
        print("5. Kembali ke Menu Utama")

        pilihan = input("\nPilih kondisi ruang kelas (1-5): ").strip()

        if pilihan == "5":
            break
        if pilihan not in opsi_kondisi:
            print("\nPilihan tidak valid. Silakan pilih 1 sampai 5.")
            continue

        kolom_kondisi = opsi_kondisi[pilihan]
        rekapan = []

        for key_prov, nama_prov in daftar_provinsi(data):
            data_prov = cari_data_provinsi(data, key_prov)
            total = hitung_total(data_prov)
            rekapan.append((nama_prov, total[kolom_kondisi], total["Jumlah"]))

        for i in range(len(rekapan)):
            for j in range(i + 1, len(rekapan)):
                if rekapan[i][1] < rekapan[j][1]:
                    sementara  = rekapan[i]
                    rekapan[i] = rekapan[j]
                    rekapan[j] = sementara

        print(f"\nRANGKING PROVINSI BERDASARKAN KONDISI: {kolom_kondisi.upper()}")
        print(f"{'Rank':4} | {'Provinsi':31} | {'kolom_kondisi':15} | {'Total_Kelas':15}")
        print("-" * 73)

        for peringkat, (nama_prov, nilai_kondisi, total_kelas) in enumerate(rekapan, start=1):
            print(f"{peringkat:4} | {nama_prov:31} | {format_angka(nilai_kondisi):>15} | {format_angka(total_kelas):>15}")

def menu_rekomendasi_solusi(data):
    print("\nMENU REKOMENDASI SOLUSI KONDISI RUANG KELAS")

    key_prov, nama_prov = pilih_provinsi(data, "Pilih nomor provinsi untuk melihat solusi")
    data_provinsi = cari_data_provinsi(data, key_prov)

    if not data_provinsi:
        print("Data provinsi tidak ditemukan.")
        return

    total = hitung_total(data_provinsi)
    tampilkan_total(nama_prov, total)

    total_rusak = total["Rusak Ringan"] + total["Rusak Sedang"] + total["Rusak Berat"]
    status      = klasifikasi_kerusakan(total_rusak, total["Jumlah"])

    print("\nPENJELASAN SOLUSI BERDASARKAN KONDISI RUANG KELAS:")
    print(f"Kondisi Baik ({format_angka(total['Baik'])}):\nPemeliharaan rutin dan berkala untuk mempertahankan kualitas dan kelayakan bangunan ruang kelas.\n")
    print(f"Kondisi Rusak Ringan ({format_angka(total['Rusak Ringan'])}):\nPerbaikan setempat, seperti penambalan plesteran dinding yang retak atau mengelupas, pengecatan ulang, dan perbaikan komponen kecil.\n")
    print(f"Kondisi Rusak Sedang ({format_angka(total['Rusak Sedang'])}):\nRehabilitasi komponen bangunan yang rusak, seperti perbaikan atap, plafon, lantai, atau kusen, untuk mengembalikan fungsi dan kualitas fisik ruang kelas.\n")
    print(f"Kondisi Rusak Berat ({format_angka(total['Rusak Berat'])}):\nPemeriksaan teknis menyeluruh, rehabilitasi berat, atau pembangunan kembali komponen dan struktur utama yang rusak demi keselamatan kegiatan belajar.\n")

    print(f"\nPRIORITAS PENANGANAN PROVINSI {nama_prov.upper()} (Status: {status}):")
    if status   == "Kritis":
        print("Tingkat kerusakan tergolong kritis sehingga penanganan darurat keselamatan, evaluasi struktur, dan rehabilitasi berat perlu diprioritaskan.")
    elif status == "Perlu Perhatian":
        print("Tingkat kerusakan perlu perhatian sehingga rehabilitasi kerusakan sedang dan berat perlu dijadwalkan secara terukur.")
    elif status == "Ringan":
        print("Tingkat kerusakan tergolong Ringan sehingga penanganan dapat difokuskan pada perbaikan Ringan dan perawatan rutin.")
    else:
        print("Kondisi ruang kelas tergolong aman sehingga fokus utama adalah pemeliharaan rutin dan pendataan berkala.")

def menu_utama(data):
    while True:
        print("\nSISTEM ANALISIS KONDISI RUANG KELAS")
        print("1. Menu Peringatan Kerusakan")
        print("2. Menu Perbandingan 2 Provinsi")
        print("3. Menu Rangking Kondisi Ruang Kelas per Provinsi")
        print("4. Menu Rekomendasi Solusi Kondisi Ruang Kelas")
        print("5. Keluar")

        pilihan = input("\nPilih menu (1-5): ").strip()

        if pilihan   == "1":
            menu_peringatan(data)
        elif pilihan == "2":
            menu_perbandingan(data)
        elif pilihan == "3":
            menu_rangking_provinsi(data)
        elif pilihan == "4":
            menu_rekomendasi_solusi(data)
        elif pilihan == "5":
            print("\nTerima kasih telah menggunakan program.")
            break
        else:
            print("\nPilihan menu tidak valid.")
            print("Silakan pilih menu 1 sampai 5.")

def main():
    print("PROGRAM ANALISIS KONDISI RUANG KELAS SD/MI")
    if login():
        data = baca_dataset()
        if data is not None:
            menu_utama(data)

if __name__ == "__main__":
    main()