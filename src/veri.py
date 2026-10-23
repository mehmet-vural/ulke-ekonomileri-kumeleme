"""Dünya Bankası göstergelerini ülke bazında çeker; 2019–2023 ortalamasını alır.

Kaynak: World Bank, World Development Indicators (CC BY 4.0).
"""

from pathlib import Path

import pandas as pd
import requests

VERI = Path(__file__).resolve().parent.parent / "veri" / "gostergeler.csv"
API = "https://api.worldbank.org/v2"
DONEM = "2019:2023"

GOSTERGELER = {
    "NY.GDP.PCAP.PP.KD": "kisi_basi_gelir",     # kişi başı GSYH, satın alma gücü paritesi (sabit $)
    "NY.GDP.MKTP.KD.ZG": "buyume",              # reel GSYH büyümesi (%)
    "FP.CPI.TOTL.ZG": "enflasyon",              # TÜFE enflasyonu (%)
    "SL.UEM.TOTL.ZS": "issizlik",               # işsizlik (% işgücü, ILO)
    "NE.TRD.GNFS.ZS": "dis_ticaret",            # dış ticaret / GSYH (%)
    "BN.CAB.XOKA.GD.ZS": "cari_denge",          # cari denge / GSYH (%)
    "NE.GDI.TOTL.ZS": "yatirim",                # brüt sermaye oluşumu / GSYH (%)
    "SP.DYN.LE00.IN": "yasam_suresi",           # doğumda beklenen yaşam süresi (yıl)
    "SP.POP.TOTL": "nufus",
}


def _getir(yol: str, **parametre) -> list:
    r = requests.get(f"{API}/{yol}", params={"format": "json", "per_page": 20000, **parametre}, timeout=90)
    return r.json()[1]


def cek() -> pd.DataFrame:
    ulkeler = {u["id"]: u["name"] for u in _getir("country") if u["region"]["id"] != "NA"}
    sutunlar = {}
    for kod, ad in GOSTERGELER.items():
        kayit = _getir(f"country/all/indicator/{kod}", date=DONEM)
        d = pd.DataFrame({"ulke": k["countryiso3code"], "deger": k["value"]} for k in kayit
                         if k["countryiso3code"] in ulkeler and k["value"] is not None)
        sutunlar[ad] = d.groupby("ulke").deger.mean()
    df = pd.DataFrame(sutunlar)
    df.insert(0, "ad", pd.Series(ulkeler))
    return df.dropna(subset=["ad"])


def yukle(yenile: bool = False) -> pd.DataFrame:
    if yenile or not VERI.exists():
        VERI.parent.mkdir(exist_ok=True)
        cek().round(4).to_csv(VERI, index_label="kod")
    return pd.read_csv(VERI, index_col="kod")


if __name__ == "__main__":
    d = yukle(yenile=True)
    print(d.shape, d.dropna().shape)
    print(d.loc["TUR"])
