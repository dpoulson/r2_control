<?php
$message = null;
$error = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['filename']) && isset($_POST['scriptdata'])) {
    $filename = preg_replace('/[^a-zA-Z0-9_\-]/', '', $_POST['filename']);
    if (!empty($filename)) {
        $filepath = __DIR__ . '/../../scripts/' . $filename . '.scr';
        file_put_contents($filepath, $_POST['scriptdata']);
        $message = "Script saved successfully! You can now run it from the <a href='?page=scripts'>Scripting</a> page.";
    } else {
        $error = "Invalid filename. Use alphanumeric characters, underscores, and dashes only.";
    }
}
?>
<style>
.script-row { display: flex; gap: 10px; margin-bottom: 5px; align-items: center; background: rgba(255,255,255,0.05); padding: 5px; border-radius: 4px; }
.script-row select, .script-row input { padding: 5px; border-radius: 3px; border: 1px solid #555; background: #333; color: white; flex-grow: 1;}
.script-row select { max-width: 150px; }
.script-row .p1, .script-row .p2, .script-row .p3, .script-row .p4 { width: auto; flex-grow: 1; }
.script-writer-container { max-width: 800px; margin: 0 auto; padding: 20px; }
.script-writer-container h2 { margin-top: 0; }
.btn { padding: 8px 15px; cursor: pointer; background: #2c97de; color: white; border: none; border-radius: 4px; transition: background 0.2s; }
.btn:hover { background: #1f7bba; }
.btn-danger { background: #e74c3c; padding: 5px 10px; width: auto; flex-grow: 0 !important; }
.btn-danger:hover { background: #c0392b; }
.alert-success { background: rgba(39, 174, 96, 0.2); border: 1px solid #27ae60; padding: 10px; margin-bottom: 15px; border-radius: 4px; }
.alert-error { background: rgba(231, 76, 60, 0.2); border: 1px solid #e74c3c; padding: 10px; margin-bottom: 15px; border-radius: 4px; }
</style>

<div class="script-writer-container panel">
    <h2>Script Writer</h2>
    <p>Compose sequential commands for the bot to run. Scripts run row by row.</p>
    
    <?php if ($message) echo "<div class='alert-success'>$message</div>"; ?>
    <?php if ($error) echo "<div class='alert-error'>$error</div>"; ?>
    
    <div id="script-rows"></div>
    
    <div style="margin-top: 15px; display: flex; gap: 10px;">
        <select id="new-cmd-type" style="padding: 5px; border-radius: 3px; background: #333; color: white;">
            <option value="sleep">Sleep</option>
            <option value="body">Body</option>
            <option value="dome">Dome</option>
            <option value="sound">Sound</option>
            <option value="flthy">Flthy</option>
            <option value="smoke">Smoke</option>
            <option value="psi_matrix">Psi Matrix</option>
            <option value="rseries">RSeries</option>
        </select>
        <button type="button" class="btn" onclick="addRow()">Add Command</button>
    </div>
    
    <hr style="margin:20px 0; border-color:#555;">
    
    <form method="POST" id="save-form">
        <div style="display:flex; gap: 10px; align-items: center; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 4px;">
            <label><strong>Filename:</strong></label>
            <input type="text" name="filename" id="filename" required placeholder="my_script_name" style="padding: 8px; border-radius: 3px; border: 1px solid #555; background: #333; color: white; flex-grow: 1;">
            <span style="color: #aaa;">.scr</span>
            <input type="hidden" name="scriptdata" id="scriptdata">
            <button type="button" class="btn" style="background: #27ae60;" onclick="saveScript()">Save Script</button>
        </div>
    </form>
</div>

<script>
function createTemplate(type) {
    let tpl = '';
    if (type === 'sleep') {
        tpl = `
            <select class="p1" onchange="toggleSleepFields(this)">
                <option value="fixed">Fixed</option>
                <option value="random">Random</option>
            </select>
            <input type="number" class="p2" placeholder="Seconds" step="0.1">
            <input type="number" class="p3" placeholder="Max Seconds" style="display:none;" step="0.1">
        `;
    } else if (type === 'body' || type === 'dome') {
        tpl = `
            <select class="p1" onchange="toggleBodyDomeFields(this)">
                <option value="all">All</option>
                <option value="custom">Custom</option>
            </select>
            <input type="text" class="p2" placeholder="Param (e.g. 1)">
            <input type="text" class="p3" placeholder="Val 2" style="display:none;">
            <input type="text" class="p4" placeholder="Val 3" style="display:none;">
        `;
    } else if (type === 'sound') {
        tpl = `
            <select class="p1" onchange="toggleSoundFields(this)">
                <option value="specific">Specific ID</option>
                <option value="random">Random</option>
            </select>
            <input type="text" class="p2" placeholder="Sound ID or Bank">
        `;
    } else {
        // flthy, smoke, psi_matrix, rseries
        tpl = `<input type="text" class="p1" placeholder="Value">`;
    }
    
    return `
        <div class="script-row" data-type="${type}">
            <strong style="width: 80px; display:inline-block; text-transform:uppercase">${type}</strong>
            ${tpl}
            <button type="button" class="btn btn-danger" onclick="this.parentElement.remove()" title="Remove Row">X</button>
        </div>
    `;
}

function addRow() {
    const type = document.getElementById('new-cmd-type').value;
    const tpl = createTemplate(type);
    document.getElementById('script-rows').insertAdjacentHTML('beforeend', tpl);
}

function toggleSleepFields(sel) {
    const row = sel.closest('.script-row');
    if (sel.value === 'random') {
        row.querySelector('.p2').placeholder = 'Min Secs (Integer)';
        row.querySelector('.p3').style.display = 'inline-block';
        row.querySelector('.p3').placeholder = 'Max Secs (Integer)';
        row.querySelector('.p2').step = '1';
        row.querySelector('.p3').step = '1';
    } else {
        row.querySelector('.p2').placeholder = 'Seconds (e.g. 1.5)';
        row.querySelector('.p3').style.display = 'none';
        row.querySelector('.p3').value = '';
        row.querySelector('.p2').step = '0.1';
    }
}

function toggleBodyDomeFields(sel) {
    const row = sel.closest('.script-row');
    if (sel.value === 'custom') {
        row.querySelector('.p2').placeholder = 'Val 1';
        row.querySelector('.p3').style.display = 'inline-block';
        row.querySelector('.p4').style.display = 'inline-block';
    } else {
        row.querySelector('.p2').placeholder = 'Param (e.g. 1)';
        row.querySelector('.p3').style.display = 'none';
        row.querySelector('.p4').style.display = 'none';
        row.querySelector('.p3').value = '';
        row.querySelector('.p4').value = '';
    }
}

function toggleSoundFields(sel) {
    const row = sel.closest('.script-row');
    if (sel.value === 'random') {
        row.querySelector('.p2').placeholder = 'Bank ID';
    } else {
        row.querySelector('.p2').placeholder = 'Sound ID';
    }
}

function saveScript() {
    const rows = document.querySelectorAll('#script-rows .script-row');
    let csvData = [];
    
    rows.forEach(row => {
        const type = row.dataset.type;
        let line = [type];
        
        if (type === 'sleep') {
            const mode = row.querySelector('.p1').value;
            if (mode === 'random') {
                line.push('random', row.querySelector('.p2').value, row.querySelector('.p3').value);
            } else {
                line.push(row.querySelector('.p2').value);
            }
        } else if (type === 'body' || type === 'dome') {
            const mode = row.querySelector('.p1').value;
            if (mode === 'all') {
                line.push('all', row.querySelector('.p2').value);
            } else {
                // custom values might be user defined texts
                line.push(row.querySelector('.p2').value, row.querySelector('.p3').value, row.querySelector('.p4').value);
            }
        } else if (type === 'sound') {
            const mode = row.querySelector('.p1').value;
            if (mode === 'random') {
                line.push('random', row.querySelector('.p2').value);
            } else {
                line.push(row.querySelector('.p2').value);
            }
        } else {
            // flthy, smoke, psi_matrix, rseries
            line.push(row.querySelector('.p1').value);
        }
        
        // Trim missing trailing empty strings to keep CSV concise
        while(line.length > 0 && line[line.length-1] === "") {
            line.pop();
        }
        
        csvData.push(line.join(','));
    });
    
    if (csvData.length === 0) {
        alert('Script cannot be empty! Add at least one command.');
        return;
    }
    
    const filename = document.getElementById('filename').value;
    if (!filename) {
        alert('Please enter a valid filename.');
        document.getElementById('filename').focus();
        return;
    }
    
    document.getElementById('scriptdata').value = csvData.join('\\n');
    document.getElementById('save-form').submit();
}

// Ensure the page has at least one row automatically
window.addEventListener('DOMContentLoaded', () => {
    addRow();
});
</script>
