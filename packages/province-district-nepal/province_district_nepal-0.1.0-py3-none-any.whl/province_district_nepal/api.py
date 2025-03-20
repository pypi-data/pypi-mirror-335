province_districts = {
    "Koshi Province": [
        "Bhojpur", "Dhankuta", "Ilam", "Jhapa", "Khotang", "Morang",
        "Okhaldhunga", "Panchthar", "Sankhuwasabha", "Solukhumbu",
        "Sunsari", "Taplejung", "Terhathum", "Udayapur"
    ],
    "Madhesh Province": [
        "Saptari", "Siraha", "Dhanusha", "Mahottari", "Sarlahi",
        "Bara", "Parsa", "Rautahat"
    ],
    "Bagmati Province": [
        "Bhaktapur", "Chitwan", "Dhading", "Dolakha", "Kathmandu",
        "Kavrepalanchok", "Lalitpur", "Makwanpur", "Nuwakot",
        "Ramechhap", "Rasuwa", "Sindhuli", "Sindhupalchok"
    ],
    "Gandaki Province": [
        "Baglung", "Gorkha", "Kaski", "Lamjung", "Manang",
        "Mustang", "Myagdi", "Nawalpur", "Parbat", "Syangja", "Tanahun"
    ],
    "Lumbini Province": [
        "Arghakhanchi", "Banke", "Bardiya", "Dang", "Gulmi",
        "Kapilvastu", "Nawalparasi (West)", "Palpa", "Pyuthan",
        "Rolpa", "Rukum (East)", "Rupandehi"
    ],
    "Karnali Province": [
        "Dailekh", "Dolpa", "Humla", "Jajarkot", "Jumla",
        "Kalikot", "Mugu", "Rukum (West)", "Salyan", "Surkhet"
    ],
    "Sudurpashchim Province": [
        "Achham", "Baitadi", "Bajhang", "Bajura", "Dadeldhura",
        "Darchula", "Doti", "Kailali", "Kanchanpur"
    ],
}


def get_districts(province_name):
    """Fetch districts for a given province in Nepal."""
    return province_districts.get(province_name, "Province not found")