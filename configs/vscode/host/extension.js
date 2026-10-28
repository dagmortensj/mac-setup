// Knapp nede til høyre i statuslinjen som bytter mellom Høstlys og Høstkveld.
// Bruker VS Codes egen kommando, som veksler mellom
// workbench.preferredLightColorTheme og workbench.preferredDarkColorTheme.
const vscode = require('vscode');

function activate(context) {
  const knapp = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 1000);
  knapp.text = '$(color-mode)';
  knapp.tooltip = 'Bytt mellom Høstlys og Høstkveld';
  knapp.command = 'workbench.action.toggleLightDarkThemes';
  knapp.show();
  context.subscriptions.push(knapp);
}

function deactivate() {}

module.exports = { activate, deactivate };
