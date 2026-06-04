const vscode = require("vscode");

function activate(context) {
    console.log("Extension Asistente RNN activada");

    const comando = vscode.commands.registerCommand(
        "asistenteRNN.insertarSugerencia",
        async function () {
            const editor = vscode.window.activeTextEditor;

            if (!editor) {
                vscode.window.showErrorMessage("No hay editor activo.");
                return;
            }

            const document = editor.document;
            const position = editor.selection.active;

            const rango = new vscode.Range(
                new vscode.Position(0, 0),
                position
            );

            const textoAntesCursor = document.getText(rango);

            try {
                const respuesta = await fetch("http://127.0.0.1:5000/api/autocompletar", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        texto: textoAntesCursor,
                        cantidad: 80,
                        temperatura: 0.30
                    })
                });

                const datos = await respuesta.json();

                if (datos.estado !== "ok") {
                    vscode.window.showErrorMessage("Error en la API.");
                    return;
                }

                await editor.edit(editBuilder => {
                    editBuilder.insert(position, datos.sugerencia);
                });

                vscode.window.showInformationMessage("Sugerencia RNN insertada.");

            } catch (error) {
                vscode.window.showErrorMessage("No se pudo conectar con Flask.");
            }
        }
    );

    context.subscriptions.push(comando);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};