#!/usr/bin/env python3
"""Bygger Høstlys og Høstkveld fra palett.py.

    python3 bygg.py            lager themes/*.json og ../../iterm2/farger/*.itermcolors
    python3 bygg.py --sjekk    skriver i tillegg ut kontrasten for tekstfargene

Etterpå: `npx @vscode/vsce package -o host-theme.vsix` og installer på nytt
(eller kjør setup.sh).

Fargene i grensesnittet og i koden er beskrevet med navn fra paletten
("rod", "markering" osv.), aldri med hex-koder. Hex-kodene står bare i palett.py.
"""
import json
import plistlib
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # ingen __pycache__ i mappa
from palett import FARGER, HOSTKVELD, HOSTLYS

HER = Path(__file__).resolve().parent


# ---------- små hjelpere ----------

def a(farge, alfa):
    """Fargen med gjennomsiktighet, alfa mellom 0 og 1."""
    return (farge, alfa)


INGEN = "#00000000"  # helt gjennomsiktig: ingen kantlinje


def lys(p, mork, lyst):
    """Velg ulik palettfarge i Høstkveld og Høstlys."""
    return mork if p["type"] == "dark" else lyst


def hex_til_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def los(p, verdi):
    """Gjør om et palettnavn, (navn, alfa) eller en hex-kode til en hex-streng."""
    if isinstance(verdi, tuple):
        farge, alfa = verdi
        return los(p, farge)[:7] + format(round(alfa * 255), "02x")
    if verdi.startswith("#"):
        return verdi.lower()
    return p[verdi].lower()


# ---------- grensesnittet ----------

def ui(p):
    """Alle fargene i grensesnittet. Nøkkel -> palettnavn."""
    return {
        # Grunnfarger som resten av VS Code bygger på
        "foreground": "tekst",
        "focusBorder": "fokus",
        "widget.border": INGEN,
        "descriptionForeground": "dempet",

        # Editoren
        "editor.background": "bakgrunn",
        "editor.foreground": "tekst",
        "editorCursor.foreground": "tekst",
        "editor.selectionBackground": "markering",
        "editor.inactiveSelectionBackground": "markering_svak",
        "editor.selectionHighlightBackground": "markering_svak",
        "editor.wordHighlightBackground": "markering_svak",
        "editor.wordHighlightStrongBackground": "markering_svak",
        "editor.findMatchBackground": "sok",
        "editor.findMatchBorder": "oransje",
        "editor.findMatchHighlightBackground": "sok_svak",
        "editor.findRangeHighlightBackground": "linje",
        "editor.lineHighlightBackground": "linje",
        "editor.lineHighlightBorder": INGEN,
        "editorLineNumber.foreground": "linjenr",
        "editorLineNumber.activeForeground": "oransje",
        "editorIndentGuide.background1": "hjelpelinje",
        "editorIndentGuide.activeBackground1": "hjelpelinje_aktiv",
        "editorWhitespace.foreground": "mellomrom",
        "editorRuler.foreground": "hjelpelinje",
        "editorBracketMatch.background": "klammepar",
        "editorBracketMatch.border": INGEN,
        **{f"editorBracketHighlight.foreground{i}": "dempet" for i in range(1, 7)},
        "editorBracketHighlight.unexpectedBracket.foreground": "rod",
        "editorGutter.background": "bakgrunn",
        "editorGroupHeader.tabsBackground": "ramme",
        "editorGroup.border": INGEN,
        "editorWidget.background": "widget",
        "editorWidget.border": "widgetkant",
        "editorHoverWidget.background": "widget",
        "editorHoverWidget.border": "widgetkant",
        "editorSuggestWidget.background": "widget",
        "editorSuggestWidget.border": "widgetkant",
        "editorSuggestWidget.selectedBackground": "markering",
        "editorError.foreground": "rod",
        "editorWarning.foreground": "oransje",
        "editorInfo.foreground": "bla",
        "editorOverviewRuler.border": INGEN,

        # Faner
        "tab.activeBackground": "bakgrunn",
        "tab.activeForeground": "tekst",
        "tab.inactiveBackground": "ramme",
        "tab.inactiveForeground": "fane_inaktiv",
        "tab.border": INGEN,
        "tab.activeBorderTop": INGEN,

        # Sidelinje, aktivitetslinje, tittel- og statuslinje
        "sideBar.background": "ramme",
        "sideBar.foreground": "tekst",
        "sideBar.border": INGEN,
        "sideBarSectionHeader.background": "ramme",
        "sideBarTitle.foreground": "tekst",
        "activityBar.background": "ramme",
        "activityBar.foreground": "tekst",
        "activityBar.inactiveForeground": "inaktiv",
        "activityBar.border": INGEN,
        "activityBarBadge.background": "merke",
        "activityBarBadge.foreground": "bakgrunn",
        "badge.background": "merke",
        "badge.foreground": "bakgrunn",
        "titleBar.activeBackground": "ramme",
        "titleBar.activeForeground": "tekst",
        "titleBar.inactiveBackground": "ramme",
        "titleBar.inactiveForeground": "inaktiv",
        "titleBar.border": INGEN,
        "statusBar.background": "ramme",
        "statusBar.foreground": "tekst",
        "statusBar.border": INGEN,
        "statusBar.noFolderBackground": "ramme",
        "statusBar.debuggingBackground": "oransje",
        "statusBar.debuggingForeground": "bakgrunn",

        # Panelet (terminal, problemer)
        "panel.background": "bakgrunn",
        "panel.border": INGEN,
        "panelTitle.activeForeground": "tekst",
        "panelTitle.activeBorder": "oransje",
        "panelTitle.inactiveForeground": "dempet",

        # Lister og trær
        "list.activeSelectionBackground": "liste_aktiv",
        "list.activeSelectionForeground": "tekst",
        "list.inactiveSelectionBackground": "liste_inaktiv",
        "list.hoverBackground": "liste_hover",
        "list.focusOutline": "hjelpelinje_aktiv",
        "list.highlightForeground": "oransje",

        # Tekstfelt, knapper, rullefelt
        "input.background": "felt",
        "input.border": "widgetkant",
        "input.foreground": "tekst",
        "input.placeholderForeground": "plassholder",
        "dropdown.background": "felt",
        "dropdown.border": "widgetkant",
        "button.background": "knapp",
        "button.foreground": "bakgrunn",
        "button.hoverBackground": "knapp_hover",
        "scrollbarSlider.background": a("rullefelt", 0x22 / 255),
        "scrollbarSlider.hoverBackground": a("rullefelt", 0x33 / 255),
        "scrollbarSlider.activeBackground": a("rullefelt", 0x44 / 255),
        "textLink.foreground": "lenke",
        "textLink.activeForeground": "lenke",

        # Git i filutforskeren
        "gitDecoration.modifiedResourceForeground": "oransje",
        "gitDecoration.untrackedResourceForeground": "gronn",
        "gitDecoration.addedResourceForeground": "gronn",
        "gitDecoration.deletedResourceForeground": "rod",
        "gitDecoration.ignoredResourceForeground": "inaktiv",

        # Terminalen
        "terminal.background": "bakgrunn",
        "terminal.foreground": "tekst",
        "terminalCursor.foreground": "tekst",
        "terminal.selectionBackground": "markering",
        **{f"terminal.ansi{n}": v for n, v in p["ansi"].items()},

        # Ingen kantlinjer
        "editorGroupHeader.tabsBorder": INGEN,
        "editorGroupHeader.border": INGEN,
        "sideBarSectionHeader.border": INGEN,
        "tab.activeBorder": INGEN,
        "commandCenter.border": INGEN,
        "commandCenter.inactiveBorder": INGEN,
        "commandCenter.background": "kommandosenter",
        "commandCenter.activeBackground": "kommandosenter_aktiv",
        **ui_utvidet(p),
    }


