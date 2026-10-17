"""Construit Boussole IA à partir des fichiers de contenu.

Usage : python3 source/construire.py

Produit :
- boussole-ia.html          l'application autonome, à la racine du dossier boussole-ia/ (fichier à ouvrir) ;
- build/artifact.html       la même page sans squelette HTML, pour une publication en ligne.

Chaque fichier de contenu est d'abord contrôlé par valider.js (si Node.js est installé).
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent
CONTENU = SOURCE / "contenu"
RACINE = SOURCE.parent
BUILD = RACINE / "build"

ORDRE = ["socle", "m0", "m1", "m2", "m4", "m5", "prompts", "erreurs"]
TITRES = {
    "socle": "Socle : règles d'or, CADRE, VÉRIF, checklist éthique, matrice outils × données",
    "m0": "Module 0 · Démarrage express",
    "m1": "Module 1 · Comprendre l'IA sans maths",
    "m2": "Module 2 · L'art du prompt",
    "m4": "Module 4 · Évaluation critique",
    "m5": "Module 5 · Éthique et réglementation",
    "prompts": "Bibliothèque de prompts",
    "erreurs": "Exercices « Trouvez l'erreur »",
    "reglementation": "Repères réglementaires (54 pays africains, cadres internationaux)",
}


def valider():
    """Contrôle chaque fichier de contenu avec valider.js ; arrête la construction en cas d'erreur."""
    if not shutil.which("node"):
        print("Node.js absent : validation du contenu ignorée.")
        return
    for nom in ORDRE:
        r = subprocess.run(["node", str(SOURCE / "valider.js"), str(CONTENU / f"{nom}.js")], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"Contenu invalide dans {nom}.js :\n{r.stdout}{r.stderr}")
    print("Contenu validé.")


def reglementation():
    """Transforme la synthèse réglementaire (JSON) en bloc JavaScript REGLEMENTATION."""
    reg = json.loads((CONTENU / "reglementation_afrique.json").read_text(encoding="utf-8"))
    ai_act = dict(reg["ai_act"])
    ai_act["resume"] = next(c["resume"] for c in reg["cadres"] if c["id"] == "ai_act").replace(" Voir le bloc ai_act.", "")
    champs = ("pays", "iso2", "region", "statut", "loi", "autorite", "autorite_operationnelle",
              "sante", "malabo", "strategie_ia", "note", "confiance", "source")
    bloc = {
        "date_verification": reg["date_verification"],
        "date_verification_lisible": reg.get("date_verification_lisible", "octobre 2026"),
        "pays": [{k: p.get(k) for k in champs} for p in reg["pays"]],
        "cadres": [c for c in reg["cadres"] if c["id"] != "ai_act"],
        "ai_act": ai_act,
    }
    return "const REGLEMENTATION = " + json.dumps(bloc, ensure_ascii=False, indent=1) + ";"


def construire():
    valider()
    blocs = []
    for nom in ORDRE:
        code = (CONTENU / f"{nom}.js").read_text(encoding="utf-8").strip()
        blocs.append(f"/* ───────── {TITRES[nom]} ───────── */\n{code}")
    blocs.append(f"/* ───────── {TITRES['reglementation']} ───────── */\n{reglementation()}")
    for b in blocs:
        assert "</script" not in b.lower(), "La séquence </script est interdite dans le contenu."

    contenu = (
        "<script>\n"
        "/* ══════════════════════════════════════════════════════════════════════\n"
        "   CONTENU\n"
        "   Généré depuis source/contenu/ par source/construire.py : modifiez les\n"
        "   fichiers sources, pas ce bloc. Mode d'emploi : docs/FAIRE-EVOLUER.md\n"
        "   ══════════════════════════════════════════════════════════════════════ */\n"
        + "\n\n".join(blocs) + "\n</script>"
    )
    page = (SOURCE / "modele.html").read_text(encoding="utf-8").replace("<!--CONTENU-->", contenu)

    BUILD.mkdir(exist_ok=True)
    (BUILD / "artifact.html").write_text(page, encoding="utf-8")

    autonome = (
        "<!doctype html>\n<html lang=\"fr\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
        + page.replace("<div class=\"app\">", "</head>\n<body>\n<div class=\"app\">", 1)
        + "\n</body>\n</html>\n"
    )
    (RACINE / "boussole-ia.html").write_text(autonome, encoding="utf-8")
    print(f"boussole-ia.html construit ({len(autonome.encode('utf-8')) // 1024} Ko).")


if __name__ == "__main__":
    construire()
