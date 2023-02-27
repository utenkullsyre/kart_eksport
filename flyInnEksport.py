import arcpy
import os
import unicodedata
import numpy as np
import re

# Henter input fra bruker
valgt_layout = arcpy.GetParameterAsText(0)
gruppelag = arcpy.GetParameterAsText(1)
eksport_folder = arcpy.GetParameterAsText(2)
dpi = int(arcpy.GetParameterAsText(3))

# Henter grunnvariabler
gis = arcpy.mp.ArcGISProject("CURRENT")
mp = gis.activeMap

# valgt_layout = gis.listLayouts()[0].name
# gruppelag = "Fly_inn"
# eksport_folder = r"C:\DATA\Koding\Lag_eksport\Media"

# arcpy.AddMessage("\n Prøver å eksportere layout:\n{} - {} - {}".format(valgt_layout, gruppelag, eksport_folder))

# Deklarerer variabler som skal brukes
ly = gis.listLayouts(valgt_layout)[0]
synlige_lag = [x for x in mp.listLayers() if x.visible == True]
flyinn_gruppelag = mp.listLayers(gruppelag)[0]
flyinn_lag = [x for x in flyinn_gruppelag.listLayers() if x.visible == True]
# synlige_bakgrunnslag = [item for item in mp.listLayers() if item not in flyinn_lag and item.isGroupLayer != True] # Fjerner temalag og gruppelag fra den komplette laglista
synlige_bakgrunnslag = list(filter(lambda i: i not in flyinn_lag and i != flyinn_gruppelag, synlige_lag))

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
    for x in synlige_bakgrunnslag: x.visible = False # Skrur av lag som ikke er temalag
    for row in lagliste:
        if row != aktivt_lag:
            row.visible = False
        elif row == aktivt_lag:
            row.visible = True

    filnavn = os.path.join(eksport_folder,"{}_{}_{}".format(slugify(layout.name), slugify(gruppelag), (nr+1)))
    # layout.exportToPDF(filnavn)
    layout.exportToPNG(filnavn, resolution=dpi, transparent_background=True)
    arcpy.AddMessage("-- Ferdig med å skrive ut kart {}".format(aktivt_lag.name))


def renskeBakgrunnskart(temalag):
    ikke_synlige = []
    alle_lag = mp.listLayers()
    ikkesynlige_gruppelag = [x for x in alle_lag if x.isGroupLayer == True and x.visible != True]

    for gruppelag in ikkesynlige_gruppelag:
        for lyr in gruppelag.listLayers():
            ikke_synlige.append(lyr)

    for lag in [x for x in alle_lag if x.visible != True]:
        ikke_synlige.append(lag)
    print(ikke_synlige)

    bakgrunn = np.subtract(np.array(alle_lag), np.array(ikke_synlige))

    return ikke_synlige

def resetKart(synlige_lag):
    for row in mp.listLayers():
        if row in synlige_lag:
            row.visible = True
        else:
            row.visible = False

try:
    # Slå av temalag og skrive ut bare bakgrunnskart
    arcpy.AddMessage("\n-------------------------------------------\n Skriver ut bakgrunnskart uten temalag")
    for x in flyinn_lag: x.visible = False
    for x in synlige_bakgrunnslag: x.visible = True

    filnavn = os.path.join(eksport_folder, "{}_{}_bakgrunn".format(slugify(gis.metadata.title), slugify(ly.name)))
    ly.exportToPNG(filnavn, resolution=dpi, transparent_background=True)

    # Itererer over lagene i gruppelaget over temalag, og eksporterer disse
    for nr, lag in enumerate(flyinn_lag):
        arcpy.AddMessage("\n-------------------------------------------\n- Prøver å skrive ut lag {}".format(lag.name))
        eksporterLagvis(nr, lag, flyinn_lag, ly)

    arcpy.AddMessage("\nEksportert alle lag enkeltvis, eksporterer et kart me alle lag aktiv")

    # Gjør alle lag synlige før siste eksport
    resetKart(synlige_lag)
    filnavn = os.path.join(eksport_folder, "{}_{}_alle_lag".format(slugify(gis.metadata.title), slugify(ly.name)))
    # ly.exportToPDF(filnavn)
    ly.exportToPNG(filnavn, resolution=dpi, transparent_background=True)

except:
    arcpy.AddMessage("Noe gikk galt, prøv igjen.")

finally:
    resetKart(synlige_lag)
    arcpy.AddMessage("Scriptet er ferdig med å kjøre")



