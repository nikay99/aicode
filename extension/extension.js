const vscode = require('vscode');
const { LanguageClient, TransportKind } = require('vscode-languageclient');

let client;

function activate(context) {
    const serverModule = require.resolve('aic/lsp/server.py');
    const debugOptions = { execArgv: ['--nolazy', '--inspect=6009'] };
    
    const serverOptions = {
        run: {
            command: 'python3',
            args: [serverModule],
            transport: TransportKind.stdio
        },
        debug: {
            command: 'python3',
            args: [serverModule],
            transport: TransportKind.stdio,
            options: debugOptions
        }
    };
    
    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'aic' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/.aic')
        }
    };
    
    client = new LanguageClient('aic-lsp', 'AICode Language Server', serverOptions, clientOptions);
    
    const disposable = client.start();
    context.subscriptions.push(disposable);
    
    client.onReady().then(() => {
        console.log('AICode Language Server is now active!');
    }).catch(err => {
        console.error('Failed to activate AICode Language Server:', err);
    });
}

function deactivate() {
    if (client) {
        return client.stop();
    }
    return undefined;
}

module.exports = { activate, deactivate };