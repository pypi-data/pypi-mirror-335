import unittest
from textstat_id.convert_word_to_number import konversi_angka_ke_teks

class TestConvertWordToNumber(unittest.TestCase):
    
    def test_nol(self):
        self.assertEqual(konversi_angka_ke_teks(0), "nol")
    
    def test_sebelas(self):
        self.assertEqual(konversi_angka_ke_teks(11), "sebelas")
    
    def test_lima_belas(self):
        self.assertEqual(konversi_angka_ke_teks(15), "lima belas")
    
    def test_seratus(self):
        self.assertEqual(konversi_angka_ke_teks(100), "seratus")
    
    def test_seratus_satu(self):
        self.assertEqual(konversi_angka_ke_teks(101), "seratus satu")
    
    def test_2023(self):
        # Harapan: "dua ribu dua puluh tiga"
        self.assertEqual(konversi_angka_ke_teks(2023), "dua ribu dua puluh tiga")
    
    def test_ratusan(self):
        # Contoh angka di tengah ribuan
        self.assertEqual(konversi_angka_ke_teks(850), "delapan ratus lima puluh")

if __name__ == '__main__':
    unittest.main()