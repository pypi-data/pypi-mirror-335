def konversi_angka_ke_teks(angka):
    angka_teks = {
        0: "nol", 1: "satu", 2: "dua", 3: "tiga", 4: "empat",
        5: "lima", 6: "enam", 7: "tujuh", 8: "delapan", 9: "sembilan",
        10: "sepuluh", 11: "sebelas"
    }
    
    if angka < 12:
        return angka_teks[angka]
    elif angka < 20:
        return konversi_angka_ke_teks(angka - 10) + " belas"
    elif angka < 100:
        puluh, sisa = divmod(angka, 10)
        hasil = konversi_angka_ke_teks(puluh) + " puluh"
        if sisa:
            hasil += " " + konversi_angka_ke_teks(sisa)
        return hasil
    elif angka < 200:
        return "seratus" + (" " + konversi_angka_ke_teks(angka - 100) if angka > 100 else "")
    elif angka < 1000:
        ratus, sisa = divmod(angka, 100)
        hasil = konversi_angka_ke_teks(ratus) + " ratus"
        if sisa:
            hasil += " " + konversi_angka_ke_teks(sisa)
        return hasil
    elif angka < 2000:
        return "seribu" + (" " + konversi_angka_ke_teks(angka - 1000) if angka > 1000 else "")
    elif angka < 1000000:
        ribu, sisa = divmod(angka, 1000)
        hasil = konversi_angka_ke_teks(ribu) + " ribu"
        if sisa:
            hasil += " " + konversi_angka_ke_teks(sisa)
        return hasil
    elif angka < 1000000000:
        juta, sisa = divmod(angka, 1000000)
        hasil = konversi_angka_ke_teks(juta) + " juta"
        if sisa:
            hasil += " " + konversi_angka_ke_teks(sisa)
        return hasil
    else:
        return str(angka)


# Contoh penggunaan
print(konversi_angka_ke_teks(101241413))  # Output: "dua ribu dua puluh tiga"