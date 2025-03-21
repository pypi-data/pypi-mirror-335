import re

def hapus_duplikasi_kalimat(teks : str) -> str:
    """
        Menghapus kalimat yang duplikat dalam teks.

        Args : 
            teks (str) : teks yang akan diproses

        Returns : 
            str : Teks hasil dengan kalimat unik
    """

    if not teks:
        return teks
    
    kalimat_list = re.split(r'[.!?]', teks)
    kalimat_list = [k.strip() for k in kalimat_list if k.strip()]

    unik = []
    sudah_ada = set()

    for kalimat in kalimat_list:
        if kalimat not in sudah_ada:
            unik.append(kalimat)
            sudah_ada.add(kalimat)

    return '.'.join(unik) + '.'