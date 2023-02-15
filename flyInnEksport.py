import arcpy
import os
import unicodedata
import numpy as py
import re

# Henter input fra bruker
valgt_layout = arcpy.GetParameterAsText(0)
gruppelag = arcpy.GetParameterAsText(1)
eksport_folder = arcpy.GetParameterAsText(2)

# Henter grunnvariabler
gis = arcpy.mp.ArcGISProject("CURRENT")
mp = gis.activeMap

# valgt_layout = gis.listLayouts()[0].name
# gruppelag = "Fly_inn"
# eksport_folder = r"C:\DATA\Koding\Lag_eksport\Media"

# arcpy.AddMessage("\n Prøver å eksportere layout:\n{} - {} - {}".format(valgt_layout, gruppelag, eksport_folder))

# Deklarerer variabler som skal brukes
ly = gis.listLayouts(valgt_layout)[0]
flyinn_gruppelag = mp.listLayers(gruppelag)[0]
flyinn_lag = flyinn_gruppelag.listLayers()
ikke_temalag = test = [item for item in mp.listLayers() if item not in flyinn_lag and item.isGroupLayer != True] # Fjerner temalag og gruppelag fra den komplette laglista

# Funksjon for å rense navn som skal brukes inn i filnavn
def slugify(value, allow_unicode=True):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

# Funksjon for å skur av og på lag som er aktiv og ikke aktiv, eksporterer deretter kartet uten bakgrunnskart
def eksporterLagvis(nr, aktivt_lag, lagliste, layout):
    for x in ikke_temalag: x.visible = False # Skrur av lag som ikke er temalag
    for row in lagliste:
        if row != aktivt_lag:
            row.visible = False
        elif row == aktivt_lag:
            row.visible = True

    filnavn = os.path.join(eksport_folder,"{}_{}_{}".format(slugify(layout.name), slugify(gruppelag), (nr+1)))
    # layout.exportToPDF(filnavn)
    layout.exportToPNG(filnavn, resolution=300, transparent_background=True)
    arcpy.AddMessage("-- Ferdig med å skrive ut kart {}".format(aktivt_lag.name))

# Slå av temalag og skrive ut bare bakgrunnskart
for x in flyinn_lag: x.visible = False
for x in ikke_temalag: x.visible = True

filnavn = os.path.join(eksport_folder, "{}_{}_uten_temalag".format(slugify(gis.metadata.title), slugify(ly.name)))
ly.exportToPNG(filnavn, resolution=300, transparent_background=True)

# Itererer over lagene i gruppelaget over temalag, og eksporterer disse
for nr,lag in enumerate(flyinn_lag):
    arcpy.AddMessage("\n-------------------------------------------\n- Prøver å skrive ut lag {}".format(lag.name))
    eksporterLagvis(nr, lag, flyinn_lag, ly)

arcpy.AddMessage("\nEksportert alle lag enkeltvis, eksporterer et kart me alle lag aktiv")

# Gjør alle lag synlige før siste eksport
for x in mp.listLayers(): x.visible = True

filnavn = os.path.join(eksport_folder, "{}_{}".format(slugify(gis.metadata.title), slugify(ly.name)))
# ly.exportToPDF(filnavn)
ly.exportToPNG(filnavn, resolution=300, transparent_background=True)