def ui_utvidet(p):
    """Resten av grensesnittet: alt som ellers ville fått VS Codes egne farger.

    Kontrollert med revisjonsskriptet, som viser hvilke nøkler som faller
    tilbake på VS Codes standardfarger (blått, turkis, kalde gråtoner).
    """
    skygge = lys(p, a("#000000", 0.45), a("#3c3836", 0.16))
    hover = a("tekst", lys(p, 0.10, 0.07))
    aktiv = a("tekst", lys(p, 0.16, 0.11))
    slipp = a("oransje", 0.16)  # når noe dras over et område
    lagt_til, fjernet = "gronn", "rod"
    u = {}

    # ----- Grunnfarger og tekst i grensesnittet -----
    u.update({
        "icon.foreground": a("tekst", 0.85),
        "disabledForeground": "inaktiv",
        "errorForeground": "rod",
        "strongForeground": "tekst",
        "selection.background": "markering",
        "textBlockQuote.background": "widget",
        "textBlockQuote.border": "dempet",
        "textCodeBlock.background": "widget",
        "textPreformat.foreground": "bla",
        "textPreformat.background": "markering_svak",
        "textSeparator.foreground": "widgetkant",
        "sash.hoverBorder": "oransje",
        "toolbar.hoverBackground": hover,
        "toolbar.activeBackground": aktiv,
        "widget.shadow": skygge,
        "scrollbar.shadow": skygge,
        "editorStickyScroll.shadow": skygge,
        "sideBarStickyScroll.shadow": skygge,
        "panelStickyScroll.shadow": skygge,
        "listFilterWidget.shadow": skygge,
        "inlineChat.shadow": skygge,
        "diffEditor.unchangedRegionShadow": skygge,
    })

    # ----- Aktivitetslinja (ligger øverst), merker og profiler -----
    u.update({
        "activityBar.activeBorder": "oransje",
        "activityBar.dropBorder": "oransje",
        "activityBarTop.foreground": "tekst",
        "activityBarTop.inactiveForeground": "inaktiv",
        "activityBarTop.activeBorder": "oransje",
        "activityBarTop.dropBorder": "oransje",
        "activityErrorBadge.background": "rod",
        "activityErrorBadge.foreground": "bakgrunn",
        "activityWarningBadge.background": "oransje",
        "activityWarningBadge.foreground": "bakgrunn",
        "profileBadge.background": "dempet",
        "profileBadge.foreground": "bakgrunn",
    })

    # ----- Statuslinja -----
    u.update({
        "statusBarItem.hoverBackground": hover,
        "statusBarItem.compactHoverBackground": hover,
        "statusBarItem.activeBackground": aktiv,
        "statusBarItem.prominentBackground": aktiv,
        "statusBarItem.prominentHoverBackground": hover,
        "statusBarItem.errorBackground": "rod",
        "statusBarItem.errorForeground": "bakgrunn",
        "statusBarItem.errorHoverBackground": hover,
        "statusBarItem.warningBackground": "oransje",
        "statusBarItem.warningForeground": "bakgrunn",
        "statusBarItem.warningHoverBackground": hover,
        "statusBarItem.offlineBackground": "rod",
        "statusBarItem.offlineForeground": "bakgrunn",
        "statusBarItem.offlineHoverBackground": hover,
        "statusBarItem.remoteBackground": "ramme",
        "statusBarItem.remoteForeground": "oransje",
        "statusBarItem.remoteHoverBackground": hover,
        "statusBar.debuggingBorder": INGEN,
        "statusBar.focusBorder": "oransje",
        "statusBarItem.focusBorder": "oransje",
    })

    # ----- Faner -----
    u.update({
        "tab.hoverBackground": "liste_hover",
        "tab.unfocusedHoverBackground": "liste_hover",
        "tab.activeModifiedBorder": "oransje",
        "tab.inactiveModifiedBorder": a("oransje", 0.5),
        "tab.unfocusedActiveModifiedBorder": a("oransje", 0.5),
        "tab.unfocusedInactiveModifiedBorder": a("oransje", 0.25),
        "tab.lastPinnedBorder": "widgetkant",
        "tab.dragAndDropBorder": "oransje",
    })

    # ----- Editoren -----
    u.update({
        "editorActiveLineNumber.foreground": "oransje",
        "editor.hoverHighlightBackground": "markering_svak",
        "editor.rangeHighlightBackground": a("oransje", 0.10),
        "editor.foldPlaceholderForeground": "dempet",
        "editor.linkedEditingBackground": a("rod", 0.15),
        "editor.snippetTabstopHighlightBackground": "markering_svak",
        "editor.snippetFinalTabstopHighlightBorder": "dempet",
        "editor.inlineValuesBackground": a("oransje", 0.15),
        "editor.inlineValuesForeground": "dempet",
        "editor.stackFrameHighlightBackground": a("oransje", 0.15),
        "editor.focusedStackFrameHighlightBackground": a("gronn", 0.15),
        "editor.compositionBorder": "tekst",
        "editor.placeholder.foreground": "plassholder",
        "editorCodeLens.foreground": "dempet",
        "editorGhostText.foreground": "kommentar",
        "editorHint.foreground": "dempet",
        "editorInlayHint.foreground": "dempet",
        "editorInlayHint.background": a("dempet", 0.12),
        "editorInlayHint.typeForeground": "dempet",
        "editorInlayHint.parameterForeground": "dempet",
        "editorLightBulb.foreground": "oransje",
        "editorLightBulbAi.foreground": "oransje",
        "editorLightBulbAutoFix.foreground": "gronn",
        "editorLink.activeForeground": "lenke",
        "editorStickyScrollHover.background": "liste_hover",
        "editorGutter.foldingControlForeground": "dempet",
        "editorGutter.addedBackground": lagt_til,
        "editorGutter.addedSecondaryBackground": a(lagt_til, 0.5),
        "editorGutter.modifiedBackground": "oransje",
        "editorGutter.modifiedSecondaryBackground": a("oransje", 0.5),
        "editorGutter.deletedBackground": fjernet,
        "editorGutter.deletedSecondaryBackground": a(fjernet, 0.5),
        "editorCommentsWidget.replyInputBackground": "felt",
        "editorCommentsWidget.resolvedBorder": "dempet",
        "editorCommentsWidget.unresolvedBorder": "oransje",
        "editorCommentsWidget.rangeActiveBackground": a("oransje", 0.12),
        "editorCommentsWidget.rangeBackground": a("oransje", 0.06),
        "commentsView.resolvedIcon": "dempet",
        "commentsView.unresolvedIcon": "oransje",
        "editorUnicodeHighlight.border": "oransje",
        "editorMarkerNavigation.background": "widget",
        "editorMarkerNavigationError.background": "rod",
        "editorMarkerNavigationWarning.background": "oransje",
        "editorMarkerNavigationInfo.background": "bla",
    })

    # ----- Oversiktslinja til høyre og minikartet -----
    u.update({
        "editorOverviewRuler.addedForeground": a(lagt_til, 0.6),
        "editorOverviewRuler.modifiedForeground": a("oransje", 0.6),
        "editorOverviewRuler.deletedForeground": a(fjernet, 0.6),
        "editorOverviewRuler.errorForeground": a("rod", 0.8),
        "editorOverviewRuler.warningForeground": a("oransje", 0.8),
        "editorOverviewRuler.infoForeground": a("bla", 0.8),
        "editorOverviewRuler.findMatchForeground": a("oransje", 0.5),
        "editorOverviewRuler.rangeHighlightForeground": a("oransje", 0.4),
        "editorOverviewRuler.selectionHighlightForeground": a("dempet", 0.6),
        "editorOverviewRuler.wordHighlightForeground": a("dempet", 0.6),
        "editorOverviewRuler.wordHighlightStrongForeground": a("dempet", 0.8),
        "editorOverviewRuler.wordHighlightTextForeground": a("dempet", 0.6),
        "editorOverviewRuler.bracketMatchForeground": "dempet",
        "editorOverviewRuler.currentContentForeground": a("gronn", 0.5),
        "editorOverviewRuler.incomingContentForeground": a("plum", 0.5),
        "editorOverviewRuler.commonContentForeground": a("dempet", 0.4),
        "editorOverviewRuler.inlineChatInserted": a(lagt_til, 0.12),
        "editorOverviewRuler.inlineChatRemoved": a(fjernet, 0.12),
        "editorMinimap.inlineChatInserted": a(lagt_til, 0.12),
        "minimap.errorHighlight": a("rod", 0.7),
        "minimap.warningHighlight": a("oransje", 0.7),
        "minimap.findMatchHighlight": a("oransje", 0.6),
        "minimap.selectionHighlight": "markering",
        "minimapGutter.addedBackground": lagt_til,
        "minimapGutter.modifiedBackground": "oransje",
        "minimapGutter.deletedBackground": fjernet,
    })

    # ----- Diff og innebygde forslag (grønt = lagt til, rødt = fjernet) -----
    u.update({
        "diffEditor.insertedTextBackground": a(lagt_til, 0.22),
        "diffEditor.insertedLineBackground": a(lagt_til, 0.12),
        "diffEditor.removedTextBackground": a("diff_fjernet", 0.22),
        "diffEditor.removedLineBackground": a("diff_fjernet", 0.12),
        "diffEditorGutter.insertedLineBackground": a(lagt_til, 0.25),
        "diffEditorGutter.removedLineBackground": a("diff_fjernet", 0.3),
        "diffEditorOverview.insertedForeground": a(lagt_til, 0.6),
        "diffEditorOverview.removedForeground": a(fjernet, 0.6),
        "diffEditor.diagonalFill": a("dempet", 0.2),
        "diffEditor.unchangedCodeBackground": a("dempet", 0.08),
        "diffEditor.unchangedRegionBackground": "ramme",
        "diffEditor.unchangedRegionForeground": "dempet",
        "diffEditor.move.border": a("dempet", 0.6),
        "diffEditor.moveActive.border": "oransje",
        "diffEditor.border": INGEN,
        "multiDiffEditor.headerBackground": "ramme",
        "multiDiffEditor.background": "bakgrunn",
        "multiDiffEditor.border": INGEN,
        "inlineChatDiff.inserted": a(lagt_til, 0.12),
        "inlineChatDiff.removed": a("diff_fjernet", 0.12),
        "inlineEdit.modifiedBackground": a(lagt_til, 0.06),
        "inlineEdit.modifiedBorder": a(lagt_til, 0.25),
        "inlineEdit.modifiedChangedLineBackground": a(lagt_til, 0.14),
        "inlineEdit.modifiedChangedTextBackground": a(lagt_til, 0.22),
        "inlineEdit.originalBackground": a("diff_fjernet", 0.06),
        "inlineEdit.originalBorder": a("diff_fjernet", 0.25),
        "inlineEdit.originalChangedLineBackground": a("diff_fjernet", 0.14),
        "inlineEdit.originalChangedTextBackground": a("diff_fjernet", 0.22),
        "inlineEdit.tabWillAcceptModifiedBorder": a(lagt_til, 0.25),
        "inlineEdit.tabWillAcceptOriginalBorder": a("diff_fjernet", 0.25),
        "inlineEdit.gutterIndicator.background": a("dempet", 0.12),
    })

    # ----- Flettekonflikter (vår versjon grønn, innkommende plum) -----
    u.update({
        "merge.currentHeaderBackground": a("gronn", 0.45),
        "merge.currentContentBackground": a("gronn", 0.18),
        "merge.incomingHeaderBackground": a("plum", 0.45),
        "merge.incomingContentBackground": a("plum", 0.18),
        "merge.commonHeaderBackground": a("dempet", 0.4),
        "merge.commonContentBackground": a("dempet", 0.16),
        "merge.border": INGEN,
        "mergeEditor.change.background": a(lagt_til, 0.18),
        "mergeEditor.change.word.background": a(lagt_til, 0.32),
        "mergeEditor.changeBase.background": a("diff_fjernet", 0.18),
        "mergeEditor.changeBase.word.background": a("diff_fjernet", 0.32),
        "mergeEditor.conflict.input1.background": a("gronn", 0.18),
        "mergeEditor.conflict.input2.background": a("plum", 0.18),
        "mergeEditor.conflict.unhandledFocused.border": "oransje",
        "mergeEditor.conflict.unhandledUnfocused.border": a("oransje", 0.5),
        "mergeEditor.conflict.handledFocused.border": a("gronn", 0.8),
        "mergeEditor.conflict.handledUnfocused.border": a("gronn", 0.4),
        "mergeEditor.conflict.unhandled.minimapOverViewRuler": "oransje",
        "mergeEditor.conflict.handled.minimapOverViewRuler": "gronn",
        "mergeEditor.conflictingLines.background": a("oransje", 0.25),
    })

    # ----- Peek-visning (Alt+F12, referanser) -----
    u.update({
        "peekView.border": "oransje",
        "peekViewEditor.background": "ramme",
        "peekViewEditorGutter.background": "ramme",
        "peekViewEditorStickyScroll.background": "ramme",
        "peekViewEditorStickyScrollGutter.background": "ramme",
        "peekViewEditor.matchHighlightBackground": a("oransje", 0.35),
        "peekViewResult.background": "widget",
        "peekViewResult.fileForeground": "tekst",
        "peekViewResult.lineForeground": "dempet",
        "peekViewResult.selectionBackground": "markering",
        "peekViewResult.selectionForeground": "tekst",
        "peekViewResult.matchHighlightBackground": a("oransje", 0.3),
        "peekViewTitle.background": "widget",
        "peekViewTitleLabel.foreground": "tekst",
        "peekViewTitleDescription.foreground": "dempet",
    })

    # ----- Kommandopalett, menyer og tastaturmerker -----
    u.update({
        "pickerGroup.foreground": "oransje",
        "pickerGroup.border": "widgetkant",
        "quickInputTitle.background": a("tekst", 0.06),
        "menu.foreground": "tekst",
        "menu.background": "widget",
        "menu.selectionBackground": "liste_aktiv",
        "menu.selectionForeground": "tekst",
        "menu.separatorBackground": "widgetkant",
        "menu.border": "widgetkant",
        "menubar.selectionBackground": hover,
        "keybindingLabel.foreground": "tekst",
        "keybindingLabel.background": a("dempet", 0.18),
        "keybindingLabel.border": a("dempet", 0.3),
        "keybindingLabel.bottomBorder": a("dempet", 0.45),
    })

    # ----- Skjemaelementer -----
    u.update({
        "dropdown.foreground": "tekst",
        "dropdown.listBackground": "felt",
        "checkbox.foreground": "tekst",
        "checkbox.background": "felt",
        "checkbox.border": "widgetkant",
        "checkbox.selectBorder": "dempet",
        "inputOption.activeBorder": "oransje",
        "inputOption.activeBackground": a("oransje", 0.2),
        "inputOption.activeForeground": "tekst",
        "inputOption.hoverBackground": hover,
        "radio.activeBorder": "oransje",
        "radio.activeBackground": a("oransje", 0.2),
        "radio.activeForeground": "tekst",
        "radio.inactiveBorder": "widgetkant",
        "radio.inactiveHoverBackground": hover,
        "inputValidation.errorBackground": "widget",
        "inputValidation.errorBorder": "rod",
        "inputValidation.warningBackground": "widget",
        "inputValidation.warningBorder": "oransje",
        "inputValidation.infoBackground": "widget",
        "inputValidation.infoBorder": "bla",
        "button.secondaryBackground": "liste_aktiv",
        "button.secondaryForeground": "tekst",
        "button.secondaryHoverBackground": "markering",
        "button.border": INGEN,
        "button.separator": a("bakgrunn", 0.4),
        "progressBar.background": "oransje",
    })

    # ----- Lister, trær og dra-og-slipp -----
    u.update({
        "list.errorForeground": "rod",
        "list.warningForeground": "oransje",
        "list.invalidItemForeground": "oransje",
        "list.deemphasizedForeground": "inaktiv",
        "list.dropBackground": slipp,
        "list.dropBetweenBackground": "oransje",
        "listFilterWidget.noMatchesOutline": "rod",
        "listFilterWidget.outline": INGEN,
        "tree.indentGuidesStroke": "hjelpelinje_aktiv",
        "tree.inactiveIndentGuidesStroke": "hjelpelinje",
        "tree.tableColumnsBorder": "widgetkant",
        "tree.tableOddRowsBackground": a("tekst", 0.03),
        "sideBar.dropBackground": slipp,
        "editorGroup.dropBackground": slipp,
        "panelSection.dropBackground": slipp,
        "terminal.dropBackground": slipp,
        "panelSectionHeader.background": "ramme",
        "panelSection.border": INGEN,
        "panelInput.border": "widgetkant",
        "simpleFindWidget.sashBorder": "widgetkant",
    })

    # ----- Innstillinger, velkomstside, utvidelser -----
    u.update({
        "settings.headerForeground": "tekst",
        "settings.settingsHeaderHoverForeground": a("tekst", 0.7),
        "settings.modifiedItemIndicator": "oransje",
        "settings.checkboxForeground": "tekst",
        "settings.dropdownForeground": "tekst",
        "settings.headerBorder": "widgetkant",
        "settings.sashBorder": "widgetkant",
        "welcomePage.tileBackground": "widget",
        "welcomePage.tileHoverBackground": "liste_hover",
        "welcomePage.tileBorder": a("tekst", 0.1),
        "welcomePage.progress.foreground": "oransje",
        "walkthrough.stepTitle.foreground": "tekst",
        "walkThrough.embeddedEditorBackground": "ramme",
        "extensionIcon.starForeground": "oransje",
        "extensionIcon.preReleaseForeground": "gronn",
        "extensionIcon.sponsorForeground": "plum",
        "extensionIcon.verifiedForeground": "gronn",
        "extensionIcon.privateForeground": a("tekst", 0.4),
        "mcpIcon.starForeground": "oransje",
        "debugToolBar.background": "widget",
        "debugToolBar.border": "widgetkant",
    })

    # ----- Feilsøking -----
    u.update({
        "debugIcon.breakpointForeground": "rod",
        "debugIcon.breakpointDisabledForeground": "inaktiv",
        "debugIcon.breakpointUnverifiedForeground": "dempet",
        "debugIcon.breakpointCurrentStackframeForeground": "oransje",
        "debugIcon.breakpointStackframeForeground": "gronn",
        "debugIcon.startForeground": "gronn",
        "debugIcon.continueForeground": "gronn",
        "debugIcon.restartForeground": "gronn",
        "debugIcon.pauseForeground": "oransje",
        "debugIcon.stopForeground": "rod",
        "debugIcon.disconnectForeground": "rod",
        "debugIcon.stepOverForeground": "plum",
        "debugIcon.stepIntoForeground": "plum",
        "debugIcon.stepOutForeground": "plum",
        "debugIcon.stepBackForeground": "plum",
        "debugConsole.errorForeground": "rod",
        "debugConsole.warningForeground": "oransje",
        "debugConsole.infoForeground": "bla",
        "debugConsole.sourceForeground": "dempet",
        "debugConsoleInputIcon.foreground": "oransje",
        "debugTokenExpression.name": "plum",
        "debugTokenExpression.type": "plum",
        "debugTokenExpression.value": "dempet",
        "debugTokenExpression.string": "bla",
        "debugTokenExpression.number": "oransje",
        "debugTokenExpression.boolean": "oransje",
        "debugTokenExpression.error": "rod",
        "debugView.stateLabelBackground": a("dempet", 0.3),
        "debugView.stateLabelForeground": "tekst",
        "debugView.exceptionLabelBackground": "rod",
        "debugView.exceptionLabelForeground": "bakgrunn",
        "debugView.valueChangedHighlight": "oransje",
        "debugExceptionWidget.background": "widget",
        "debugExceptionWidget.border": "rod",
    })

    # ----- Tester -----
    u.update({
        "testing.iconPassed": "gronn",
        "testing.iconFailed": "rod",
        "testing.iconErrored": "rod",
        "testing.iconQueued": "oransje",
        "testing.iconUnset": "dempet",
        "testing.iconSkipped": "inaktiv",
        "testing.runAction": "gronn",
        "testing.peekBorder": "rod",
        "testing.peekHeaderBackground": a("rod", 0.1),
        "testing.message.error.lineBackground": a("rod", 0.1),
        "testing.message.error.badgeBackground": "rod",
        "testing.message.error.badgeForeground": "bakgrunn",
        "testing.message.error.badgeBorder": "rod",
        "testing.message.info.decorationForeground": "dempet",
        "testing.coveredBackground": a("gronn", 0.12),
        "testing.coveredGutterBackground": a("gronn", 0.5),
        "testing.uncoveredBackground": a("rod", 0.12),
        "testing.uncoveredGutterBackground": a("rod", 0.5),
        "testing.coverCountBadgeBackground": "dempet",
        "testing.coverCountBadgeForeground": "bakgrunn",
    })

    # ----- Jupyter-notebooks -----
    u.update({
        "notebook.cellBorderColor": "widgetkant",
        "notebook.focusedCellBorder": "oransje",
        "notebook.inactiveFocusedCellBorder": a("oransje", 0.4),
        "notebook.focusedEditorBorder": a("oransje", 0.5),
        "notebook.selectedCellBorder": "widgetkant",
        "notebook.cellToolbarSeparator": "widgetkant",
        "notebook.cellStatusBarItemHoverBackground": hover,
        "notebook.symbolHighlightBackground": a("oransje", 0.08),
        "notebook.cellInsertionIndicator": "oransje",
        "notebookStatusSuccessIcon.foreground": "gronn",
        "notebookStatusErrorIcon.foreground": "rod",
        "notebookStatusRunningIcon.foreground": "oransje",
        "notebookEditorOverviewRuler.runningCellForeground": "gronn",
        "notebookScrollbarSlider.background": a("rullefelt", 0x22 / 255),
        "notebookScrollbarSlider.hoverBackground": a("rullefelt", 0x33 / 255),
        "notebookScrollbarSlider.activeBackground": a("rullefelt", 0x44 / 255),
        "interactive.activeCodeBorder": "oransje",
        "interactive.inactiveCodeBorder": "widgetkant",
    })

    # ----- Terminalen -----
    u.update({
        "terminalCursor.background": "bakgrunn",
        "terminal.hoverHighlightBackground": a("oransje", 0.12),
        "terminal.initialHintForeground": "kommentar",
        "terminalCommandDecoration.defaultBackground": a("dempet", 0.5),
        "terminalCommandDecoration.successBackground": "gronn",
        "terminalCommandDecoration.errorBackground": "rod",
        "terminalOverviewRuler.cursorForeground": "dempet",
        "terminalOverviewRuler.findMatchForeground": a("oransje", 0.5),
        "terminalStickyScrollHover.background": "liste_hover",
        "terminalSymbolIcon.aliasForeground": "plum",
        "terminalSymbolIcon.argumentForeground": "tekst",
        "terminalSymbolIcon.flagForeground": "oransje",
        "terminalSymbolIcon.methodForeground": "gronn",
        "terminalSymbolIcon.optionForeground": "oransje",
        "terminalSymbolIcon.optionValueForeground": "bla",
    })

    # ----- Ikoner for symboler (disposisjon, forslag) i samme farger som koden -----
    for navn, farge in {
        "class": "plum", "interface": "plum", "struct": "plum", "enumerator": "plum", "typeParameter": "plum",
        "constructor": "gronn", "function": "gronn", "method": "gronn",
        "constant": "oransje", "boolean": "oransje", "number": "oransje", "null": "oransje",
        "enumeratorMember": "oransje", "event": "oransje", "unit": "oransje", "color": "oransje",
        "string": "bla", "key": "plum", "keyword": "rust", "operator": "tekst",
        "variable": "tekst", "field": "tekst", "property": "tekst", "object": "tekst", "array": "tekst",
        "module": "tekst", "namespace": "tekst", "package": "tekst", "file": "tekst", "folder": "tekst",
        "reference": "tekst", "snippet": "dempet", "text": "dempet",
    }.items():
        u[f"symbolIcon.{navn}Foreground"] = farge

    # ----- Git -----
    u.update({
        "gitDecoration.renamedResourceForeground": "gronn",
        "gitDecoration.stageModifiedResourceForeground": "oransje",
        "gitDecoration.stageDeletedResourceForeground": "rod",
        "gitDecoration.conflictingResourceForeground": "plum",
        "gitDecoration.submoduleResourceForeground": "plum",
        "scmGraph.foreground1": "oransje",
        "scmGraph.foreground2": "rod",
        "scmGraph.foreground3": "gronn",
        "scmGraph.foreground4": "plum",
        "scmGraph.foreground5": "bla",
        "scmGraph.historyItemRefColor": "oransje",
        "scmGraph.historyItemRemoteRefColor": "plum",
        "scmGraph.historyItemBaseRefColor": "gronn",
        "scmGraph.historyItemHoverAdditionsForeground": "gronn",
        "scmGraph.historyItemHoverDeletionsForeground": "rod",
    })

    # ----- Diagrammer, Markdown-varsler og chat -----
    u.update({
        "charts.foreground": "tekst",
        "charts.lines": "dempet",
        "charts.red": "rod",
        "charts.orange": "oransje",
        "charts.yellow": "oransje",
        "charts.green": "gronn",
        "charts.blue": "bla",
        "charts.purple": "plum",
        "chart.line": "oransje",
        "chart.axis": a("dempet", 0.4),
        "chart.guide": a("dempet", 0.2),
        "agentsWindowGraphic.orange": "oransje",
        "markdownAlert.note.foreground": "bla",
        "markdownAlert.tip.foreground": "gronn",
        "markdownAlert.important.foreground": "plum",
        "markdownAlert.warning.foreground": "oransje",
        "markdownAlert.caution.foreground": "rod",
        "chat.requestBorder": a("tekst", 0.1),
        "chat.requestCodeBorder": a("oransje", 0.5),
        "chat.slashCommandBackground": a("plum", 0.2),
        "chat.slashCommandForeground": "plum",
        "chat.avatarBackground": "ramme",
        "chat.avatarForeground": "tekst",
        "chat.editedFileForeground": "oransje",
        "chat.linesAddedForeground": "gronn",
        "chat.linesRemovedForeground": "rod",
        "chat.checkpointSeparator": "widgetkant",
        "chat.mcpCompatibilityWarningForeground": "oransje",
        "chat.thinkingShimmer": "tekst",
        "chat.workingProgressStableIconForeground": "oransje",
        "chat.workingProgressInsidersIconForeground": "oransje",
        "chat.sessionStateIndicator.needsInputBorder": "oransje",
        "chat.sessionStateIndicator.unvisitedBorder": "gronn",
        "chat.fusionBadgeGradientStart": "oransje",
        "chat.fusionBadgeGradientEnd": "rod",
        "chat.inputWorkingBorderColor1": "oransje",
        "chat.inputWorkingBorderColor2": "rod",
        "chat.inputWorkingBorderColor3": "gronn",
    })
    return u


