import unittest
from textstat_id.duplication_checker import hapus_duplikasi_kalimat

class TestHapusDuplikasiKalimat(unittest.TestCase):
    def test_teks_kosong(self):
        # Teks kosong harus menghasilkan teks kosong
        self.assertEqual(hapus_duplikasi_kalimat(""), "")
    
    def test_duplikasi_persis(self):
        # Kalimat yang sama persis akan dihapus duplikasinya
        teks = "Ini kalimat pertama. Ini kalimat kedua. Ini kalimat pertama. Ini kalimat kedua."
        hasil = hapus_duplikasi_kalimat(teks)
        # Harapkan dua kalimat unik dengan spasi setelah titik
        self.assertEqual(hasil, "Ini kalimat pertama. Ini kalimat kedua.")
    
    def test_tidak_ada_duplikasi(self):
        # Jika tidak ada duplikasi, output harus tetap dengan spasi setelah titik
        teks = "Kalimat satu. Kalimat dua. Kalimat tiga"
        hasil = hapus_duplikasi_kalimat(teks)
        self.assertEqual(hasil, "Kalimat satu. Kalimat dua. Kalimat tiga.")
    
    def test_penanganan_spasi(self):
        # Uji dengan spasi berlebih dan tanda baca campuran
        teks = "  Kalimat A!  Kalimat B? Kalimat A. Kalimat C.  "
        hasil = hapus_duplikasi_kalimat(teks)
        self.assertEqual(hasil, "Kalimat A. Kalimat B. Kalimat C.")

if __name__ == '__main__':
    unittest.main() 