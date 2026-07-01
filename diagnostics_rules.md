# Règles diagnostics — Compromis V6

### 2.6 Diagnostics — lecture progressive (🆕 v4.8)

**Table de correspondance fieldId :**

| Diagnostic | Champ | fieldId | Présence | Conclusion |
|---|---|---|---|---|
| Termites (PC) | `Document_Termites_PC` | `fldE7zOKdvTTDez7a` | `{Presence_Termites_PC}` | `{Conclusion_Termites_PC}` |
| Assainissement (PC) | `Document_Assainissement_PC` | `fldhawarDUr6rWnhU` | `{Presence_Ass_PC}` | `{Conclusion_Ass_PC}` |
| Termites | `Document_termites` | `fldc97dCLbjD21P2w` | `{Presence_Termites}` | `{Conclusion_Termites}` |
| Gaz | `Document_diagnostic_gaz` | `fld2zHTzUt1qMG8Hd` | `{Presence_Gaz}` | `{Conclusion_Gaz}` |
| ERP | `Document_ERP` | `fldFJpRQ6AY6kDkQs` | `{Presence_ERP}` | `{Conclusion_ERP}` |
| DPE | `Document_DPE` | `fldxWm1CQD3ZmTNTv` | `{Presence_DPE}` | `{Conclusion_DPE}` |
| Électricité | `Document_electricite` | `fldy8m6qByLxCfvE8` | `{Presence_elec}` | `{Conclusion_elec}` |
| Assainissement | `Document_Assainissement` | `fldqRsTHWkltKlDNA` | `{Presence_ass}` | `{Conclusion_ass}` |

**Étape 1 — tester la présence :**
Champ absent/vide dans le dump → `{Presence_*}` = `Non`, `{Conclusion_*}` = `Sans objet`. Stop.
Champ présent → `{Presence_*}` = `Oui`. Passer à l'étape 2.

**Étape 2 — télécharger tous les PDFs présents en parallèle (un seul appel bash) :**
```bash
mkdir -p /home/claude/build/diagnostics && cd /home/claude/build/diagnostics
# Un curl par PDF présent, tous en parallèle :
curl -L "<url_termites>" -o termites.pdf -s &
curl -L "<url_dpe>" -o dpe.pdf -s &
# ... etc.
wait
```
Utiliser **uniquement** le champ `url` racine de l'attachment — jamais `thumbnails.*.url`.

**Étape 3 — 🆕 lecture progressive par type (STRATÉGIE FIGÉE) :**

> **Principe :** extraire uniquement les pages nécessaires, dans l'ordre indiqué.
> S'arrêter dès que **date ET conclusion** sont obtenues. Ne jamais lire un PDF entier.

#### TERMITES (structure AFNOR NF P 03-201 — IMMODIAG et autres)
```bash
# Page 1 : date du repérage (texte natif)
pdftotext -f 1 -l 1 -layout termites.pdf -
```
Extraire : `Date du repérage : JJ/MM/AAAA` → c'est la **date**.
```bash
# Page 2 : tableau des résultats (texte natif)
pdftotext -f 2 -l 2 -layout termites.pdf -
```
Lire la colonne "Résultats du diagnostic d'infestation" :
- Toutes les cellules = `Absence d'indices d'infestation de termites` → conclusion =
  `Absence d'indice d'infestation de termites.`
- Au moins une cellule différente → reprendre le libellé exact de la cellule.
**Stop après page 2.** Les pages 3-13 ne contiennent que des rappels réglementaires.

#### DPE (structure ADEME — toujours page 1 image)
```bash
# Page 1 : date en texte natif
pdftotext -f 1 -l 1 dpe.pdf - | grep -E "Etabli le|Valable"
```
Extraire `Etabli le : JJ/MM/AAAA` → **date**.
```bash
# Page 1 : rasteriser pour lire les lettres (graphique image, jamais en texte natif)
pdftoppm -jpeg -r 150 -f 1 -l 1 dpe.pdf dpe_p1
# Puis lire visuellement dpe_p1-1.jpg (ou dpe_p1-01.jpg selon le nombre de pages)
```
Lire dans le graphique "Performance énergétique et climatique" :
- Flèche pointant sur la lettre dans l'échelle gauche (consommation énergie primaire) → **Niveau X**
- Flèche pointant sur la lettre dans l'échelle droite (GES/CO₂) → **Niveau Y**
**Stop après page 1.** Pages 2-11 = détails et recommandations.

