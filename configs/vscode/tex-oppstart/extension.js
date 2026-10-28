// Åpner main.tex og LaTeX Workshops PDF-visning til høyre når en mappe
// med main.tex i roten åpnes. Gjør ingenting med det som allerede er åpent.
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');

const vent = (ms) => new Promise((r) => setTimeout(r, ms));

function aapneFaner() {
  return vscode.window.tabGroups.all.flatMap((g) => g.tabs);
}

function erTexFane(tab, texSti) {
  const inp = tab.input;
  return inp instanceof vscode.TabInputText && inp.uri.fsPath === texSti;
}

function erPdfFane(tab) {
  const inp = tab.input;
  const type = inp && inp.viewType ? String(inp.viewType) : '';
  return tab.label.toLowerCase().endsWith('.pdf') || type.includes('latex-workshop');
}

async function activate() {
  const mappe = vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders[0];
  if (!mappe) return;
  const texSti = path.join(mappe.uri.fsPath, 'main.tex');
  const pdfSti = path.join(mappe.uri.fsPath, 'main.pdf');
  if (!fs.existsSync(texSti)) return;

  await vent(700); // la VS Code gjenopprette faner først

  if (!aapneFaner().some((t) => erTexFane(t, texSti))) {
    const dok = await vscode.workspace.openTextDocument(texSti);
    await vscode.window.showTextDocument(dok, { viewColumn: vscode.ViewColumn.One, preview: false });
  } else {
    const dok = await vscode.workspace.openTextDocument(texSti);
    await vscode.window.showTextDocument(dok, { preview: false });
  }

  if (fs.existsSync(pdfSti) && !aapneFaner().some(erPdfFane)) {
    await vent(300);
    await vscode.commands.executeCommand('latex-workshop.view');
    await vent(300);
    const dok = await vscode.workspace.openTextDocument(texSti);
    await vscode.window.showTextDocument(dok, { viewColumn: vscode.ViewColumn.One, preview: false });
  }
}

function deactivate() {}

module.exports = { activate, deactivate };
