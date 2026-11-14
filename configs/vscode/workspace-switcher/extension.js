// Buttons at the left end of the status bar, one for each .code-workspace
// file in workspaceSwitcher.folder. A click opens that workspace in the same
// window, and the button of the open workspace is coloured, the way the
// classroom button is while its mode is on. The buttons stand in the order
// given by workspaceSwitcher.order; workspaces not named there follow
// alphabetically. The command "Workspace: Choose from List" in the command
// palette shows them all.
//
// Before the buttons, in the very corner, stands a small cross that closes the
// workspace, the way a tab in macOS has its cross first. It leaves an empty
// window, where no button is coloured. The cross is only there while a
// workspace is open, and workspaceSwitcher.showClose turns it off in a profile
// that never leaves its workspace.
//
// The buttons switch workspace only. The profile is switched from the gear
// menu, and VS Code remembers it per workspace: a workspace opens in the
// profile it last had.
const vscode = require('vscode');
const fs = require('fs');
const os = require('os');
const path = require('path');

const EXTENSION = '.code-workspace';

function folder() {
  const dir = vscode.workspace.getConfiguration('workspaceSwitcher').get('folder') || '';
  return dir.replace('${userHome}', os.homedir());
}

function openFile() {
  const f = vscode.workspace.workspaceFile;
  return f && f.scheme === 'file' ? f.fsPath : '';
}

function nameOf(file) {
  return path.basename(file, EXTENSION);
}

// The name as it is shown, with a capital first letter like the other labels
// in the status bar. The files keep their lower-case names.
function label(file) {
  const name = nameOf(file);
  return name.charAt(0).toUpperCase() + name.slice(1);
}

// Every workspace file in the folder with its full path: first the ones named
// in workspaceSwitcher.order, in that order, then the rest alphabetically.
function files() {
  const dir = folder();
  const order = vscode.workspace.getConfiguration('workspaceSwitcher').get('order') || [];
  const rank = (name) => (order.indexOf(name) === -1 ? order.length : order.indexOf(name));
  try {
    return fs
      .readdirSync(dir)
      .filter((f) => f.endsWith(EXTENSION))
      .sort((x, y) => rank(nameOf(x)) - rank(nameOf(y)) || x.localeCompare(y))
      .map((f) => path.join(dir, f));
  } catch (e) {
    return [];
  }
}

async function open(file) {
  if (!file || file === openFile()) return;
  await vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(file));
}

async function choose() {
  const current = openFile();
  const items = files().map((file) => ({ label: label(file), description: file === current ? 'open now' : '', file }));
  const picked = await vscode.window.showQuickPick(items, { placeHolder: 'Switch workspace' });
  if (!picked || picked.file === current) return;
  await vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(picked.file));
}

async function close() {
  await vscode.commands.executeCommand('workbench.action.closeFolder');
}

function activate(context) {
  // Left-aligned items stand in descending priority from the left, so high
  // priorities put them at the edge, before the error and warning count: the
  // cross first (100000), then the workspaces (99999 and downwards).
  const current = openFile();

  const cross = vscode.window.createStatusBarItem('workspaceSwitcher.close', vscode.StatusBarAlignment.Left, 100000);
  cross.name = 'Close Workspace';
  cross.command = 'workspaceSwitcher.close';
  cross.text = '$(close)';
  cross.tooltip = 'Close workspace';
  const showClose = vscode.workspace.getConfiguration('workspaceSwitcher').get('showClose');
  if (current && showClose !== false) cross.show();
  context.subscriptions.push(cross);

  files().forEach((file, i) => {
    const name = label(file);
    const button = vscode.window.createStatusBarItem(`workspaceSwitcher.open.${nameOf(file)}`, vscode.StatusBarAlignment.Left, 99999 - i);
    button.name = `Workspace: ${name}`;
    button.text = name;
    if (file === current) {
      button.tooltip = `${name} is open`;
      button.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
    } else {
      button.tooltip = `Open ${name}`;
      button.command = { command: 'workspaceSwitcher.open', title: `Open ${name}`, arguments: [file] };
    }
    button.show();
    context.subscriptions.push(button);
  });

  context.subscriptions.push(
    vscode.commands.registerCommand('workspaceSwitcher.open', (file) => (file ? open(file) : choose())),
    vscode.commands.registerCommand('workspaceSwitcher.choose', choose),
    vscode.commands.registerCommand('workspaceSwitcher.close', close),
  );
}

function deactivate() {}

module.exports = { activate, deactivate };
