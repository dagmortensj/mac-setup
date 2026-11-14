// A button in the status bar that turns classroom mode on and off: the quiet,
// large-type setup for showing code on a projector. On: light theme, large
// type, and no suggestions, hovers, light bulbs, squiggles, auto-closing
// brackets or formatting, so what is typed stays exactly as typed. (The
// squiggles are hidden by making their colours transparent; VS Code has no
// setting that switches them off.) Off:
// everything back as it was.
//
// Nothing is reloaded, so the open files, the cursor and the other extensions
// are untouched. That is the difference from a separate profile, which
// reloads the window and binds the folder to itself.
//
// What the mode means is written in one place, the setting
// classroomMode.settings, whose default is in package.json. Turning the mode
// on writes those values into the user settings, the way every toggle in
// VS Code does, and remembers what each one was before. Turning it off puts
// exactly those back, and removes the ones that were not set at all. The
// remembered values are kept in the extension's own storage, so the mode
// survives a restart: it stays on until the button is clicked.
//
// A setting that this version of VS Code does not know, or that belongs to an
// extension that is not installed, cannot be written. It is skipped and named
// in one message, and the rest of the mode still applies. What has been
// written is remembered even if something fails halfway, so turning the mode
// off always restores it.
const vscode = require('vscode');

const SAVED = 'classroomMode.saved';
const GLOBAL = vscode.ConfigurationTarget.Global;

// The definition as a flat list. A key in square brackets holds settings for
// one language: { "[python]": { "editor.formatOnSave": false } }.
function entries() {
  const def = vscode.workspace.getConfiguration('classroomMode').get('settings') || {};
  const list = [];
  for (const [key, value] of Object.entries(def)) {
    const lang = /^\[(.+)\]$/.exec(key);
    if (lang && value && typeof value === 'object') {
      for (const [k, v] of Object.entries(value)) list.push({ lang: lang[1], key: k, value: v });
    } else {
      list.push({ lang: null, key, value });
    }
  }
  return list;
}

function config(lang) {
  return vscode.workspace.getConfiguration(undefined, lang ? { languageId: lang } : undefined);
}

// The value in the user settings, not the effective one: undefined when the
// setting is not written there.
function userValue(lang, key) {
  const found = config(lang).inspect(key);
  if (!found) return undefined;
  return lang ? found.globalLanguageValue : found.globalValue;
}

function isObject(v) {
  return v !== null && typeof v === 'object' && !Array.isArray(v);
}

async function turnOn(context) {
  const saved = [];
  const skipped = [];
  try {
    for (const e of entries()) {
      const before = userValue(e.lang, e.key);
      // An object, such as workbench.colorCustomizations, is merged into what
      // is there, so the mode adds its keys without removing the others.
      const value = isObject(e.value) && isObject(before) ? { ...before, ...e.value } : e.value;
      try {
        await config(e.lang).update(e.key, value, GLOBAL, Boolean(e.lang));
        saved.push({ lang: e.lang, key: e.key, had: before !== undefined, value: before });
      } catch (err) {
        skipped.push(e.key);
      }
    }
  } finally {
    await context.globalState.update(SAVED, saved);
  }
  if (skipped.length) {
    vscode.window.showWarningMessage(`Classroom Mode: skipped settings that VS Code does not know: ${skipped.join(', ')}`);
  }
}

async function turnOff(context) {
  const saved = context.globalState.get(SAVED) || [];
  const left = [];
  for (const s of saved) {
    try {
      await config(s.lang).update(s.key, s.had ? s.value : undefined, GLOBAL, Boolean(s.lang));
    } catch (err) {
      left.push(s);
    }
  }
  // Anything that could not be restored is kept, so another click tries again.
  await context.globalState.update(SAVED, left.length ? left : undefined);
  if (left.length) {
    vscode.window.showWarningMessage(`Classroom Mode: could not restore ${left.map((s) => s.key).join(', ')}. Click again to retry.`);
  }
}

function isOn(context) {
  return Array.isArray(context.globalState.get(SAVED));
}

function activate(context) {
  // Right-aligned items stand in descending priority from the left. The theme
  // button (hoest.toggle) has -1000 and stands at the edge; -999 is the place
  // just left of it.
  const button = vscode.window.createStatusBarItem('classroomMode.toggle', vscode.StatusBarAlignment.Right, -999);
  button.name = 'Classroom Mode';
  button.command = 'classroomMode.toggle';

  const refresh = () => {
    if (isOn(context)) {
      button.text = '$(mortar-board) Classroom';
      button.tooltip = 'Classroom mode is on. Click to turn it off.';
      button.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
    } else {
      button.text = '$(mortar-board)';
      button.tooltip = 'Turn classroom mode on';
      button.backgroundColor = undefined;
    }
  };

  let busy = false;
  const toggle = async () => {
    if (busy) return;
    busy = true;
    try {
      if (isOn(context)) await turnOff(context);
      else await turnOn(context);
    } catch (e) {
      vscode.window.showErrorMessage(`Classroom Mode: ${e.message || e}`);
    } finally {
      busy = false;
      refresh();
    }
  };

  refresh();
  button.show();
  context.subscriptions.push(button, vscode.commands.registerCommand('classroomMode.toggle', toggle));
}

function deactivate() {}

module.exports = { activate, deactivate };
