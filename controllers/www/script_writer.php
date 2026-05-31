<?php
$message = null;
$error = null;
$scripts_dir = __DIR__ . '/../../scripts/';

// Handle Save
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['filename']) && isset($_POST['scriptdata'])) {
    $filename = preg_replace('/[^a-zA-Z0-9_\-]/', '', $_POST['filename']);
    if (!empty($filename)) {
        $filepath = $scripts_dir . $filename . '.scr';
        file_put_contents($filepath, $_POST['scriptdata']);
        $message = "Script saved successfully!";
        
        // Handle Test execution
        if (isset($_POST['test_script']) && $_POST['test_script'] === '1') {
            $test_url = "http://localhost:5000/scripts/" . $filename . "/0";
            @file_get_contents($test_url);
            $message .= " Test execution started!";
        }
        $message .= " You can also run it from the <a href='?page=scripts'>Scripting</a> page.";
    } else {
        $error = "Invalid filename. Use alphanumeric characters, underscores, and dashes only.";
    }
}

// Get available scripts for loading
$available_scripts = [];
foreach (glob($scripts_dir . "*.scr") as $file) {
    $available_scripts[] = basename($file, '.scr');
}
sort($available_scripts);

// Handle Load
$load_data = [];
$load_filename = "";
if (isset($_GET['load']) && in_array($_GET['load'], $available_scripts)) {
    $load_filename = $_GET['load'];
    $filepath = $scripts_dir . $load_filename . '.scr';
    if (($handle = fopen($filepath, "r")) !== FALSE) {
        while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
            // Ignore empty lines or comments
            if (!empty($data) && count($data) > 0 && substr(trim($data[0]), 0, 1) !== '#') {
                $load_data[] = $data;
            }
        }
        fclose($handle);
    }
}

