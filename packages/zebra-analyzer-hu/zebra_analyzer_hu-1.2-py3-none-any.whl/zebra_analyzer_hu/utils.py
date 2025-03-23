import re

def sanitize_filename(filename):
    """
    Dosya isimlerinde geçersiz karakterleri alt çizgi ile değiştirir.
    """
    return re.sub(r'[<>:"/\\|?*]', '_', filename)
