from tf.core.files import (
    writeJson,
    fileOpen,
    fileExists,
    initTree,
    dirExists,
    dirRemove,
    dirCopy,
    dirContents,
    stripExt,
)
from tf.core.generic import AttrDict
from tf.core.helpers import console, readCfg
from .helpers import getPageInfo, getImageLocations, getImageSizes

DS_STORE = ".DS_Store"


def fillinIIIF(data, **kwargs):
    tpd = type(data)

    if tpd is str:
        for k, v in kwargs.items():
            pattern = "{" + k + "}"

            if type(v) is int and data == pattern:
                data = v
                break
            else:
                data = data.replace(pattern, str(v))

        return data

    if tpd is list:
        return [fillinIIIF(item, **kwargs) for item in data]

    if tpd is dict:
        return {k: fillinIIIF(v, **kwargs) for (k, v) in data.items()}

    return data


def parseIIIF(settings, prod, selector, **kwargs):
    """Parse the iiif yml file and deliver a filled in section.

    The iiif.yml file contains switches and constants and macros which then are used
    to define IIIF things via templates.

    The top-level section `scans` contains instructions to define extra annotations
    on node types that need to refer to scans.
    This is only used for WATM generation.

    The top-level section `templates` contains fragments from which manifests can be
    constructed. This is only used in this module.

    This function fills in the switches, based on the parameter `prod`, then
    prepares the constants, then prepares the macros, and then uses it all
    to assemble either the `scans` section or the `templates` section; this
    choice is based on the parameter `selector`.

    Parameters
    ----------
    prod: string
        Either `prod` or `dev` or `preview`.
        This determines whether we fill in a production value or a develop value
        or a preview value for each of the settings mentioned in the `switches`
        section of the iiif.yml file.
    selector: string
        Either `scans` or `templates`.
        Which top-level of sections we are going to grab out of the iiif.yml file.
    kwargs: dict
        Additional optional parameters to pass as key value pairs to
        the iiif config file. These values will be filled in for place holders
        of the form `[`*arg*`]`.
    """

    def applySwitches(prod, constants, switches):
        if len(switches):
            for k, v in switches[prod].items():
                constants[k] = v

        return constants

    def substituteConstants(data, macros, constants, kwargs):
        tpd = type(data)

        if tpd is str:
            for k, v in macros.items():
                pattern = f"<{k}>"
                data = data.replace(pattern, str(v))

            for k, v in constants.items():
                pattern = f"«{k}»"

                if type(v) is int and data == pattern:
                    data = v
                    break
                else:
                    data = data.replace(pattern, str(v))

            if type(data) is str:
                for k, v in kwargs.items():
                    pattern = f"[{k}]"

                    if type(v) is int and data == pattern:
                        data = v
                        break
                    else:
                        data = data.replace(pattern, str(v))

            return data

        if tpd is list:
            return [
                substituteConstants(item, macros, constants, kwargs) for item in data
            ]

        if tpd is dict:
            return {
                k: substituteConstants(v, macros, constants, kwargs)
                for (k, v) in data.items()
            }

        return data

    constants = applySwitches(
        prod, settings.get("constants", {}), settings.get("switches", {})
    )
    macros = applySwitches(
        prod, settings.get("macros", {}), settings.get("switches", {})
    )

    return AttrDict(
        {
            x: substituteConstants(xText, macros, constants, kwargs)
            for (x, xText) in settings[selector].items()
        }
    )


