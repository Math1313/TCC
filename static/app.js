// État de l'application
const sourceBoardInput = document.getElementById('sourceBoard');
const targetBoardsInput = document.getElementById('targetBoards');
const labelNameInput = document.getElementById('labelName');
const copyBtn = document.getElementById('copyBtn');
const clearBtn = document.getElementById('clearBtn');
const progressBar = document.getElementById('progressBar');
const consoleElement = document.getElementById('console');

// Charger la configuration au démarrage
window.addEventListener('DOMContentLoaded', async () => {
    await loadConfig();
});

// Charger la configuration sauvegardée
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const data = await response.json();
        
        if (data.source_board_id) {
            sourceBoardInput.value = data.source_board_id;
        }
        if (data.target_board_ids && data.target_board_ids.length > 0) {
            targetBoardsInput.value = data.target_board_ids.join('\n');
        }
        if (data.label_name) {
            labelNameInput.value = data.label_name;
        }
        
        logToConsole('✓ Configuration précédente chargée');
    } catch (error) {
        logToConsole('✗ Erreur lors du chargement de la configuration', 'error');
    }
}

// Bouton copier
copyBtn.addEventListener('click', async () => {
    const sourceBoardId = sourceBoardInput.value.trim();
    const targetBoardsText = targetBoardsInput.value.trim();
    const labelName = labelNameInput.value.trim();
    
    // Validation
    if (!sourceBoardId) {
        logToConsole('⚠️ Le Source Board ID est requis', 'warning');
        return;
    }
    
    const targetBoardIds = targetBoardsText
        .split('\n')
        .map(line => line.trim())
        .filter(line => line);
    
    if (targetBoardIds.length === 0) {
        logToConsole('⚠️ Au moins un Target Board ID est requis', 'warning');
        return;
    }
    
    if (!labelName) {
        logToConsole('⚠️ Le nom du Label est requis', 'warning');
        return;
    }
    
    // Désactiver les boutons et afficher la barre de progression
    copyBtn.disabled = true;
    clearBtn.disabled = true;
    progressBar.style.display = 'block';
    
    logToConsole('\n' + '='.repeat(70));
    logToConsole('🚀 DÉBUT DE LA COPIE');
    logToConsole('='.repeat(70));
    
    try {
        // Utiliser fetch avec streaming
        const response = await fetch('/api/copy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                source_board_id: sourceBoardId,
                target_board_ids: targetBoardIds,
                label_name: labelName
            })
        });
        
        if (!response.ok) {
            throw new Error('Erreur lors de la requête');
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            
            // Garder la dernière ligne incomplète dans le buffer
            buffer = lines.pop();
            
            for (const line of lines) {
                if (line.trim() === '') continue;
                
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.substring(6));
                        
                        if (data.log) {
                            logToConsole(data.log);
                        }
                        
                        if (data.result) {
                            const result = data.result;
                            if (result.error) {
                                logToConsole(`\n❌ Erreur: ${result.error}`, 'error');
                            } else if (result.failed === 0) {
                                logToConsole(`\n✅ ${result.success} carte(s) copiée(s) avec succès!`, 'success');
                            } else {
                                logToConsole(`\n⚠️ ${result.success} carte(s) copiée(s), ${result.failed} échouée(s)`, 'warning');
                            }
                        }
                        
                        if (data.error) {
                            logToConsole(`❌ Erreur: ${data.error}`, 'error');
                        }
                    } catch (e) {
                        console.error('Erreur parsing JSON:', e, line);
                    }
                }
            }
        }
        
    } catch (error) {
        logToConsole(`❌ Erreur critique: ${error.message}`, 'error');
    } finally {
        // Réactiver les boutons et cacher la barre de progression
        copyBtn.disabled = false;
        clearBtn.disabled = false;
        progressBar.style.display = 'none';
    }
});

// Bouton effacer
clearBtn.addEventListener('click', () => {
    const consoleCode = consoleElement.querySelector('code');
    consoleCode.innerHTML = '';
    logToConsole('✨ Console effacée');
});

// Fonction pour ajouter des logs à la console
function logToConsole(message, type = 'normal') {
    const consoleCode = consoleElement.querySelector('code');
    const line = document.createElement('div');
    
    if (type === 'error' || message.includes('❌') || message.includes('✗')) {
        line.className = 'log-error';
    } else if (type === 'success' || message.includes('✓') || message.includes('✅')) {
        line.className = 'log-success';
    } else if (type === 'warning' || message.includes('⚠️')) {
        line.className = 'log-warning';
    }
    
    line.textContent = message;
    consoleCode.appendChild(line);
    
    // Auto-scroll vers le bas
    consoleElement.scrollTop = consoleElement.scrollHeight;
}
