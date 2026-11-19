# Préparer et publier avec GitHub Pages

**État au 18 novembre 2026 : paquet local préparé, aucune publication ou opération distante effectuée.** Le dépôt cible et l’URL publique restent inconnus. Le paquet staging ne contient pas de base publique inventée et ne doit pas être confondu avec une version SEO finale.

## Livrable local

- Dossier prêt à transférer pour un contrôle staging : `publication-package/site/`.
- Aucune archive ZIP n’est produite — le transfert et le QA se font directement sur le dossier.
- Commande de régénération : `python3 scripts/prepare_publication.py --mode staging`.
- Contrôle du paquet : `python3 scripts/qa_publication.py --mode staging`.

Le paquet staging contient 87 routes HTML et 217 fichiers de site. Pour empêcher l’indexation prématurée, toutes ses pages portent `noindex,follow`. Il n’embarque ni `sitemap.xml`, ni `robots.txt`, ni canonical, `og:url` ou `mainEntityOfPage`; les images Open Graph/Twitter liées à un hôte et les URL d’image JSON-LD sont omises jusqu’à la confirmation de la base. La prévisualisation E2B n’est pas recopiée dans ces métadonnées. Le dossier `site/` est la racine web; le README du paquet reste hors de cette racine.

Ce staging peut servir à vérifier manuellement l’hébergement, mais **ce n’est pas la version indexable à conserver comme publication finale**. Le générateur ne touche pas au build d’aperçu racine et ne publie, ne déploie ni ne pousse de fichiers.

## Faits et blocages vérifiés

- Le dossier de travail n’est pas un dépôt Git : aucun propriétaire, remote, branche, `CNAME` ou workflow Pages n’est identifié. Aucun fichier `.github/workflows/` n’est configuré.
- `gta6guide.duckdns.org` résout vers `185.199.108.153`; aucune entrée AAAA ni CNAME n’a été renvoyée lors du contrôle DNS.
- Le domaine répond **HTTP 404** avec la page générique GitHub Pages. En HTTPS, la validation TLS échoue : le certificat présenté ne correspond pas au nom `gta6guide.duckdns.org`.
- Ces réponses ne permettent pas d’identifier le dépôt cible ni d’établir que ce sous-domaine DuckDNS est correctement associé à un site Pages. Ne pas utiliser cette adresse comme base SEO ou `CNAME` tant que son routage et TLS ne sont pas réparés et vérifiés.
- Les `sitemap.xml` et `robots.txt` du build d’aperçu historique contiennent des URL E2B. Ils sont exclus du paquet staging et ne doivent pas être soumis ni publiés tels quels.

## Parcours recommandé

### 1. Choisir et préparer le dépôt vous-même

1. Créez/choisissez le dépôt GitHub et notez son propriétaire, son nom, sa branche de publication et l’URL qui servira réellement le site.
2. Pour un site de projet, la base ressemble généralement à `https://OWNER.github.io/REPOSITORY/`. Pour le dépôt utilisateur/organisation `OWNER.github.io`, elle ressemble à `https://OWNER.github.io/`.
3. Dans **Settings → Pages**, sélectionnez votre source de publication. Pour un domaine personnalisé, enregistrez d’abord le domaine dans Pages, puis appliquez les instructions DNS de GitHub à ce domaine exact; attendez la propagation et l’émission du certificat.
4. Aucun remote ni réglage GitHub n’est modifié depuis ce workspace.

### 2. Vérifier le chemin avant d’activer le SEO public

Transférez manuellement le contenu de `publication-package/site/` selon votre source Pages. En mode branche, GitHub Pages propose la racine du dépôt ou `/docs`; copiez alors **le contenu** de `site/` dans l’emplacement retenu. Avec un workflow Actions, le dossier d’artefact peut être `publication-package/site/`.

Confirmez dans un navigateur que la bonne page d’accueil est servie à l’URL exacte, que les routes principales répondent, que le certificat TLS est valide et qu’il n’y a ni 404 GitHub générique ni redirection vers un autre propriétaire/dépôt. Cette première version reste volontairement `noindex`.

### 3. Construire le paquet public final après cette vérification

Le mode public fait lui-même une requête HTTPS : il exige HTTP 200, un certificat accepté, la même origine et le même chemin, ainsi que le titre du guide dans la réponse. Il exige également un opt-in explicite. Il ne fait toujours aucun déploiement.

```sh
python3 scripts/prepare_publication.py \
  --mode public \
  --base-url 'https://OWNER.github.io/REPOSITORY/' \
  --confirm-public-base

python3 scripts/qa_publication.py \
  --mode public \
  --base-url 'https://OWNER.github.io/REPOSITORY/'
```

Remplacez l’exemple par la base exacte qui fonctionne en HTTPS, barre oblique finale comprise. Le dossier `publication-package/site/` est alors régénéré localement avec les métadonnées canoniques/Open Graph/JSON-LD, `robots.txt` et un sitemap fondés sur cette base vérifiée. Aucune archive n’est créée. Vérifiez le résultat QA, puis transférez vous-même le contenu de `publication-package/site/` vers votre source Pages. Si l’hôte ou le chemin change, reconstruisez le dossier avec la nouvelle base.

**Ne forcez pas** `--confirm-public-base` pour contourner une erreur réseau, un certificat invalide, un 404, un hôte E2B ou une URL encore inconnue. Ce flag exprime une confirmation humaine et ne remplace pas le contrôle HTTPS effectué par le script.

### Option workflow GitHub Actions

Aucun workflow n’est livré/activé. Si vous choisissez Actions, adaptez ce modèle dans votre dépôt seulement après avoir choisi la branche et le chemin d’artefact. Un push sur la branche configurée déclenchera alors la publication selon vos réglages :

```yaml
name: Publish GitHub Pages
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/upload-pages-artifact@v4
        with:
          path: publication-package/site
  deploy:
    needs: build
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

Après ajout de ce workflow, sélectionnez **GitHub Actions** dans les paramètres Pages. Le dépôt, son owner, sa branche et le domaine doivent être confirmés par vous; ce modèle ne doit pas être copié tel quel avant ces décisions.

## Veille de version conservée dans le site

Au relevé du 18 novembre 2026, la dernière note numérotée visible dans l’index officiel BSG demeure 1.3.0.0. Le journal BSG du 18 novembre annonce 1.3.5.0 pour la seconde moitié de novembre, sans jour précis ni confirmation d’installation. Le contenu distingue Unity 6, chargement, mémoire, stabilité, fluidité et reconnexion annoncés pour cette mise à jour des travaux futurs (DirectX 12, DLSS Frame Generation, NVIDIA Reflex, végétation et FSR 4). Il ne présente pas 1.3.5.0 comme déployée.

Couverture de veille non exhaustive : la page officielle BSG a été consultée; les recherches X/Reddit/YouTube/GitHub/Steam ont fourni des éléments de contexte de portée variable. Aucune vidéo YouTube récente directement vérifiable sur ce journal n’a été obtenue et les discussions communautaires ne prouvent pas le build installé. Les limites sont consignées dans `docs/recherche-phase-10.md` et `docs/recherche-tarkov-2026-11-18.md`.

## Références GitHub Pages

- [Configurer une source de publication](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [Utiliser des workflows personnalisés](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Gérer un domaine personnalisé](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
- [Limites de GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
- [DuckDNS — FAQ](https://www.duckdns.org/faqs.jsp) et [API/spécification](https://www.duckdns.org/spec.jsp)