class IIIF:
    def __init__(
        self,
        teiVersion,
        app,
        pageInfoDir,
        outputDir=None,
        prod="dev",
        silent=False,
        **kwargs,
    ):
        """Class for generating IIIF manifests.

        Parameters
        ----------
        teiVersion: string
            Subdirectory within the static directory.
            The manifests are generated in this subdirectory, which corresponds to
            the version of the TEI source.
        app: object
            A loaded TF data source
        pageInfoDir: string
            Directory where the files with page information are, especially the
            page sequence file.
        outputDir: string, optional None
            If present, manifests nad logo will be generated in this directory.
            Otherwise a standard location is chosen: `static` at
            the top-level of the repo and within that `prod` or `dev` or `preview`
        prod: string, optional dev
            Whether the manifests are for production (`prod`) or development (`dev`)
            of preview (`preview`)
        silent: boolean, optional False
            Whether to suppress output messages
        kwargs: dict
            Additional optional parameters to pass as key value pairs to
            the iiif config file. These values will be filled in for place holders
            of the form `[`*arg*`]`.
        """
        self.teiVersion = teiVersion
        self.app = app
        self.pageInfoDir = pageInfoDir
        self.prod = prod if prod in {"prod", "dev", "preview"} else "dev"
        self.silent = silent
        self.error = False
        self.kwargs = kwargs

        teiVersionRep = f"/{teiVersion}" if teiVersion else teiVersion

        F = app.api.F
        L = app.api.L

        locations = getImageLocations(app, prod, silent)
        repoLocation = locations.repoLocation
        self.scanDir = locations.scanDir
        self.thumbDir = locations.thumbDir
        scanRefDir = locations.scanRefDir
        self.scanRefDir = scanRefDir
        self.coversDir = locations.coversDir
        doCovers = locations.doCovers
        self.doCovers = doCovers

        outputDir = (
            f"{repoLocation}/static{teiVersionRep}/{prod}"
            if outputDir is None
            else outputDir
        )
        self.outputDir = outputDir
        self.manifestDir = f"{outputDir}/manifests"

        self.pagesDir = f"{scanRefDir}/pages"
        self.logoInDir = f"{scanRefDir}/logo"
        self.logoDir = f"{outputDir}/logo"

        if doCovers:
            self.coversHtmlIn = f"{repoLocation}/programs/covers.html"
            self.coversHtmlOut = f"{outputDir}/covers.html"

        (ok, settings) = readCfg(
            repoLocation, "iiif", "IIIF", verbose=-1 if silent else 1, plain=True
        )
        if not ok:
            self.error = True
            return

        self.settings = settings
        manifestLevel = settings.get("manifestLevel", "folder")
        console(f"Manifestlevel = {manifestLevel}")
        self.manifestLevel = manifestLevel

        self.templates = parseIIIF(settings, prod, "templates", **kwargs)

        folders = (
            [F.folder.v(f) for f in F.otype.s("folder")]
            if manifestLevel == "folder"
            else [
                (F.folder.v(fo), [F.file.v(fi) for fi in L.d(fo, otype="file")])
                for fo in F.otype.s("folder")
            ]
        )

        self.getSizes()
        self.getRotations()
        self.getPageSeq()
        pages = self.pages
        self.folders = folders

        self.console("Collections:")

        if manifestLevel == "folder":
            for folder in folders:
                n = len(pages["pages"][folder])
                self.console(f"{folder:>5} with {n:>4} pages")
        else:
            for folder, files in folders:
                n = len(pages["pages"][folder])
                m = sum(len(x) for x in pages["pages"][folder].values())
                self.console(f"{folder:>10} with {n:>4} files and {m:>4} pages")

    def console(self, msg, **kwargs):
        """Print something to the output.

        This works exactly as `tf.core.helpers.console`

        When the silent member of the object is True, the message will be suppressed.
        """
        silent = self.silent

        if not silent:
            console(msg, **kwargs)

    def getRotations(self):
        if self.error:
            return

        scanRefDir = self.scanRefDir

        rotateFile = f"{scanRefDir}/rotation_pages.tsv"

        rotateInfo = {}
        self.rotateInfo = rotateInfo

        if not fileExists(rotateFile):
            console(f"Rotation file not found: {rotateFile}")
            return

        with fileOpen(rotateFile) as rh:
            next(rh)
            for line in rh:
                fields = line.rstrip("\n").split("\t")
                p = fields[0]
                rot = int(fields[1])
                rotateInfo[p] = rot

    def getSizes(self):
        if self.error:
            return

        scanRefDir = self.scanRefDir
        doCovers = self.doCovers
        silent = self.silent

        self.sizeInfo = getImageSizes(scanRefDir, doCovers, silent)

    def getPageSeq(self):
        if self.error:
            return

        manifestLevel = self.manifestLevel
        doCovers = self.doCovers
        zoneBased = self.settings.get("zoneBased", False)

        if doCovers:
            coversDir = self.coversDir
            covers = sorted(
                stripExt(f) for f in dirContents(coversDir)[0] if f is not DS_STORE
            )
            self.covers = covers

        pageInfoDir = self.pageInfoDir

        pages = getPageInfo(pageInfoDir, zoneBased, manifestLevel)

        if doCovers:
            pages["covers"] = covers

        self.pages = pages

    def genPages(self, kind, folder=None, file=None):
        if self.error:
            return

        manifestLevel = self.manifestLevel
        zoneBased = self.settings.get("zoneBased", False)

        templates = self.templates
        sizeInfo = self.sizeInfo[kind]
        rotateInfo = None if kind == "covers" else self.rotateInfo
        things = self.pages[kind]
        theseThings = things if folder is None else things.get(folder, None)

        if manifestLevel == "folder":
            thesePages = theseThings or []
        else:
            thesePages = theseThings if file is None else theseThings.get(file, [])

        if kind == "covers":
            folder = "covers"

        pageItem = templates.coverItem if kind == "covers" else templates.pageItem

        itemsSeen = set()

        items = []

        nPages = 0

        for p in thesePages:
            nPages += 1

            if zoneBased:
                (p, region) = p
            else:
                region = "full"

            item = {}
            w, h = sizeInfo.get(p, (0, 0))
            rot = 0 if rotateInfo is None else rotateInfo.get(p, 0)

            key = (p, w, h, rot)

            if key in itemsSeen:
                continue

            itemsSeen.add(key)

            for k, v in pageItem.items():
                v = fillinIIIF(
                    v,
                    folder=folder,
                    file=file,
                    page=p,
                    region=region,
                    width=w,
                    height=h,
                    rot=rot,
                )
                item[k] = v

            items.append(item)

        pageSequence = (
            templates.coverSequence if kind == "covers" else templates.pageSequence
        )
        manifestDir = self.manifestDir

        data = {}

        for k, v in pageSequence.items():
            v = fillinIIIF(v, folder=folder, file=file)
            data[k] = v

        data["items"] = items

        nItems = len(items)

        if nItems:
            writeJson(
                data,
                asFile=(
                    f"{manifestDir}/{folder}.json"
                    if manifestLevel == "folder"
                    else f"{manifestDir}/{folder}/{file}.json"
                ),
            )
        return (nPages, nItems)

    def manifests(self):
        if self.error:
            return

        folders = self.folders
        manifestDir = self.manifestDir
        logoInDir = self.logoInDir
        logoDir = self.logoDir
        doCovers = self.doCovers
        manifestLevel = self.manifestLevel

        prod = self.prod
        settings = self.settings
        server = settings["switches"][prod]["server"]

        initTree(manifestDir, fresh=True)

        if doCovers:
            coversHtmlIn = self.coversHtmlIn
            coversHtmlOut = self.coversHtmlOut

            with fileOpen(coversHtmlIn) as fh:
                coversHtml = fh.read()

            coversHtml = coversHtml.replace("«server»", server)

            with fileOpen(coversHtmlOut, "w") as fh:
                fh.write(coversHtml)

            self.genPages("covers")

        p = 0
        i = 0
        m = 0

        if manifestLevel == "folder":
            for folder in folders:
                (thisP, thisI) = self.genPages("pages", folder=folder)
                p += thisP
                i += thisI

                if thisI:
                    m += 1
        else:
            for folder, files in folders:
                folderDir = f"{manifestDir}/{folder}"
                initTree(folderDir, fresh=True, gentle=False)

                folderI = 0

                for file in files:
                    (thisP, thisI) = self.genPages("pages", folder=folder, file=file)
                    p += thisP
                    i += thisI

                    if thisI:
                        m += 1

                    folderI += thisI

                if folderI == 0:
                    dirRemove(folderDir)

        if dirExists(logoInDir):
            dirCopy(logoInDir, logoDir)
        else:
            console(f"Directory with logos not found: {logoInDir}", error=True)

        self.console(
            f"{m} IIIF manifests with {i} items for {p} pages generated in {manifestDir}"
        )
