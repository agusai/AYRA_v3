import random
from datetime import datetime

def get_tips_jiji():
    """Return random tip for today (surprise Uncle Jiji style)"""
    
    # List of tips - boleh tambah banyak lagi
    tips = [
        # Resepi
        ("🍳 Resepi Nasi Lemak Simple", 
         "- Nasi: 2 cawan beras, 1 inci halia\n- Santan: 1 cawan santan pekat\n- Masak macam biasa, tambah daun pandan"),
        
        ("🍜 Maggi Goreng Mamak Style",
         "- 2 keping maggi, rebus & toskan\n- Tumis bawang, cili, ikan bilis\n- Masukkan maggi, kicap manis, sos tiram"),
        
        # Petua
        ("🏠 Hilangkan Bau Peti Sejuk",
         "Letak semangkuk kecil serbuk kopi. Biarkan semalaman – esok bau hilang! ✨"),
        
        # Teka-teki
        ("🧩 Teka-Teki Uncle Jiji",
         "Apa dia, makin banyak kau ambil, makin besar?\n\n(Jawapan: Lubang! 😄)"),
        
        # Tip bisnes
        ("💼 Tip Bisnes Minggu Ini",
         "Guna FOMO: 'Stok terhad', 'Sale tamat esok' – pembeli akan cepat buat keputusan."),
        
        # Quote
        ("🌟 Quote Semangat",
         "Jangan bandingkan Chapter 1 kau dengan Chapter 20 orang lain."),
    ]
    
    # Seed based on date so same tip all day
    today = datetime.now().strftime("%Y%m%d")
    random.seed(int(today))
    
    return random.choice(tips)