# 📖 mydeen

**mydeen** est un package Python qui, par la permission d’Allah ﷻ, vise à faciliter l’accès aux ressources islamiques (Coran, chaînes YouTube éducatives) pour la communauté francophone.

---

## ✨ Fonctionnalités

- 📚 Accès aux données du Coran (sourates, versets, métadonnées…)
- 📺 Intégration avec l’API YouTube pour récupérer :
  - les identifiants de chaînes à partir de leur handle
  - les playlists d’une chaîne
  - les vidéos d’une playlist
- 🔎 Filtrage et recherche de sourates ou versets spécifiques
- 🧠 Typages stricts et code Python bien structuré

---

## 🔧 Installation

```bash
pip install mydeen
```

> ⚠️ Python 3.9 ou supérieur est requis

---

## 🧪 Exemple d'utilisation

```python
from mydeen import MyDeen, Config

mydeen = MyDeen(path_database="./database")

# Récupérer toutes les sourates
sourates = mydeen.meta_surah.get_all()

# Obtenir les playlists d’une chaîne YouTube
from mydeen.yt_services import YoutubeServices
yt = YoutubeServices(api_key="VOTRE_CLE_API")
playlists = yt.get_playlist(yt.channels.lecoransimplement)
```

---

## 📁 Structure du package

```
mydeen/
├── config.py
├── exception_error.py
├── interface.py
├── mydeen.py
├── parser_meta_surahs.py
├── yt_services.py
└── ...
```

---

## 🤝 Contribuer

Toute contribution utile est la bienvenue, qu’il s’agisse de correction, documentation ou nouvelles fonctionnalités.

---

## 📜 Licence

Ce projet est sous licence **MIT** — Faites-en bon usage et avec sincérité.

---

## 🕋 Intention

> _"Les actions ne valent que par les intentions."_  
> — Hadith authentique (rapporté par Al-Bukhari & Muslim)

Ce projet a été initié dans le but de propager la science bénéfique et l'amour du Coran. Qu’Allah accepte 🌙

---

## 🧑 Auteur

Développé avec foi par **YassinePaquitoNobody**  
📧 Contact : monsieurnobody01@gmail.com  
🔗 [Mon GitHub](https://github.com/YassineNobody)