// Get available sounds for autocomplete
$sounds_dir = __DIR__ . '/../../sounds/';
$available_sounds = [];
if (is_dir($sounds_dir)) {
    foreach (glob($sounds_dir . "*.{mp3,wav}", GLOB_BRACE) as $file) {
        $available_sounds[] = pathinfo($file, PATHINFO_FILENAME);
    }
    sort($available_sounds);
}
?>
<style>
.script-row { display: flex; gap: 10px; margin-bottom: 5px; align-items: center; background: rgba(255,255,255,0.05); padding: 5px; border-radius: 4px; width: 100%; box-sizing: border-box; }
.script-row select, .script-row input { padding: 5px; border-radius: 3px; border: 1px solid #555; background: #333; color: white; flex-grow: 1; min-width: 0; }
.script-row select { max-width: 150px; }
.script-row .p1, .script-row .p2, .script-row .p3, .script-row .p4, .script-row .p5, .script-row .p6 { width: auto; flex-grow: 1; }
.script-writer-container { max-width: 900px; margin: 0 auto; padding: 20px; }
.script-writer-container h2 { margin-top: 0; }
.btn { padding: 8px 15px; cursor: pointer; background: #2c97de; color: white; border: none; border-radius: 4px; transition: background 0.2s; }
.btn:hover { background: #1f7bba; }
.btn-duplicate { background: #f39c12; padding: 5px 10px; width: auto; flex-grow: 0 !important; }
.btn-duplicate:hover { background: #e67e22; }
.btn-danger { background: #e74c3c; padding: 5px 10px; width: auto; flex-grow: 0 !important; }
.btn-danger:hover { background: #c0392b; }
.script-inputs { display: flex; gap: 10px; flex-grow: 1; align-items: center; min-width: 0; }
.script-actions { margin-left: auto; display: flex; gap: 5px; flex-shrink: 0; }
#script-rows { max-height: 55vh; overflow-y: auto; overflow-x: hidden; padding-right: 5px; margin-bottom: 15px; }
.alert-success { background: rgba(39, 174, 96, 0.2); border: 1px solid #27ae60; padding: 10px; margin-bottom: 15px; border-radius: 4px; }
.alert-error { background: rgba(231, 76, 60, 0.2); border: 1px solid #e74c3c; padding: 10px; margin-bottom: 15px; border-radius: 4px; }
.ui-state-highlight { height: 42px; background: rgba(255,255,255,0.1); border: 1px dashed #668CFF; border-radius: 4px; margin-bottom: 5px; }
.drag-handle:active { cursor: grabbing !important; }
.sortable-ghost { opacity: 0.4; }
</style>
<script src="js/Sortable.min.js"></script>

<div class="script-writer-container panel">
    <h2>Script Writer</h2>
    <p>Compose sequential commands for the bot to run. Scripts run row by row.</p>
    
    <div style="display:flex; gap: 10px; align-items: center; background: rgba(0,0,0,0.2); padding: 15px; border-radius: 4px; margin-bottom: 20px;">
        <label><strong>Load Script:</strong></label>
        <select id="load-script-select" style="padding: 8px; border-radius: 3px; border: 1px solid #555; background: #333; color: white;">
            <option value="">-- Select an existing script --</option>
            <?php foreach ($available_scripts as $s): ?>
                <option value="<?= htmlspecialchars($s) ?>" <?= $s === $load_filename ? 'selected' : '' ?>><?= htmlspecialchars($s) ?></option>
            <?php endforeach; ?>
        </select>
        <button type="button" class="btn" onclick="loadScript()">Load</button>
    </div>

    <?php if ($message) echo "<div class='alert-success'>$message</div>"; ?>
    <?php if ($error) echo "<div class='alert-error'>$error</div>"; ?>
    
    <div id="script-rows"></div>
    
    <div style="margin-top: 15px; display: flex; gap: 10px;">
        <select id="new-cmd-type" style="padding: 5px; border-radius: 3px; background: #333; color: white;">
            <option value="sleep">Sleep</option>
            <option value="body">Body</option>
            <option value="dome">Dome</option>
            <option value="autodome">Autodome</option>
            <option value="sound">Sound</option>
            <option value="script">Script (Nested)</option>
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
            <input type="hidden" name="test_script" id="test_script" value="0">
            <button type="button" class="btn" style="background: #27ae60;" onclick="saveScript(0)">Save</button>
            <button type="button" class="btn" style="background: #e67e22;" onclick="saveScript(1)">Save & Test</button>
        </div>
    </form>

    <datalist id="sound-files">
        <?php foreach ($available_sounds as $snd): ?>
            <option value="<?= htmlspecialchars($snd) ?>"></option>
        <?php endforeach; ?>
    </datalist>

    <datalist id="script-files">
        <?php foreach ($available_scripts as $s): ?>
            <option value="<?= htmlspecialchars($s) ?>"></option>
        <?php endforeach; ?>
    </datalist>
</div>

<script>
const loadedData = <?= json_encode($load_data) ?>;
const loadedFilename = <?= json_encode($load_filename) ?>;

function loadScript() {
    const sel = document.getElementById('load-script-select').value;
    if (sel) {
        window.location.href = "?page=script_writer&load=" + encodeURIComponent(sel);
    }
}

function createTemplate(type, rowData = null) {
    let tpl = '';
    
    // Helper to get row data safely
    const getVal = (index, defaultVal = '') => {
        return (rowData && rowData.length > index) ? rowData[index] : defaultVal;
    };

    if (type === 'sleep') {
        const mode = getVal(1) === 'random' ? 'random' : 'fixed';
        const v1 = mode === 'random' ? getVal(2) : getVal(1);
        const v2 = mode === 'random' ? getVal(3) : '';
        
        tpl = `
            <select class="p1" onchange="toggleSleepFields(this)">
                <option value="fixed" ${mode === 'fixed' ? 'selected' : ''}>Fixed</option>
                <option value="random" ${mode === 'random' ? 'selected' : ''}>Random</option>
            </select>
            <input type="number" class="p2" placeholder="${mode === 'random' ? 'Min Secs' : 'Seconds'}" step="${mode === 'random' ? '1' : '0.1'}" value="${v1}">
            <input type="number" class="p3" placeholder="Max Secs" style="display:${mode === 'random' ? 'inline-block' : 'none'};" step="1" value="${v2}">
        `;
    } else if (type === 'body' || type === 'dome') {
        // If mode is 'all', it's stored as type,all,command. Otherwise type,id,pos,speed
        const mode = getVal(1) === 'all' ? 'all' : (getVal(1) ? 'custom' : 'all');
        const v1 = getVal(1) === 'all' ? getVal(2) : getVal(1);
        const v2 = getVal(2);
        const v3 = getVal(3);
        
        tpl = `
            <select class="p1" onchange="toggleBodyDomeFields(this)">
                <option value="all" ${mode === 'all' ? 'selected' : ''}>All</option>
                <option value="custom" ${mode === 'custom' ? 'selected' : ''}>Custom</option>
            </select>
            <input type="text" class="p2" placeholder="${mode === 'custom' ? 'Servo ID (e.g. LLD)' : 'Command (e.g. open)'}" value="${v1}">
            <input type="text" class="p3" placeholder="Position" style="display:${mode === 'custom' ? 'inline-block' : 'none'};" value="${mode === 'custom' ? v2 : ''}">
            <input type="text" class="p4" placeholder="Speed" style="display:${mode === 'custom' ? 'inline-block' : 'none'};" value="${mode === 'custom' ? v3 : ''}">
        `;
    } else if (type === 'sound') {
        const mode = getVal(1) === 'random' ? 'random' : 'specific';
        const v1 = mode === 'random' ? getVal(2) : getVal(1);
        
        tpl = `
            <select class="p1" onchange="toggleSoundFields(this)">
                <option value="specific" ${mode === 'specific' ? 'selected' : ''}>Specific ID</option>
                <option value="random" ${mode === 'random' ? 'selected' : ''}>Random</option>
            </select>
            <input type="text" class="p2" placeholder="${mode === 'random' ? 'Category (e.g. happy)' : 'Sound ID'}" value="${v1}" ${mode === 'specific' ? 'list="sound-files"' : ''}>
        `;
    } else if (type === 'script') {
        const scriptName = getVal(1);
        const actionVal = getVal(2);
        tpl = `
            <input type="text" class="p1" placeholder="Script Name" value="${scriptName}" list="script-files">
            <select class="p2">
                <option value="" ${actionVal !== '1' && actionVal !== 'stop' ? 'selected' : ''}>Run Once</option>
                <option value="1" ${actionVal === '1' ? 'selected' : ''}>Loop Continuous</option>
                <option value="stop" ${actionVal === 'stop' ? 'selected' : ''}>Stop Script</option>
            </select>
        `;
    } else if (type === 'autodome') {
        const action = getVal(1) || 'spin';
        const p2 = getVal(2);
        const p3 = getVal(3);
        const p4 = getVal(4);
        
        tpl = `
            <select class="p1" onchange="toggleAutodomeFields(this)">
                <option value="spin" ${action === 'spin' ? 'selected' : ''}>Spin</option>
                <option value="stop" ${action === 'stop' ? 'selected' : ''}>Stop</option>
                <option value="random" ${action === 'random' ? 'selected' : ''}>Random Look</option>
                <option value="position" ${action === 'position' ? 'selected' : ''}>Position</option>
            </select>
            <input type="text" class="p2" placeholder="Direction (left/right)" value="${p2}" style="display:${action === 'spin' ? 'inline-block' : 'none'};">
            <input type="text" class="p3" placeholder="Speed (0.0-1.0)" value="${p3}" style="display:${action === 'spin' ? 'inline-block' : 'none'};">
            <input type="text" class="p4" placeholder="Duration Secs (optional)" value="${p4}" style="display:${action === 'spin' ? 'inline-block' : 'none'};">
            <select class="p5" style="display:${action === 'random' ? 'inline-block' : 'none'};">
                <option value="on" ${p2 === 'on' ? 'selected' : ''}>On</option>
                <option value="off" ${p2 === 'off' ? 'selected' : ''}>Off</option>
            </select>
            <input type="number" class="p6" placeholder="Angle" value="${action === 'position' ? p2 : ''}" style="display:${action === 'position' ? 'inline-block' : 'none'};">
        `;
    } else {
        // flthy, smoke, psi_matrix, rseries
        tpl = `<input type="text" class="p1" placeholder="Value" value="${getVal(1)}">`;
    }
    
    return `
        <div class="script-row" data-type="${type}">
            <span class="drag-handle" style="cursor: grab; color: #888; font-size: 1.2em; padding: 0 10px; flex-shrink: 0;" title="Drag to reorder">☰</span>
            <strong style="width: 85px; display:inline-block; text-transform:uppercase; flex-shrink: 0;">${type}</strong>
            <div class="script-inputs">
                ${tpl}
            </div>
            <div class="script-actions">
                <button type="button" class="btn btn-duplicate" onclick="duplicateRow(this)" title="Duplicate Row">Copy</button>
                <button type="button" class="btn btn-danger" onclick="this.parentElement.parentElement.remove()" title="Remove Row">X</button>
            </div>
        </div>
    `;
}

function duplicateRow(btn) {
    const row = btn.closest('.script-row');
    const clone = row.cloneNode(true);
    
    // We need to properly sync select values since cloneNode doesn't copy current states of selects
    const originalSelects = row.querySelectorAll('select');
    const clonedSelects = clone.querySelectorAll('select');
    originalSelects.forEach((select, i) => {
        clonedSelects[i].value = select.value;
    });
    
    row.parentNode.insertBefore(clone, row.nextSibling);
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
        row.querySelector('.p2').placeholder = 'Servo ID (e.g. LLD)';
        row.querySelector('.p3').style.display = 'inline-block';
        row.querySelector('.p4').style.display = 'inline-block';
    } else {
        row.querySelector('.p2').placeholder = 'Command (e.g. open)';
        row.querySelector('.p3').style.display = 'none';
        row.querySelector('.p4').style.display = 'none';
        row.querySelector('.p3').value = '';
        row.querySelector('.p4').value = '';
    }
}

function toggleSoundFields(sel) {
    const row = sel.closest('.script-row');
    const p2 = row.querySelector('.p2');
    if (sel.value === 'random') {
        p2.placeholder = 'Category (e.g. happy)';
        p2.removeAttribute('list');
    } else {
        p2.placeholder = 'Sound ID';
        p2.setAttribute('list', 'sound-files');
    }
}

function toggleAutodomeFields(sel) {
    const row = sel.closest('.script-row');
    const val = sel.value;
    row.querySelector('.p2').style.display = (val === 'spin') ? 'inline-block' : 'none';
    row.querySelector('.p3').style.display = (val === 'spin') ? 'inline-block' : 'none';
    row.querySelector('.p4').style.display = (val === 'spin') ? 'inline-block' : 'none';
    row.querySelector('.p5').style.display = (val === 'random') ? 'inline-block' : 'none';
    row.querySelector('.p6').style.display = (val === 'position') ? 'inline-block' : 'none';
    
    // Clear unused fields
    if (val !== 'spin') { row.querySelector('.p2').value = ''; row.querySelector('.p3').value = ''; row.querySelector('.p4').value = ''; }
    if (val !== 'position') { row.querySelector('.p6').value = ''; }
}

function saveScript(test = 0) {
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
                line.push(row.querySelector('.p2').value, row.querySelector('.p3').value, row.querySelector('.p4').value);
            }
        } else if (type === 'sound') {
            const mode = row.querySelector('.p1').value;
            if (mode === 'random') {
                line.push('random', row.querySelector('.p2').value);
            } else {
                line.push(row.querySelector('.p2').value);
            }
        } else if (type === 'script') {
            const scriptName = row.querySelector('.p1').value;
            const actionVal = row.querySelector('.p2').value;
            line.push(scriptName);
            if (actionVal) {
                line.push(actionVal);
            }
        } else if (type === 'autodome') {
            const action = row.querySelector('.p1').value;
            line.push(action);
            if (action === 'spin') {
                line.push(row.querySelector('.p2').value, row.querySelector('.p3').value);
                const dur = row.querySelector('.p4').value;
                if (dur) line.push(dur);
            } else if (action === 'random') {
                line.push(row.querySelector('.p5').value);
            } else if (action === 'position') {
                line.push(row.querySelector('.p6').value);
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
    
    document.getElementById('test_script').value = test ? "1" : "0";
    document.getElementById('scriptdata').value = csvData.join('\n');
    document.getElementById('save-form').submit();
}

window.addEventListener('DOMContentLoaded', () => {
    // Initialize drag-and-drop sortable
    if (typeof Sortable !== 'undefined') {
        new Sortable(document.getElementById('script-rows'), {
            handle: '.drag-handle',
            animation: 150,
            ghostClass: 'sortable-ghost'
        });
    } else {
        console.error("SortableJS not loaded.");
    }

    if (loadedFilename) {
        document.getElementById('filename').value = loadedFilename;
    }

    if (loadedData.length > 0) {
        loadedData.forEach(row => {
            const type = row[0];
            const tpl = createTemplate(type, row);
            document.getElementById('script-rows').insertAdjacentHTML('beforeend', tpl);
        });
    } else {
        addRow();
    }
});
</script>