# ---------- koden (TextMate) ----------

# Miljøtypene i LaTeX-grammatikken. Brukes for å skille \\begin fra kommandoer
# som \\color{...}, som grammatikken gir samme scope når de står i klammer.
# VS Code rangerer regler etter lengden på scope-navnene, så de fulle navnene trengs.
MILJOER = ["general", "math", "list", "tabular", "frame", "latex.tikz"]


def tokens(p):
    """Regler for fargelegging av kode: (navn, scopes, farge, stil).

    Farge None betyr at fargen ikke endres, stil None at stilen ikke endres
    og "" at teksten verken er fet eller kursiv. Når flere regler treffer,
    vinner den mest spesifikke, uansett rekkefølge.
    """
    return [
        # ===== Felles for alle språk =====
        ("Standardtekst", ["source", "variable", "variable.parameter", "meta.function-call.arguments", "keyword.operator", "entity.name.namespace", "entity.name.module", "entity.name.label", "variable.other.readwrite", "variable.other.property", "variable.other.object"], "tekst", None),
        ("Operatorer (ikke fet)", ["keyword.operator", "keyword.operator.assignment", "keyword.operator.arithmetic", "keyword.operator.comparison", "keyword.operator.bitwise", "keyword.operator.pipe", "keyword.operator.redirect", "keyword.operator.expansion"], "tekst", ""),
        ("Kommentarer", ["comment", "punctuation.definition.comment", "string.quoted.docstring.multi.python", "string.quoted.docstring", "string.quoted.docstring punctuation.definition.string"], "kommentar", "italic"),
        ("1 Rust: nøkkelord", ["keyword", "storage.type", "storage.modifier", "keyword.other", "keyword.operator.new", "keyword.control.import", "keyword.control.import.python", "storage.type.function.lambda.python", "storage.type.function.async.python"], "rust", ""),
        ("1 Rust, fet: kontrollord og logiske ord", ["keyword.control", "keyword.control.flow", "keyword.control.flow.python", "keyword.control.conditional", "keyword.control.loop", "keyword.control.return", "keyword.control.trycatch", "keyword.control.exception", "keyword.operator.logical", "keyword.operator.logical.python", "keyword.operator.word", "keyword.operator.expression", "keyword.operator.instanceof", "keyword.operator.typeof", "storage.type.function.python", "storage.type.class.python"], "rust", "bold"),
        ("2 Oransje: tall og konstanter", ["constant.numeric", "constant.language", "constant.other", "support.constant", "variable.other.constant", "variable.other.enummember", "constant.other.color", "keyword.other.unit"], "oransje", None),
        ("Python: navn med store bokstaver er vanlige variabler (M, G, GRENSE)", ["constant.other.caps", "constant.other.caps.python", "variable.other.constant"], "tekst", ""),
        ("2 Oransje: prefiks og suffiks på tall (0x, 1j)", ["storage.type.number", "storage.type.imaginary.number", "storage.type.number.python", "storage.type.imaginary.number.python"], "oransje", ""),
        ("3 Blå: strenger", ["string", "punctuation.definition.string", "string.quoted", "string.interpolated", "string.template", "string.regexp", "string.other"], "bla", None),
        ("3 Blå: strengprefiks (f, r, b)", ["storage.type.string", "storage.type.string.python"], "bla", ""),
        ("4 Grønn: funksjoner", ["entity.name.function", "support.function", "support.function.builtin", "meta.function-call.generic", "support.function.magic", "variable.function", "entity.name.function.member", "entity.name.command"], "gronn", None),
        ("5 Plum: klasser, typer, dekoratorer, self", ["entity.name.type", "entity.name.type.class", "entity.name.class", "entity.other.inherited-class", "support.type", "support.class", "entity.name.function.decorator", "meta.function.decorator", "punctuation.definition.decorator", "variable.language.special.self", "variable.parameter.function.language.special.self", "variable.language.special.cls", "variable.parameter.function.language.special.cls", "variable.language.this", "variable.language.self", "support.variable.magic", "constant.character.escape", "constant.character.format.placeholder", "meta.fstring.python constant.character.format.placeholder", "entity.name.type.parameter", "storage.type.annotation", "support.type.primitive"], "plum", None),
        ("5 Plum: formatspesifikasjon i f-strenger (:.2f, !r)", ["storage.type.format", "storage.type.format.python"], "plum", ""),
        ("5 Plum: spesialtegn i regulære uttrykk", ["string.regexp keyword.operator", "string.regexp keyword.control", "string.regexp support.other", "string.regexp constant.other.set", "string.regexp constant.other.character-class", "string.regexp constant.character.character-class", "string.regexp punctuation.character.set", "string.regexp punctuation.parenthesis", "string.regexp punctuation.definition.group", "string.regexp punctuation.definition.character-class", "string.regexp keyword.operator.quantifier", "string.regexp keyword.operator.disjunction", "string.regexp support.other.escape.special", "string.regexp support.other.match"], "plum", ""),
        ("Ugyldig", ["invalid", "invalid.illegal"], "rod", None),
        ("Utdatert", ["invalid.deprecated"], "rod", "strikethrough"),

        # ===== Markdown =====
        ("Markdown: overskrifter (fet tekst)", ["markup.heading", "entity.name.section", "markup.heading.setext"], "tekst", "bold"),
        ("Markdown: # foran overskrifter (rød)", ["punctuation.definition.heading.markdown"], "rod", "bold"),
        ("Markdown utheving", ["markup.bold"], None, "bold"),
        ("Markdown kursiv", ["markup.italic"], None, "italic"),
        ("Markdown overstreking", ["markup.strikethrough"], None, "strikethrough"),
        ("Markdown understreking", ["markup.underline"], None, "underline"),
        ("Markdown: kode i teksten (blå)", ["markup.inline.raw", "markup.inline.raw.string.markdown", "markup.raw", "markup.raw.block.markdown"], "bla", None),
        ("Markdown: kodeblokker følger språket inni", ["markup.fenced_code.block.markdown", "meta.embedded.block"], "tekst", None),
        ("Markdown: ``` og språknavn (grå)", ["punctuation.definition.markdown", "fenced_code.block.language", "fenced_code.block.language.markdown", "fenced_code.block.language.attributes.markdown", "punctuation.definition.raw.markdown"], "dempet", ""),
        ("Markdown: lenker (rød, som i PDF-en)", ["markup.underline.link", "string.other.link", "meta.link.inline.markdown", "meta.image.inline.markdown", "meta.link.reference.markdown", "constant.other.reference.link.markdown"], "rod", ""),
        ("Markdown: klammer rundt lenker (grå)", ["punctuation.definition.link.title.begin.markdown", "punctuation.definition.link.title.end.markdown", "punctuation.definition.link.description.begin.markdown", "punctuation.definition.link.description.end.markdown", "punctuation.definition.metadata.markdown"], "dempet", ""),
        ("Markdown: listetegn (rust)", ["punctuation.definition.list.begin.markdown", "beginning.punctuation.definition.list.markdown"], "rust", None),
        ("Markdown: sitat (grå, kursiv)", ["markup.quote"], "dempet", "italic"),
        ("Markdown: skillelinjer og tabellstreker (grå)", ["meta.separator.markdown", "punctuation.definition.table.markdown", "punctuation.separator.table.markdown", "punctuation.definition.strikethrough.markdown", "punctuation.definition.bold.markdown", "punctuation.definition.italic.markdown"], "dempet", None),
        ("Markdown: matematikk (blå, kommandoer nøytrale)", ["meta.embedded.math.markdown", "markup.math.inline.markdown", "markup.math.block.markdown", "meta.function.math.tex"], "bla", None),
        ("Markdown: matematikk, kommandoer som \\frac (nøytral)", ["entity.name.function.math.tex", "punctuation.definition.function.math.tex", "storage.type.function.math.tex"], "tekst", ""),
        ("Markdown: matematikk, operatorer (nøytral)", ["punctuation.math.operator.latex", "punctuation.line.separator.math.tex", "line.separator.math.tex"], "tekst", None),
        ("Markdown: matematikk, $ og klammer (grå)", ["punctuation.definition.math.begin.markdown", "punctuation.definition.math.end.markdown", "punctuation.math.begin.bracket.curly", "punctuation.math.end.bracket.curly", "punctuation.math.begin.bracket.round", "punctuation.math.end.bracket.round", "punctuation.definition.arguments.begin.math.tex", "punctuation.definition.arguments.end.math.tex"], "dempet", None),

        # ===== LaTeX =====
        ("LaTeX: struktur (rust)", ["keyword.control.preamble.latex", "keyword.control.include.latex", "storage.type.function.latex", "keyword.other.item.latex", "storage.type.function.tex", "keyword.control.tex", "keyword.control.catcode.tex"], "rust", ""),
        ("LaTeX: \\begin og \\end (rust, fet)", ["support.function.be.latex"], "rust", "bold"),
        ("LaTeX: seksjonskommandoer (rød, fet)", ["support.function.section.latex"], "rod", "bold"),
        ("LaTeX: linjeskift og tabellceller (nøytral)", ["keyword.control.newline.tex", "keyword.control.equation.newline.latex", "keyword.control.table.cell.latex", "keyword.control.table.newline.latex", "keyword.control.equation.align.latex", "keyword.control.layout.latex"], "tekst", ""),
        ("LaTeX: seksjonstitler", ["entity.name.section.latex"], "tekst", "bold"),
        ("LaTeX: matematikk, variabler (blå)", ["support.class.math.block.tex", "support.class.math.block.environment.latex", "meta.math.block.tex", "meta.math.block.latex"], "bla", None),
        ("LaTeX: greske bokstaver og symboler (plum)", ["constant.character.math.tex"], "plum", None),
        ("LaTeX: tall (oransje)", ["constant.numeric.math.tex"], "oransje", None),
        ("LaTeX: vanlig tekst inne i matte (\\text{})", ["meta.text.normal.tex"], "tekst", None),
        ("LaTeX: miljønavn (grønn, fet)", ["variable.parameter.function.latex"], "gronn", "bold"),
        ("LaTeX: navn på nye kommandoer (grønn)", ["meta.parameter.newcommand.latex support.function.general.latex", "entity.name.function.latex", "entity.name.function.tex"], "gronn", ""),
        ("LaTeX: øvrige kommandoer (nøytral)", ["support.function.general.latex", "support.function.general.tex", "support.function.emph.latex", "support.function.textbf.latex", "support.function.textit.latex", "support.function.texttt.latex", "support.function.url.latex", "support.function.footnote.latex", "support.function.marginpar.latex", "support.function.verb.latex", "keyword.control.ref.latex", "keyword.control.label.latex", "keyword.control.cite.latex", "constant.other.general.math.tex", "constant.other.math.tex", "support.function.textcolor.latex", "support.function.textsubscript.latex", "support.function.textsuperscript.latex", "support.function.textsc.latex", "support.function.textsf.latex", "support.function.textrm.latex", "support.function.underline.latex"], "tekst", ""),
        ("LaTeX: kommandoer i klammer og \\newcommand som ikke er miljøer (nøytral)", ["meta.group.braces.latex support.function.be.latex", "meta.parameter.newcommand.latex support.function.be.latex", "meta.group.braces.latex variable.parameter.function.latex", "meta.parameter.newcommand.latex variable.parameter.function.latex"], "tekst", ""),
        ("LaTeX: \\begin og \\end inne i klammer (rust, fet)", [f"{f} meta.function.environment.{m}.latex support.function.be.latex".replace(".latex.tikz.latex", ".latex.tikz") for f in ("meta.group.braces.latex", "meta.parameter.newcommand.latex") for m in MILJOER], "rust", "bold"),
        ("LaTeX: miljønavn inne i klammer (grønn, fet)", [f"{f} meta.function.environment.{m}.latex variable.parameter.function.latex".replace(".latex.tikz.latex", ".latex.tikz") for f in ("meta.group.braces.latex", "meta.parameter.newcommand.latex") for m in MILJOER], "gronn", "bold"),
        ("LaTeX: navn og nøkler (nøytral)", ["variable.parameter.definition.label.latex", "constant.other.reference.label.latex", "constant.other.reference.citation.latex", "support.class.latex", "constant.other.citation.latex"], "tekst", ""),
        ("LaTeX: operatorer (nøytral)", ["punctuation.math.operator.tex"], "tekst", None),
        ("LaTeX: fet og kursiv tekst", ["markup.bold.textbf.latex"], "tekst", "bold"),
        ("LaTeX: kursiv tekst", ["markup.italic.emph.latex", "markup.italic.textit.latex"], "tekst", "italic"),
        ("LaTeX: klammer, parenteser og $ (grå)", [
            "punctuation.definition.arguments.begin.latex", "punctuation.definition.arguments.end.latex",
            "punctuation.definition.arguments.begin.tex", "punctuation.definition.arguments.end.tex",
            "punctuation.definition.arguments.optional.begin.latex", "punctuation.definition.arguments.optional.end.latex",
            "punctuation.group.begin.latex", "punctuation.group.end.latex", "punctuation.group.begin.tex", "punctuation.group.end.tex",
            "punctuation.definition.brackets.tex",
            "punctuation.definition.begin.latex", "punctuation.definition.end.latex",
            "punctuation.math.begin.bracket.curly.tex", "punctuation.math.end.bracket.curly.tex",
            "punctuation.math.begin.bracket.round.tex", "punctuation.math.end.bracket.round.tex",
            "punctuation.math.bracket.pair.tex", "punctuation.math.bracket.pair.big.tex",
            "punctuation.definition.emph.begin.latex", "punctuation.definition.emph.end.latex",
            "punctuation.definition.textbf.begin.latex", "punctuation.definition.textbf.end.latex",
            "punctuation.definition.textit.begin.latex", "punctuation.definition.textit.end.latex",
            "punctuation.definition.texttt.begin.latex", "punctuation.definition.texttt.end.latex",
            "punctuation.definition.footnote.begin.latex", "punctuation.definition.footnote.end.latex",
            "punctuation.definition.marginpar.begin.latex", "punctuation.definition.marginpar.end.latex",
            "punctuation.definition.string.begin.tex", "punctuation.definition.string.end.tex",
            "punctuation.definition.string.begin.latex", "punctuation.definition.string.end.latex",
            "punctuation.section.embedded.begin.math.tex", "punctuation.section.embedded.end.math.tex",
            "punctuation.definition.verb.latex",
        ], "dempet", ""),
        ("LaTeX: kommentarer", ["comment.line.percentage.tex", "comment.line.percentage.latex", "punctuation.definition.comment.tex", "punctuation.definition.comment.latex", "comment.block.preprocessor.tex", "comment.line.percentage.directive.texshop.tex"], "kommentar", "italic"),
        ("LaTeX: henvisninger og lenker (rød, som i PDF-en)", ["keyword.control.ref.latex", "keyword.control.cite.latex", "constant.other.reference.label.latex", "constant.other.reference.citation.latex", "support.function.url.latex", "markup.underline.link.latex", "keyword.control.ref.latex punctuation.definition.keyword.latex", "keyword.control.cite.latex punctuation.definition.keyword.latex", "support.function.url.latex punctuation.definition.function.latex"], "rod", ""),
        ("LaTeX: siunitx og mhchem, kommandonavn (nøytral)", ["support.function.siunitx.latex", "support.function.mhchem.latex"], "tekst", ""),
        ("LaTeX: enheter i siunitx (tekst, også i matte)", ["meta.unit.siunitx.latex"], "tekst", ""),
        ("LaTeX: kjemiske formler i \\ce (blå, som matte)", ["meta.chemistry.mhchem.latex"], "bla", ""),
        ("LaTeX: filstier (blå, som strenger)", ["string.unquoted.path.latex", "meta.include.latex"], "bla", ""),
        ("LaTeX: pakkeopsjoner (tekst, ikke grønn og fet)", ["meta.parameter.optional.latex variable.parameter.function.latex"], "tekst", ""),
        ("LaTeX: tegnekommandoer i tikzpicture (grønn)", ["meta.function.environment.latex.tikz support.function.general.latex", "meta.function.environment.latex.tikz support.function.general.tex"], "gronn", ""),

        # ===== BibTeX =====
        ("BibTeX: posttype (@book)", ["keyword.other.entry-type.bibtex", "punctuation.definition.keyword.bibtex"], "rust", "bold"),
        ("BibTeX: nøkkel som brukes i \\cite (nøytral, fet)", ["entity.name.type.entry-key.bibtex"], "tekst", "bold"),
        ("BibTeX: feltnavn (plum)", ["support.function.key.bibtex", "string.unquoted.key.bibtex"], "plum", ""),
        ("BibTeX: verdier (nøytral) og klammer (grå)", ["meta.key-assignment.bibtex"], "tekst", None),
        ("BibTeX: klammer rundt verdier (grå)", ["meta.key-assignment.bibtex punctuation.definition.string.begin.bibtex", "meta.key-assignment.bibtex punctuation.definition.string.end.bibtex", "punctuation.section.entry.begin.bibtex", "punctuation.section.entry.end.bibtex", "punctuation.definition.group.begin.bibtex", "punctuation.definition.group.end.bibtex"], "dempet", None),

        # ===== Data og konfigurasjon (JSON, YAML, TOML, INI) =====
        ("Generelt: nøkler og attributter (plum)", ["support.type.property-name", "meta.object-literal.key", "entity.other.attribute-name", "meta.mapping.key string", "support.type.property-name.toml", "keyword.other.definition.ini", "entity.name.section.group-title.ini"], "plum", ""),
        ("Generelt: tagger i HTML og XML, og typevelgere i CSS (rust, struktur)", ["entity.name.tag"], "rust", ""),
        ("Generelt: < og > rundt tagger (grå, som klammer)", ["punctuation.definition.tag"], "dempet", ""),
        ("YAML: nøkler (plum, selv om grammatikken kaller dem tagger)", ["entity.name.tag.yaml"], "plum", ""),
        ("Generelt: innebygde typer (int, double, char) er typer (plum)", ["storage.type.built-in", "storage.type.built-in.primitive", "storage.type.primitive", "support.type.primitive", "support.type.builtin"], "plum", ""),
        ("Generelt: super og andre språkvariabler (plum)", ["variable.language.super", "variable.language.makefile", "constant.character.entity", "punctuation.definition.entity.html"], "plum", ""),
        ("Markdown: skillelinjer rundt front matter (grå)", ["punctuation.definition.begin.frontmatter", "punctuation.definition.end.frontmatter"], "dempet", ""),
        ("YAML: ankere og alias (plum)", ["variable.other.anchor", "variable.other.alias", "punctuation.definition.anchor", "punctuation.definition.alias"], "plum", ""),
        ("JSON og YAML: strukturtegn (grå)", ["punctuation.support.type.property-name", "punctuation.definition.dictionary", "punctuation.definition.array", "punctuation.definition.mapping", "punctuation.definition.sequence"], "dempet", None),

        # ===== Diff og git =====
        ("Diff: lagt til (grønn)", ["markup.inserted", "punctuation.definition.inserted", "meta.diff.header.to-file", "punctuation.definition.to-file.diff"], "gronn", None),
        ("Diff: fjernet (rød)", ["markup.deleted", "punctuation.definition.deleted", "meta.diff.header.from-file", "punctuation.definition.from-file.diff"], "rod", None),
        ("Diff: endret (oransje)", ["markup.changed", "punctuation.definition.changed"], "oransje", None),
        ("Diff: linjenummer og overskrifter (plum)", ["meta.diff.range", "meta.toc-list.line-number.diff", "punctuation.definition.range.diff"], "plum", None),
        ("Diff: git-overskrift (fet)", ["meta.diff.header.git", "meta.diff.header.command", "meta.diff.index.git", "meta.diff.index"], "dempet", "bold"),
        ("Git commit: emnelinje", ["meta.scope.subject.git-commit"], "tekst", "bold"),
        ("Git commit: filer i kommentaren", ["comment markup.inserted.git-commit", "comment markup.deleted.git-commit", "comment markup.changed.git-commit"], None, "italic"),

        # ===== Skall =====
        ("Skall: variabler ($HOME)", ["variable.other.normal.shell", "variable.other.positional.shell", "variable.parameter.positional.shell", "variable.other.special.shell", "punctuation.definition.variable.shell"], "plum", ""),
        ("Skall: shebang", ["meta.shebang", "comment.line.shebang"], "kommentar", "italic"),

        # ===== Logger (Output-panelet) =====
        ("Logg: feil (rød)", ["token.error-token", "log.error"], "rod", None),
        ("Logg: advarsel (oransje)", ["token.warn-token", "log.warning"], "oransje", None),
        ("Logg: info (grønn)", ["token.info-token", "log.info"], "gronn", None),
        ("Logg: debug (grå)", ["token.debug-token", "log.debug"], "kommentar", None),
    ]


