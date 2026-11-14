// A button at the left end of the status bar with the name of the open
// workspace. A click opens the next .code-workspace file in
// workspaceSwitcher.folder in the same window, so with two workspaces the
// button toggles between them, the way the theme button toggles between the
// themes. The command "Workspace: Choose from List" in the command palette
// shows them all.
//
// Before the name, in the very corner, stands a small cross that closes the
// workspace, the way a tab in macOS has its cross first. It leaves
// an empty window, where the button reads "workspace". Switching between
// workspaces and leaving them are thus two separate actions. The cross is only
// there while a workspace is open, and workspaceSwitcher.showClose turns it
// off in a profile that never leaves its workspace.
//
// The button switches workspace only. The profile is switched from the gear
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

// Every workspace file in the folder, sorted, with its full path.
function files() {
  const dir = folder();
  try {
    return fs.readdirSync(dir).filter((f) => f.endsWith(EXTENSION)).sort().map((f) => path.join(dir, f));
  } catch (e) {
    return [];
  }
}

// The one after the open workspace in the list, or the first if none is open.
// An empty string when there is no other workspace to switch to.
function nextFile() {
  const all = files();
  const current = openFile();
  const next = all[(all.indexOf(current) + 1) % (all.length || 1)];
  return next && next !== current ? next : '';
}

async function next() {
  const file = nextFile();
  if (!file) {
    vscode.window.showInformationMessage(`Workspace: no other workspace in ${folder()}`);
    return;
  }
  await vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(file));
}

async function choose() {
  const current = openFile();
  const items = files().map((file) => ({ label: nameOf(file), description: file === current ? 'open now' : '', file }));
  const picked = await vscode.window.showQuickPick(items, { placeHolder: 'Switch workspace' });
  if (!picked || picked.file === current) return;
  await vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(picked.file));
}

async function close() {
  await vscode.commands.executeCommand('workbench.action.closeFolder');
}

function activate(context) {
  // Left-aligned items stand in descending priority from the left, so high
  // priorities put the two at the edge, before the error and warning count:
  // the cross first (100000), then the name (99999).
  const button = vscode.window.createStatusBarItem('workspaceSwitcher.next', vscode.StatusBarAlignment.Left, 99999);
  button.name = 'Workspace';
  button.command = 'workspaceSwitcher.next';
  const target = nextFile();
  button.tooltip = target ? `Switch to ${nameOf(target)}` : 'Workspace';
  const file = openFile();
  button.text = `$(folder) ${file ? nameOf(file) : 'workspace'}`;
  button.show();

  const cross = vscode.window.createStatusBarItem('workspaceSwitcher.close', vscode.StatusBarAlignment.Left, 100000);
  cross.name = 'Close Workspace';
  cross.command = 'workspaceSwitcher.close';
  cross.text = '$(close)';
  cross.tooltip = 'Close workspace';
  const showClose = vscode.workspace.getConfiguration('workspaceSwitcher').get('showClose');
  if (file && showClose !== false) cross.show();

  context.subscriptions.push(
    button,
    cross,
    vscode.commands.registerCommand('workspaceSwitcher.next', next),
    vscode.commands.registerCommand('workspaceSwitcher.choose', choose),
    vscode.commands.registerCommand('workspaceSwitcher.close', close),
  );
}

function deactivate() {}

module.exports = { activate, deactivate };
