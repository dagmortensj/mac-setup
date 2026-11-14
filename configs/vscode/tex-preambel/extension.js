// Folder sammen preamblen i .tex-filer: alt fra første linje til linja før
// \begin{document} blir én sammenfoldet linje når fila åpnes. Klikk på
// linja (eller Alt+Cmd+]) for å åpne den igjen. Hver fil foldes én gang per
// vindu, så en preamble du har åpnet selv, blir stående åpen.
const vscode = require('vscode');

const vent = (ms) => new Promise((r) => setTimeout(r, ms));
const foldet = new Set();

// Linjenummeret til \begin{document}, eller -1 om fila ikke har noen
// (innholdsfiler som leses inn med \input har ingen preamble).
function dokumentstart(dok) {
  const n = Math.min(dok.lineCount, 3000);
  for (let i = 0; i < n; i++) {
    if (/^\s*\\begin\{document\}/.test(dok.lineAt(i).text)) return i;
  }
  return -1;
}

// VS Code slår sammen foldeområdene fra alle utvidelser, så dette kommer i
// tillegg til dem LaTeX Workshop gir for seksjoner og miljøer.
const foldeomraade = {
  provideFoldingRanges(dok) {
    const start = dokumentstart(dok);
    if (start < 2) return [];
    return [new vscode.FoldingRange(0, start - 1, vscode.FoldingRangeKind.Region)];
  },
};

async function fold(editor) {
  if (!editor || editor.document.languageId !== 'latex') return;
  const id = editor.document.uri.toString();
  if (foldet.has(id) || dokumentstart(editor.document) < 2) return;
  foldet.add(id);
  await vent(500); // la VS Code hente foldeområdene først
  if (vscode.window.activeTextEditor !== editor) {
    foldet.delete(id);
    return;
  }
  await vscode.commands.executeCommand('editor.fold', { selectionLines: [0], levels: 1 });
}

function activate(context) {
  context.subscriptions.push(
    vscode.languages.registerFoldingRangeProvider({ language: 'latex' }, foldeomraade),
    vscode.window.onDidChangeActiveTextEditor(fold),
    vscode.workspace.onDidCloseTextDocument((dok) => foldet.delete(dok.uri.toString())),
  );
  fold(vscode.window.activeTextEditor);
}

function deactivate() {}

module.exports = { activate, deactivate };
