import shutil

# Path asal dan tujuan
asal = "C:/Users/Andini/Documents/skincare/data-set"
tujuan = "C:/Users/Andini/skincare/data-set"

try:
    shutil.move(asal, tujuan)
    print(" Folder data-set berhasil dipindahkan!")
except Exception as e:
    print(f" Gagal memindahkan folder: {e}")