def semantiske(p):
    """Semantisk utheving (Pylance og andre språkservere): type -> palettnavn og stil."""
    return {
        "class": "plum",
        "class.builtin": "plum",
        "type": "plum",
        "typeParameter": "plum",
        "enum": "plum",
        "interface": "plum",
        "struct": "plum",
        "decorator": "plum",
        "selfParameter": "plum",
        "clsParameter": "plum",
        "function": "gronn",
        "function.builtin": "gronn",
        "method": "gronn",
        "macro": "gronn",
        "namespace": "tekst",
        "module": "tekst",
        "variable": "tekst",
        # Pylance regner alle navn med store bokstaver som konstanter, også M, G og F i fysikkode.
        # De får tekstfarge som andre variabler; oransje er for tall, True, False og None.
        "variable.readonly": "tekst",
        "variable.readonly.builtin": "tekst",
        "enumMember": "oransje",
        "parameter": "tekst",
        "property": "tekst",
        "property.readonly": "tekst",
        "keyword": "rust",
        "number": "oransje",
        "string": "bla",
        "regexp": "bla",
        "operator": "tekst",
        "comment": ("kommentar", "italic"),
        "*.deprecated": {"strikethrough": True},
    }


# ---------- bygging ----------

def lag_tema(navn, p):
    colors = {k: los(p, v) for k, v in ui(p).items()}
    token_colors = []
    for tnavn, scopes, farge, stil in tokens(p):
        settings = {}
        if farge is not None:
            settings["foreground"] = los(p, farge)
        if stil is not None:
            settings["fontStyle"] = stil
        token_colors.append({"name": tnavn, "scope": scopes, "settings": settings})
    semantic = {}
    for k, v in semantiske(p).items():
        if isinstance(v, dict):
            semantic[k] = v
        elif isinstance(v, tuple):
            semantic[k] = {"foreground": los(p, v[0]), v[1]: True}
        else:
            semantic[k] = los(p, v)
    return {
        "$schema": "vscode://schemas/color-theme",
        "name": navn,
        "type": p["type"],
        "semanticHighlighting": True,
        "colors": colors,
        "tokenColors": token_colors,
        "semanticTokenColors": semantic,
    }


