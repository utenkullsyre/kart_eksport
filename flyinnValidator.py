import arcpy


class ToolValidator:
    # Class to add custom behavior and properties to the tool and tool parameters.

    def __init__(self):
        # set self.params for use in other function
        self.params = arcpy.GetParameterInfo()

    def initializeParameters(self):
        # Customize parameter properties.
        # This gets called when the tool is opened.
        pr = arcpy.mp.ArcGISProject("CURRENT")
        mp = pr.activeMap

        layouts = pr.listLayouts()
        gruppelag = list(filter(lambda x: x.isGroupLayer, mp.listLayers()))

        self.params[0].filter.list = [x.name for x in layouts]
        self.params[1].filter.list = [x.name for x in gruppelag]
        return

    def updateParameters(self):
        pr = arcpy.mp.ArcGISProject("CURRENT")
        layOuts = [x.name for x in pr.listLayouts()]
        # formater = ["EPS", "SVG", "PDF", "JPG", "PNG"]
        # Modify parameter values and properties.
        # This gets called each time a parameter is modified, before
        # standard validation.

        return

    def updateMessages(self):
        # Customize messages for the parameters.
        # This gets called after standard validation

        ## pr = arcpy.mp.ArcGISProject("CURRENT")
        ## layOuts = [x.name for x in pr.listLayouts()]
        ## if len(pr.listLayouts()) == 0:
        ##    self.params[0].addErrorMessage("Finner ingen layouter i prosjektet")
        return

    # def isLicensed(self):
    #     # set tool isLicensed.
    # return True

    def postExecute(self):
        # This method takes place after outputs are processed and
        # added to the display.
        self.params[0].value = []
        self.params[0].filter.list = []
        return