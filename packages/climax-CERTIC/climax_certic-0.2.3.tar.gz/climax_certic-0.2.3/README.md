# CLIMAX

## Install

```
 Utilisation: climax [OPTIONS] COMMAND [ARGS]...                                            
                                                                                            
 Utilitaire en ligne de commande pour la gestion des projets MaX                            
                                                                                            
╭─ Options ────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                  │
│ --show-completion             Show completion for the current shell, to copy it or       │
│                               customize the installation.                                │
│ --help                        Voir cette aide et quitter                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commandes ──────────────────────────────────────────────────────────────────────────────╮
│ sync             Initialisation d'une instance existante de MaX                          │
│ new              Création d'une nouvelle instance de MaX                                 │
│ demo             Installe une édition de démonstration dans l'instance de MaX en cours   │
│ stop             Arrête l'instance de MaX du dossier en cours                            │
│ start            Démarre l'instance de MaX du dossier en cours                           │
│ cache-clear      Efface le cache de climax                                               │
│ config           Affiche la configuration de MaX                                         │
│ freeze           Fait une copie HTML statique du projet dans le dossier                  │
│ bundles-remove   Supprime un bundle pour l'instance de Max en cours                      │
│ bundles-list     Liste les bundles disponibles                                           │
│ bundles-add      Ajoute un bundle pour l'instance de Max en cours                        │
│ feed             Ajoute un fichier XML à l'instance de Max en cours                      │
│ basex            Lance le client de BaseX                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────╯
```

## Development

### Prerequisite

- uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- gettext

### Commands

Type `make help`