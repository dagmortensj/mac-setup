// Knapp nede til høyre i statuslinjen, rett til venstre for temaknappen, med
// navnet på arbeidsflata som er åpen. Et klikk åpner den neste
// .code-workspace-fila i arbeidsflate.mappe i samme vindu, så med to
// arbeidsflater veksler knappen mellom dem, slik temaknappen veksler mellom
// temaene. Kommandoen «Workspace: Choose from List» i kommandopaletten viser
// alle. Tekstene brukeren ser, er på engelsk som resten av VS Code.
//
// Knappen bytter bare arbeidsflate. Profilen bytter du med tannhjulet, og
// VS Code husker den per arbeidsflate: en arbeidsflate åpnes i profilen den
// sist hadde.
const vscode = require('vscode');
const fs = require('fs');
const os = require('os');
const path = require('path');

const ENDELSE = '.code-workspace';

function mappe() {
  const sti = vscode.workspace.getConfiguration('arbeidsflate').get('mappe') || '';
  return sti.replace('${userHome}', os.homedir());
}

function aapenFil() {
  const f = vscode.workspace.workspaceFile;
  return f && f.scheme === 'file' ? f.fsPath : '';
}

function navn(fil) {
  return path.basename(fil, ENDELSE);
}

// Alle arbeidsflatefilene i mappa, sortert, med full sti.
function filer() {
  const dir = mappe();
  try {
    return fs.readdirSync(dir).filter((f) => f.endsWith(ENDELSE)).sort().map((f) => path.join(dir, f));
  } catch (e) {
    return [];
  }
}

// Den som følger etter den åpne i lista, eller den første om ingen er åpen.
// Tom streng når det ikke finnes noen annen å bytte til.
function nesteFil() {
  const alle = filer();
  const naa = aapenFil();
  const neste = alle[(alle.indexOf(naa) + 1) % (alle.length || 1)];
  return neste && neste !== naa ? neste : '';
}

async function neste() {
  const fil = nesteFil();
  if (!fil) {
    vscode.window.showInformationMessage(`Workspace: no other workspace in ${mappe()}`);
    return;
  }
  await vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(fil));
}

async function bytt() {
  const naa = aapenFil();
  const valg = filer().map((fil) => ({ label: navn(fil), description: fil === naa ? 'open now' : '', fil }));
  const valgt = await vscode.window.showQuickPick(valg, { placeHolder: 'Switch workspace' });
  if (!valgt || valgt.fil === naa) return;
  await vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(valgt.fil));
}

function activate(context) {
  // Høyrestilte knapper står etter synkende prioritet fra venstre. Temaknappen
  // (hoest.toggle) har -1000 og står ytterst; -999 er plassen rett til venstre.
  const knapp = vscode.window.createStatusBarItem('arbeidsflate.bytt', vscode.StatusBarAlignment.Right, -999);
  knapp.name = 'Workspace';
  knapp.command = 'arbeidsflate.neste';
  const til = nesteFil();
  knapp.tooltip = til ? `Switch to ${navn(til)}` : 'Workspace';
  const fil = aapenFil();
  knapp.text = `$(folder) ${fil ? navn(fil) : 'workspace'}`;
  knapp.show();
  context.subscriptions.push(
    knapp,
    vscode.commands.registerCommand('arbeidsflate.neste', neste),
    vscode.commands.registerCommand('arbeidsflate.bytt', bytt),
  );
}

function deactivate() {}

module.exports = { activate, deactivate };
