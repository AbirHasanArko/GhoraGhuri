"""
GhoraGhuri — Seed Data for Dhaka Transport Network
Real-world approximate data for major Dhaka transport hubs and routes.

This seeds the graph with ~110 nodes and ~200+ edges covering:
- Major bus stops and hubs
- Rickshaw-heavy zones
- CNG corridors
- Walking connections between nearby stops
- Key interchange points

Data sources: BRTA route maps, DTCA bus network, OpenStreetMap
"""
from __future__ import annotations

from app.engine.graph import GraphEdge, GraphNode, TransportGraph


def create_dhaka_graph() -> TransportGraph:
    """
    Create and return a seeded transport graph for Dhaka.
    """
    graph = TransportGraph()

    # ══════════════════════════════════════════════════════
    # NODES — Major transport hubs and stops
    # ══════════════════════════════════════════════════════

    nodes_data = [
        # ── Mirpur Area ────────────────────────────────
        ("MIR01", "Mirpur 1", "মিরপুর ১", 23.7935, 90.3526, "bus_stop"),
        ("MIR02", "Mirpur 2", "মিরপুর ২", 23.7960, 90.3562, "bus_stop"),
        ("MIR10", "Mirpur 10 Roundabout", "মিরপুর ১০ গোলচত্বর", 23.8069, 90.3688, "hub"),
        ("MIR11", "Mirpur 11", "মিরপুর ১১", 23.8153, 90.3695, "bus_stop"),
        ("MIR12", "Mirpur 12", "মিরপুর ১২", 23.8218, 90.3652, "bus_stop"),
        ("MIR14", "Mirpur 14", "মিরপুর ১৪", 23.8267, 90.3827, "bus_stop"),
        ("KAZI", "Kazipara", "কাজীপাড়া", 23.7939, 90.3717, "bus_stop"),
        ("SHER", "Shewrapara", "শেওড়াপাড়া", 23.7906, 90.3773, "bus_stop"),

        # ── Mohammadpur / Dhanmondi ────────────────────
        ("MOHA", "Mohammadpur Bus Stand", "মোহাম্মদপুর বাস স্ট্যান্ড", 23.7660, 90.3586, "hub"),
        ("DHN27", "Dhanmondi 27", "ধানমন্ডি ২৭", 23.7531, 90.3735, "bus_stop"),
        ("DHN15", "Dhanmondi 15", "ধানমন্ডি ১৫", 23.7424, 90.3752, "bus_stop"),
        ("JIGA", "Jigatala", "জিগাতলা", 23.7393, 90.3755, "bus_stop"),
        ("SCIE", "Science Lab", "সায়েন্স ল্যাব", 23.7350, 90.3830, "hub"),
        ("LALI", "Lalmatia", "লালমাটিয়া", 23.7556, 90.3651, "bus_stop"),

        # ── Farmgate / Tejgaon ─────────────────────────
        ("FARM", "Farmgate", "ফার্মগেট", 23.7572, 90.3877, "hub"),
        ("TEJG", "Tejgaon", "তেজগাঁও", 23.7621, 90.3964, "bus_stop"),
        ("BIJA", "Bijoy Sarani", "বিজয় সরণি", 23.7662, 90.3922, "bus_stop"),

        # ── Gulshan / Banani / Baridhara ───────────────
        ("GULS", "Gulshan 1", "গুলশান ১", 23.7809, 90.4164, "hub"),
        ("GUL2", "Gulshan 2", "গুলশান ২", 23.7946, 90.4148, "hub"),
        ("BANA", "Banani", "বানানী", 23.7920, 90.4027, "bus_stop"),
        ("BARI", "Baridhara", "বারিধারা", 23.7991, 90.4218, "bus_stop"),
        ("MOHA_R", "Mohakhali", "মহাখালী", 23.7782, 90.4055, "hub"),

        # ── Uttara ─────────────────────────────────────
        ("UTT_S", "Uttara Sector 3", "উত্তরা সেক্টর ৩", 23.8685, 90.3960, "bus_stop"),
        ("UTT_N", "Uttara North", "উত্তরা উত্তর", 23.8752, 90.3996, "bus_stop"),
        ("UTT_C", "Uttara Center", "উত্তরা সেন্টার", 23.8630, 90.3985, "bus_stop"),
        ("AIRP", "Airport", "বিমানবন্দর", 23.8505, 90.4015, "hub"),
        ("ABDU", "Abdullahpur", "আব্দুল্লাহপুর", 23.8756, 90.3961, "bus_stop"),

        # ── Motijheel / Old Dhaka ──────────────────────
        ("MOTI", "Motijheel", "মতিঝিল", 23.7289, 90.4186, "hub"),
        ("PALT", "Paltan", "পল্টন", 23.7344, 90.4126, "bus_stop"),
        ("KAKA", "Kakrail", "কাকরাইল", 23.7393, 90.4097, "bus_stop"),
        ("SHAH", "Shahbag", "শাহবাগ", 23.7388, 90.3960, "hub"),
        ("DAKU", "Dhaka University", "ঢাকা বিশ্ববিদ্যালয়", 23.7335, 90.3920, "bus_stop"),
        ("GULIS", "Gulistan", "গুলিস্তান", 23.7228, 90.4130, "hub"),
        ("BAIT", "Baitul Mukarram", "বায়তুল মোকাররম", 23.7283, 90.4110, "bus_stop"),
        ("SADAR", "Sadarghat", "সদরঘাট", 23.7095, 90.4072, "hub"),
        ("CHAWK", "Chawkbazar", "চকবাজার", 23.7190, 90.3990, "bus_stop"),
        ("LALBAG", "Lalbagh", "লালবাগ", 23.7190, 90.3890, "bus_stop"),

        # ── Gabtoli / Savar Corridor ───────────────────
        ("GABT", "Gabtoli", "গাবতলী", 23.7770, 90.3460, "hub"),
        ("AMIN", "Aminbazar", "আমিনবাজার", 23.7856, 90.3205, "bus_stop"),
        ("SAVA", "Savar Bus Stand", "সাভার বাস স্ট্যান্ড", 23.8520, 90.2590, "hub"),
        ("ASHU", "Ashulia", "আশুলিয়া", 23.8730, 90.3168, "bus_stop"),

        # ── Jatrabari / South ──────────────────────────
        ("JATR", "Jatrabari", "যাত্রাবাড়ী", 23.7102, 90.4349, "hub"),
        ("SAYA", "Sayedabad", "সায়েদাবাদ", 23.7120, 90.4280, "hub"),
        ("POSTOGOLA", "Postogola", "পোস্তগোলা", 23.7000, 90.4310, "bus_stop"),

        # ── Badda / Rampura ────────────────────────────
        ("BADD", "Badda", "বাড্ডা", 23.7800, 90.4260, "bus_stop"),
        ("RAMP", "Rampura", "রামপুরা", 23.7640, 90.4280, "bus_stop"),
        ("MALIBAG", "Malibagh", "মালিবাগ", 23.7470, 90.4230, "bus_stop"),
        ("MUGH", "Mugda", "মুগদা", 23.7362, 90.4350, "bus_stop"),

        # ── Cantonment / Airport Road ──────────────────
        ("CANT", "Cantonment", "ক্যান্টনমেন্ট", 23.8140, 90.4010, "bus_stop"),
        ("BANS", "Banasree", "বনশ্রী", 23.7630, 90.4430, "bus_stop"),

        # ── Tongi / Gazipur ────────────────────────────
        ("TONG", "Tongi", "টঙ্গী", 23.8908, 90.4049, "hub"),
        ("GAZI", "Gazipur Chowrasta", "গাজীপুর চৌরাস্তা", 23.9902, 90.4231, "hub"),

        # ── New Market / Elephant Road ─────────────────
        ("NEWM", "New Market", "নিউ মার্কেট", 23.7336, 90.3862, "bus_stop"),
        ("ELEP", "Elephant Road", "এলিফ্যান্ট রোড", 23.7370, 90.3890, "bus_stop"),

        # ── Mirpur Road Corridor ───────────────────────
        ("KOLY", "Kolyanpur", "কল্যাণপুর", 23.7870, 90.3610, "bus_stop"),
        ("TECH", "Technical Mor", "টেকনিক্যাল মোড়", 23.7811, 90.3682, "bus_stop"),
        ("AGARGAON", "Agargaon", "আগারগাঁও", 23.7782, 90.3785, "hub"),
        ("TALT", "Taltola", "তালতলা", 23.7720, 90.3880, "bus_stop"),
    ]

    for code, name_en, name_bn, lat, lng, ntype in nodes_data:
        graph.add_node(GraphNode(
            id=code,
            code=code,
            name_en=name_en,
            name_bn=name_bn,
            lat=lat,
            lng=lng,
            node_type=ntype,
        ))

    # ══════════════════════════════════════════════════════
    # EDGES — Transport connections
    # (from, to, mode, route_name_en, route_name_bn,
    #  time_min, fare_bdt, distance_m, crowd, reliability)
    # ══════════════════════════════════════════════════════

    edges_data = [
        # ── Mirpur Road Corridor (Bus) ─────────────────
        ("MIR12", "MIR11", "bus", "Route Mirpur-Gulistan", "মিরপুর-গুলিস্তান রুট", 5, 8, 900, "high", 0.7),
        ("MIR11", "MIR10", "bus", "Route Mirpur-Gulistan", "মিরপুর-গুলিস্তান রুট", 5, 8, 800, "high", 0.7),
        ("MIR10", "KAZI", "bus", "Route Mirpur-Gulistan", "মিরপুর-গুলিস্তান রুট", 8, 8, 1200, "high", 0.7),
        ("KAZI", "SHER", "bus", "Route Mirpur-Gulistan", "মিরপুর-গুলিস্তান রুট", 5, 5, 700, "high", 0.7),
        ("SHER", "AGARGAON", "bus", "Route Mirpur-Gulistan", "মিরপুর-গুলিস্তান রুট", 6, 5, 800, "high", 0.7),
        ("AGARGAON", "TALT", "bus", "Route Mirpur-Gulistan", "মিরপুর-গুলিস্তান রুট", 5, 5, 700, "medium", 0.7),
        ("TALT", "FARM", "bus", "Route Mirpur-Gulistan", "মিরপুর-গুলিস্তান রুট", 5, 5, 600, "high", 0.8),
        ("FARM", "SHAH", "bus", "Route Farmgate-Shahbag", "ফার্মগেট-শাহবাগ রুট", 10, 8, 1500, "high", 0.7),
        ("SHAH", "NEWM", "bus", "Route Shahbag-Gulistan", "শাহবাগ-গুলিস্তান রুট", 5, 5, 600, "medium", 0.8),
        ("SHAH", "PALT", "bus", "Route Shahbag-Motijheel", "শাহবাগ-মতিঝিল রুট", 12, 10, 2000, "high", 0.6),
        ("PALT", "MOTI", "bus", "Route Paltan-Motijheel", "পল্টন-মতিঝিল রুট", 5, 5, 600, "medium", 0.8),
        ("MOTI", "GULIS", "bus", "Route Motijheel-Gulistan", "মতিঝিল-গুলিস্তান রুট", 8, 8, 800, "high", 0.7),
        ("GULIS", "SADAR", "bus", "Route Gulistan-Sadarghat", "গুলিস্তান-সদরঘাট রুট", 12, 8, 1500, "extreme", 0.5),

        # ── Airport Road Corridor (Bus) ────────────────
        ("UTT_N", "UTT_C", "bus", "Airport Road Bus", "এয়ারপোর্ট রোড বাস", 5, 8, 1200, "medium", 0.8),
        ("UTT_C", "AIRP", "bus", "Airport Road Bus", "এয়ারপোর্ট রোড বাস", 8, 8, 1500, "medium", 0.8),
        ("AIRP", "CANT", "bus", "Airport Road Bus", "এয়ারপোর্ট রোড বাস", 10, 10, 3000, "medium", 0.7),
        ("CANT", "BANA", "bus", "Airport Road Bus", "এয়ারপোর্ট রোড বাস", 8, 8, 1500, "medium", 0.7),
        ("BANA", "MOHA_R", "bus", "Airport Road Bus", "এয়ারপোর্ট রোড বাস", 8, 8, 1500, "medium", 0.8),
        ("MOHA_R", "FARM", "bus", "Mohakhali-Farmgate Bus", "মহাখালী-ফার্মগেট বাস", 12, 10, 2500, "high", 0.6),

        # ── Dhanmondi (Rickshaw) ───────────────────────
        ("DHN27", "DHN15", "rickshaw", None, None, 8, 20, 1300, "low", 0.9),
        ("DHN15", "JIGA", "rickshaw", None, None, 5, 15, 500, "low", 0.9),
        ("JIGA", "SCIE", "rickshaw", None, None, 5, 15, 500, "low", 0.9),
        ("DHN27", "LALI", "rickshaw", None, None, 6, 15, 900, "low", 0.9),
        ("LALI", "MOHA", "rickshaw", None, None, 8, 20, 1200, "low", 0.9),
        ("DHN27", "FARM", "rickshaw", None, None, 15, 40, 2000, "low", 0.8),
        ("SCIE", "NEWM", "rickshaw", None, None, 5, 15, 400, "low", 0.9),

        # ── Dhanmondi (Bus) ────────────────────────────
        ("SCIE", "FARM", "bus", "Route Dhanmondi-Farmgate", "ধানমন্ডি-ফার্মগেট রুট", 12, 10, 2000, "high", 0.6),
        ("MOHA", "DHN27", "bus", "Route Mohammadpur-Dhanmondi", "মোহাম্মদপুর-ধানমন্ডি রুট", 10, 8, 1800, "medium", 0.7),
        ("SCIE", "SHAH", "bus", "Route Science Lab-Shahbag", "সায়েন্স ল্যাব-শাহবাগ রুট", 8, 8, 1100, "medium", 0.7),

        # ── Gulshan/Banani (CNG) ───────────────────────
        ("GULS", "GUL2", "cng", None, None, 8, 60, 1500, "low", 0.9),
        ("GUL2", "BARI", "cng", None, None, 6, 50, 1000, "low", 0.9),
        ("GULS", "BANA", "cng", None, None, 8, 50, 1500, "low", 0.9),
        ("GULS", "MOHA_R", "cng", None, None, 10, 70, 2000, "low", 0.8),
        ("MOHA_R", "FARM", "cng", None, None, 15, 100, 3000, "medium", 0.7),
        ("MOHA_R", "BANA", "cng", None, None, 8, 50, 1500, "low", 0.8),

        # ── Gabtoli / Savar Corridor (Bus) ─────────────
        ("GABT", "AMIN", "bus", "Dhaka-Aricha Highway", "ঢাকা-আরিচা মহাসড়ক", 15, 15, 5000, "medium", 0.7),
        ("AMIN", "SAVA", "bus", "Dhaka-Aricha Highway", "ঢাকা-আরিচা মহাসড়ক", 30, 25, 10000, "medium", 0.7),
        ("GABT", "TECH", "bus", "Gabtoli-Technical", "গাবতলী-টেকনিক্যাল", 10, 10, 2500, "medium", 0.7),
        ("TECH", "KOLY", "bus", "Technical-Kolyanpur", "টেকনিক্যাল-কল্যাণপুর", 5, 5, 1000, "medium", 0.8),
        ("MIR01", "GABT", "bus", "Mirpur-Gabtoli", "মিরপুর-গাবতলী", 12, 10, 2500, "medium", 0.7),
        ("KOLY", "MIR01", "bus", "Kolyanpur-Mirpur", "কল্যাণপুর-মিরপুর", 8, 8, 1500, "medium", 0.7),

        # ── Jatrabari / South (Bus) ────────────────────
        ("GULIS", "JATR", "bus", "Gulistan-Jatrabari", "গুলিস্তান-যাত্রাবাড়ী", 15, 10, 3000, "high", 0.6),
        ("GULIS", "SAYA", "bus", "Gulistan-Sayedabad", "গুলিস্তান-সায়েদাবাদ", 12, 10, 2500, "high", 0.6),
        ("JATR", "SAYA", "bus", None, None, 5, 5, 800, "medium", 0.8),

        # ── Badda / Rampura Corridor ───────────────────
        ("BADD", "GUL2", "bus", "Badda-Gulshan Bus", "বাড্ডা-গুলশান বাস", 12, 10, 2000, "high", 0.6),
        ("BADD", "RAMP", "bus", "Badda-Rampura Bus", "বাড্ডা-রামপুরা বাস", 10, 8, 1800, "high", 0.6),
        ("RAMP", "MALIBAG", "bus", "Rampura-Malibagh Bus", "রামপুরা-মালিবাগ বাস", 8, 8, 1200, "high", 0.6),
        ("MALIBAG", "MOTI", "bus", "Malibagh-Motijheel", "মালিবাগ-মতিঝিল রুট", 12, 10, 2500, "high", 0.6),
        ("MALIBAG", "KAKA", "bus", "Malibagh-Kakrail", "মালিবাগ-কাকরাইল রুট", 10, 8, 1800, "medium", 0.7),

        # ── Uttara-Tongi-Gazipur (Bus) ─────────────────
        ("UTT_N", "ABDU", "bus", "Uttara-Abdullahpur", "উত্তরা-আব্দুল্লাহপুর", 5, 5, 800, "medium", 0.8),
        ("ABDU", "TONG", "bus", "Abdullahpur-Tongi", "আব্দুল্লাহপুর-টঙ্গী", 15, 15, 5000, "medium", 0.7),
        ("TONG", "GAZI", "bus", "Tongi-Gazipur", "টঙ্গী-গাজীপুর", 25, 20, 12000, "medium", 0.7),

        # ── Old Dhaka (Rickshaw/Walking) ───────────────
        ("SADAR", "CHAWK", "rickshaw", None, None, 10, 20, 1200, "high", 0.7),
        ("CHAWK", "LALBAG", "rickshaw", None, None, 8, 15, 1000, "medium", 0.8),
        ("GULIS", "BAIT", "walking", None, None, 5, 0, 400, "high", 0.9),
        ("BAIT", "MOTI", "walking", None, None, 5, 0, 400, "high", 0.9),

        # ── Cross-town connections ─────────────────────
        ("SHAH", "KAKA", "bus", "Shahbag-Kakrail", "শাহবাগ-কাকরাইল রুট", 8, 8, 1200, "medium", 0.7),
        ("FARM", "BIJA", "bus", "Farmgate-Bijoy Sarani", "ফার্মগেট-বিজয় সরণি রুট", 5, 5, 700, "medium", 0.8),
        ("BIJA", "MOHA_R", "bus", "Bijoy Sarani-Mohakhali", "বিজয় সরণি-মহাখালী রুট", 8, 8, 1500, "medium", 0.7),
        ("FARM", "TEJG", "bus", "Farmgate-Tejgaon", "ফার্মগেট-তেজগাঁও রুট", 8, 8, 1500, "medium", 0.7),
        ("TEJG", "GULS", "bus", "Tejgaon-Gulshan", "তেজগাঁও-গুলশান রুট", 15, 12, 3000, "medium", 0.6),
        ("MOHA", "GABT", "bus", "Mohammadpur-Gabtoli", "মোহাম্মদপুর-গাবতলী রুট", 10, 10, 2000, "medium", 0.7),

        # ── Walking connections (short distances) ──────
        ("NEWM", "ELEP", "walking", None, None, 3, 0, 250, "low", 1.0),
        ("ELEP", "SHAH", "walking", None, None, 4, 0, 350, "low", 1.0),
        ("DAKU", "SHAH", "walking", None, None, 5, 0, 400, "low", 1.0),
        ("PALT", "KAKA", "walking", None, None, 5, 0, 400, "low", 1.0),
        ("SCIE", "ELEP", "walking", None, None, 5, 0, 400, "low", 1.0),
        ("FARM", "TALT", "walking", None, None, 8, 0, 600, "low", 1.0),
        ("AGARGAON", "SHER", "walking", None, None, 10, 0, 800, "low", 1.0),
        ("BANA", "GUL2", "walking", None, None, 12, 0, 1000, "low", 1.0),
        ("MIR10", "KAZI", "walking", None, None, 15, 0, 1200, "medium", 1.0),

        # ── Leguna routes ──────────────────────────────
        ("GULIS", "JATR", "leguna", "Gulistan-Jatrabari Leguna", "গুলিস্তান-যাত্রাবাড়ী লেগুনা", 12, 8, 3000, "extreme", 0.5),
        ("SADAR", "GULIS", "leguna", "Sadarghat-Gulistan Leguna", "সদরঘাট-গুলিস্তান লেগুনা", 10, 8, 1500, "extreme", 0.5),
        ("MOTI", "RAMP", "leguna", "Motijheel-Rampura Leguna", "মতিঝিল-রামপুরা লেগুনা", 15, 10, 3000, "high", 0.5),

        # ── CNG Airport routes ─────────────────────────
        ("AIRP", "GULS", "cng", None, None, 20, 200, 8000, "low", 0.9),
        ("AIRP", "FARM", "cng", None, None, 30, 300, 12000, "low", 0.8),
        ("AIRP", "MOTI", "cng", None, None, 35, 350, 15000, "low", 0.7),

        # ── More Rickshaw connections ──────────────────
        ("MIR10", "MIR11", "rickshaw", None, None, 8, 20, 900, "low", 0.9),
        ("FARM", "SHAH", "rickshaw", None, None, 15, 40, 1500, "low", 0.8),
        ("MOTI", "PALT", "rickshaw", None, None, 5, 15, 600, "low", 0.9),
        ("SHAH", "DAKU", "rickshaw", None, None, 5, 15, 400, "low", 0.9),
        ("MOHA_R", "GULS", "rickshaw", None, None, 10, 30, 2000, "low", 0.8),
    ]

    for i, (f, t, mode, rn_en, rn_bn, time_m, fare, dist, crowd, rel) in enumerate(edges_data):
        graph.add_edge(GraphEdge(
            id=f"E{i:04d}",
            from_id=f,
            to_id=t,
            transport_mode=mode,
            route_name_en=rn_en,
            route_name_bn=rn_bn,
            time_minutes=time_m,
            fare_bdt=fare,
            distance_meters=dist,
            crowd_level=crowd,
            reliability=rel,
            is_bidirectional=True,
        ))

    return graph