Conclusion : `Consommations énergétiques : Niveau X. Émissions de gaz à effet de serre (GES) : Niveau Y.`

#### ÉLECTRICITÉ (structure AFNOR NF C 16-600)
```bash
# Page 1 : date (texte natif)
pdftotext -f 1 -l 1 -layout electricite.pdf - | grep -E "Date du repérage|repérage"
```
Extraire la date.
```bash
# Page 2 : synthèse E.1 avec cases cochées (image — rasteriser)
pdftoppm -jpeg -r 150 -f 2 -l 2 electricite.pdf elec_p2
```
Lire visuellement `elec_p2-2.jpg` (ou `elec_p2-02.jpg`) — section **E.1 Anomalies et/ou constatations diverses relevées** :
- Case cochée sur la 4e ligne (anomalies + constatations) → `L'installation intérieure d'électricité comporte une ou des anomalies et fait l'objet de constatations diverses.`
- Case cochée sur la 3e ligne (anomalies seules) → `L'installation intérieure d'électricité comporte une ou des anomalies.`
- Case cochée sur la 2e ligne (constatations seules) → `L'installation intérieure d'électricité ne comporte aucune anomalie mais fait l'objet de constatations diverses.`
- Case cochée sur la 1re ligne (aucune anomalie) → `L'installation intérieure d'électricité ne comporte aucune anomalie.`
**Stop après page 2.**

#### GAZ (même structure que électricité)
```bash
pdftotext -f 1 -l 1 -layout gaz.pdf - | grep -E "Date|repérage"
pdftoppm -jpeg -r 150 -f 2 -l 2 gaz.pdf gaz_p2
```
Lire page 2 visuellement — section synthèse des anomalies.
**Stop après page 2.**

#### ERP (État des Risques et Pollutions)
```bash
# Page 1 : date (texte natif)
pdftotext -f 1 -l 1 -layout erp.pdf - | grep -E "Date|établi|édité"
```
Extraire la date.
```bash
# Page 1 rasterisée : lire les cases cochées par aléa
pdftoppm -jpeg -r 150 -f 1 -l 1 erp.pdf erp_p1
```
Lire visuellement les cases cochées pour chaque aléa (risques naturels, technologiques, miniers,
retrait-gonflement, radon, bruit aérodrome, sismicité, trait de côte…).
Si page 1 ne couvre pas tous les aléas → rasteriser page 2 uniquement. **Stop au plus tard page 2.**

Conclusion : énumérer aléa par aléa ce qui est indiqué (concerné/non concerné/soumis/non soumis)
d'après les cases réellement cochées.

#### ASSAINISSEMENT (souvent scanné intégralement)
```bash
# Tenter texte natif page 1 :
pdftotext -f 1 -l 1 assainissement.pdf -
```
- Si texte non vide → extraire date et conclusion du contrôle directement.
- Si vide (scanné) → rasteriser page 1 uniquement :
```bash
pdftoppm -jpeg -r 150 -f 1 -l 1 assainissement.pdf assain_p1
```
Lire visuellement : date du contrôle + mention "CONFORME" / "NON CONFORME" / "CONFORME AVEC OBSERVATION".
**Stop après page 1.** (Pages 2-3 = détails des essais.)

Conclusion : `[Mention exacte lue]. Diagnostic en date du JJ/MM/AAAA.`

**Règle commune à tous les diagnostics :**
- Date ou conclusion illisible après les pages indiquées → laisser ce qui a été lu + repère `[…]`
  pour la partie manquante + signaler en synthèse. **Ne jamais aller chercher plus loin.**
- La colonne « Concerné » du tableau dans le maître est en dur — **ne jamais la modifier**.
- Conclusions multilignes (ERP, DPE) → `<w:br/>` entre lignes dans la cellule (§4.4 bis).

---