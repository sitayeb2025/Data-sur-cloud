#!/usr/bin/env python
"""
INSTRUCTIONS POUR POUSSER LE PROJET VERS GITHUB
================================================
"""

instructions = """
╔════════════════════════════════════════════════════════════════════════════════╗
║                   ✅ PROJET PRÊT POUR GITHUB!                                 ║
╚════════════════════════════════════════════════════════════════════════════════╝


📋 ÉTAPE 1: CRÉER UN REPOSITORY SUR GITHUB
═══════════════════════════════════════════

1. Accédez à: https://github.com/new
2. Remplissez les champs:
   - Repository name: nasa-eonet-analytics (ou votre choix)
   - Description: Global Disasters Analytics Platform
   - Visibility: Public (optionnel)
   - NE cochez PAS "Initialize with README" (on l'a déjà)
   - NE cochez PAS "Add gitignore" (on l'a déjà)
3. Cliquez "Create repository"


📋 ÉTAPE 2: CONNECTER LE REPOSITORY LOCAL À GITHUB
════════════════════════════════════════════════════

Remplacez YOUR_USERNAME et REPO_NAME avec vos valeurs:

Option A - HTTPS (Facile):
───────────────────────────
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main


Option B - SSH (Sécurisé):
──────────────────────────
# D'abord, configurez votre clé SSH:
# https://docs.github.com/en/authentication/connecting-to-github-with-ssh

git remote add origin git@github.com:YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main


📋 ÉTAPE 3: VÉRIFIER LE PUSH
═════════════════════════════

Après le push, vérifiez:
✓ Allez sur votre repository GitHub
✓ Vérifiez que tous les fichiers sont présents:
  - src/, data/, dashboards/
  - README.md, requirements.txt, docker-compose.yml
  - LICENSE, .github/workflows/


╔════════════════════════════════════════════════════════════════════════════════╗
║                        📊 CONTENU DU REPOSITORY                               ║
╚════════════════════════════════════════════════════════════════════════════════╝

FILES & FOLDERS:

📁 src/
   ├── collectors/
   │   ├── nasa_collector.py       # Collecter NASA EONET
   │   └── usgs_collector.py       # Collecter USGS Earthquakes
   ├── etl/
   │   └── transformer.py          # Pipeline ETL
   └── analysis/
       └── analysis.py             # Scripts analyse

📁 data/
   ├── raw/                        # Données JSON brutes
   └── processed/                  # Données Parquet/CSV

📁 dashboards/
   ├── compact_app.py              # 5 graphiques rapides (8053)
   ├── advanced_app.py             # 8 graphiques avancés (8051)
   ├── ultra_advanced_app.py       # 9 graphiques scientifiques (8052)
   └── professional_app.py         # Pipeline visuelle (8050)

📁 .github/
   └── workflows/
       └── tests.yml               # CI/CD avec GitHub Actions

📄 FILES:
├── README.md                      # Documentation principale
├── DOCUMENTATION.md               # Doc détaillée
├── requirements.txt               # Dépendances Python
├── docker-compose.yml             # Infrastructure Docker
├── .gitignore                     # Fichiers ignorés
├── LICENSE                        # MIT License
├── 00-START-HERE.md              # Guide de démarrage
└── .env                           # Variables d'environnement


╔════════════════════════════════════════════════════════════════════════════════╗
║                      📊 STATS DU REPOSITORY                                    ║
╚════════════════════════════════════════════════════════════════════════════════╝

✅ Files committed: 24
✅ Initial commits: 2
✅ Lines of code: 4,785+
✅ Dashboards: 4 apps
✅ Graphs: 17 visualizations
✅ Data: 10,000+ events
✅ License: MIT
✅ CI/CD: GitHub Actions configured


╔════════════════════════════════════════════════════════════════════════════════╗
║                    🚀 ÉTAPES SUIVANTES (OPTIONNEL)                            ║
╚════════════════════════════════════════════════════════════════════════════════╝

1. ⭐ Ajouter une description courte dans la bio du repo
2. 🏷️ Ajouter des tags: python, data-engineering, dashboards, nasa
3. 📌 Créer un Release v1.0.0
4. 🔧 Activer les "Discussions" pour la communauté
5. 🐛 Ajouter des "Issues" templates
6. 📝 Ajouter un CONTRIBUTING.md pour les contributions


╔════════════════════════════════════════════════════════════════════════════════╗
║                             💡 TIPS                                           ║
╚════════════════════════════════════════════════════════════════════════════════╝

🔐 Pour HTTPS avec authentification:
   - Créez un Personal Access Token: https://github.com/settings/tokens
   - Utilisez le token comme password

🔑 Pour SSH (Recommandé):
   - Générez une clé SSH: ssh-keygen -t ed25519
   - Ajoutez la clé publique sur GitHub: https://github.com/settings/keys

📱 Commandes utiles après le push:
   - Voir le code sur GitHub: git remote -v
   - Cloner le repo: git clone <url>
   - Créer une branche: git checkout -b feature/new-feature


╔════════════════════════════════════════════════════════════════════════════════╗
║                        ✅ CHECKLIST FINALE                                     ║
╚════════════════════════════════════════════════════════════════════════════════╝

Avant de pousser:
☐ Vérifier que .env n'est PAS commité (c'est dans .gitignore)
☐ Vérifier que les données sensibles ne sont pas commises
☐ README.md est lisible et à jour
☐ requirements.txt a toutes les dépendances

Après le push:
☐ Vérifier le repo sur GitHub
☐ Top banner devrait montrer le README
☐ Fichiers apparaissent dans la structure
☐ License affichée
☐ Workflows CI/CD actifs


════════════════════════════════════════════════════════════════════════════════

🎉 Votre projet est prêt pour GitHub!

Commandes à copier/coller:
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main

════════════════════════════════════════════════════════════════════════════════
"""

print(instructions)

# Sauvegarder aussi dans un fichier
with open("GITHUB_PUSH_INSTRUCTIONS.md", "w") as f:
    f.write(instructions.replace("╔", "").replace("╚", "").replace("╝", "").replace("║", "#").replace("═", "-").replace("└", "-").replace("┌", "-").replace("┘", "-").replace("┐", "-"))

print("\n✅ Instructions sauvegardées dans GITHUB_PUSH_INSTRUCTIONS.md")