def lag_iterm(p):
    i = p["iterm"]
    ut = {}

    def farge(v):
        h, alfa = (v if isinstance(v, tuple) else (v, 1.0))
        r, g, b = hex_til_rgb(h)
        return {"Alpha Component": float(alfa), "Blue Component": b / 255, "Color Space": "sRGB",
                "Green Component": g / 255, "Red Component": r / 255}

    for n, v in enumerate(i["ansi"]):
        ut[f"Ansi {n} Color"] = farge(v)
    for k, v in i.items():
        if k != "ansi":
            ut[k] = farge(v)
    return dict(sorted(ut.items()))


ITERM = HER.parent.parent / "iterm2" / "farger"


def kontrast(f1, f2):
    """WCAG-kontrast mellom to hex-farger (1 til 21)."""
    def lum(h):
        c = [x / 255 for x in hex_til_rgb(h)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    a_, b_ = sorted([lum(f1), lum(f2)], reverse=True)
    return (a_ + 0.05) / (b_ + 0.05)


def sjekk(navn, p):
    print(f"\n{navn}: kontrast mot editorbakgrunnen {p['bakgrunn']} (minst 4,5 for vanlig tekst, 3 for fet)")
    for rolle in ["tekst", "rod", "rust", "oransje", "gronn", "bla", "plum", "dempet", "kommentar", "linjenr", "inaktiv"]:
        k = round(kontrast(p[rolle], p["bakgrunn"]), 1)
        merk = "" if k >= 4.5 else ("  (bare fet/stor tekst)" if k >= 3 else "  (lav)")
        print(f"  {rolle:10s} {p[rolle]}  {k:4.1f}".replace(".", ",") + merk)


def lag_svg():
    """palett.svg: malene, Høstlys og Høstkveld under hverandre."""
    malene = ["#781414", "#b85c00", "#4a6b12", "#1e608c", "#6e3278"]
    rader = [("Lualatex-malene", "#ffffff", "#282828", malene, [None, None, None, None, None]),
             ("Høstlys", HOSTLYS["bakgrunn"], HOSTLYS["tekst"], [HOSTLYS[n] for n in FARGER], FARGER),
             ("Høstkveld", HOSTKVELD["bakgrunn"], HOSTKVELD["tekst"], [HOSTKVELD[n] for n in FARGER], FARGER)]
    navn = {"rod": "rød", "rust": "rust", "oransje": "oransje", "gronn": "grønn", "bla": "blå", "plum": "plum"}
    b, h, gap, x0 = 96, 96, 12, 170
    bredde = x0 + 6 * (b + gap) + 8
    y, deler = 12, []
    for tittel, bg, fg, farger, roller in rader:
        hoyde = h + 64
        deler.append(f'<rect x="8" y="{y}" width="{bredde - 16}" height="{hoyde}" rx="14" fill="{bg}" stroke="#d8d2bf"/>')
        deler.append(f'<text x="26" y="{y + hoyde / 2 + 6}" font-family="Helvetica,Arial,sans-serif" font-size="17" font-weight="600" fill="{fg}">{tittel}</text>')
        if len(farger) == 5:  # malene har ingen rust; plassen står tom
            plasser = [x0] + [x0 + (i + 2) * (b + gap) for i in range(4)]
        else:
            plasser = [x0 + i * (b + gap) for i in range(6)]
        for x, f, r in zip(plasser, farger, roller):
            deler.append(f'<rect x="{x}" y="{y + 14}" width="{b}" height="{h}" rx="10" fill="{f}"/>')
            etikett = f"{navn[r]} " if r else ""
            deler.append(f'<text x="{x + b / 2}" y="{y + h + 34}" text-anchor="middle" font-family="Menlo,monospace" font-size="11" fill="{fg}" opacity="0.75">{etikett}{f.upper()}</text>')
        y += hoyde + 14
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{bredde}" height="{y}" viewBox="0 0 {bredde} {y}">' + "".join(deler) + "</svg>\n"
    (HER / "palett.svg").write_text(svg, encoding="utf-8")


def main():
    (HER / "themes").mkdir(exist_ok=True)
    ITERM.mkdir(parents=True, exist_ok=True)
    for navn, fil, p in [("Høstlys", "hostlys", HOSTLYS), ("Høstkveld", "hostkveld", HOSTKVELD)]:
        tema = lag_tema(navn, p)
        (HER / "themes" / f"{fil}-color-theme.json").write_text(json.dumps(tema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        with open(ITERM / f"{navn}.itermcolors", "wb") as f:
            plistlib.dump(lag_iterm(p), f)
        print(f"OK: {navn} ({len(tema['colors'])} farger, {len(tema['tokenColors'])} kodefarger)")
        if "--sjekk" in sys.argv:
            sjekk(navn, p)
    lag_svg()


if __name__ == "__main__":
    main()
