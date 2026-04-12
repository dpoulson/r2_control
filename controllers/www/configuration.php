<?php
include("include/config.php");

function setTheme($theme) {
	file_put_contents('theme.txt', $theme);
	header("Location: http://$_SERVER[HTTP_HOST]/?page=configuration");
	exit;
}

if (isset($_GET['theme'])) {
	$theme = $_GET['theme'];
	setTheme($theme);
}

// Handle Configuration Form Submit
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Collect settings
    $plugins_arr = $_POST['plugins'] ?? [];
    $plugins = is_array($plugins_arr) ? implode(',', $plugins_arr) : '';
    $servos = $_POST['servos'] ?? '';
    $postdata_arr = [
        'plugins' => $plugins,
        'servos' => $servos,
        'drive_type' => $_POST['drive_type'] ?? '',
        'drive_port' => $_POST['drive_port'] ?? '',
        'dome_type' => $_POST['dome_type'] ?? '',
        'dome_port' => $_POST['dome_port'] ?? ''
    ];
    foreach($_POST as $key => $val) {
        if (strpos($key, 'servo_addr_') === 0 || strpos($key, 'plugin_cfg__') === 0) {
            $postdata_arr[$key] = $val;
        }
    }
    $postdata = http_build_query($postdata_arr);

    $opts = [
        'http' => [
            'method'  => 'POST',
            'header'  => 'Content-type: application/x-www-form-urlencoded',
            'content' => $postdata
        ]
    ];
    $context  = stream_context_create($opts);
    @file_get_contents('http://localhost:5000/config/set', false, $context);
    
    // Redirect 
    header("Location: http://$_SERVER[HTTP_HOST]/?page=configuration&msg=saved");
    exit;
}

// Fetch current configuration
$config_json = @file_get_contents("http://localhost:5000/config/get");
$config_data = json_decode($config_json, true) ?: ['plugins' => '', 'servos' => '', 'drive_type' => ''];

$available_ports = $config_data['available_ports'] ?? [];
$drive_port = $config_data['drive_port'] ?? '';
$dome_port = $config_data['dome_port'] ?? '';

if ($drive_port && !in_array($drive_port, $available_ports)) {
    $available_ports[] = $drive_port;
}
if ($dome_port && !in_array($dome_port, $available_ports)) {
    $available_ports[] = $dome_port;
}
sort($available_ports);
?>
<style>
.config-form { padding: 10px; color: #fff;}
.config-group { margin-bottom: 20px; }
.config-group label { display: block; font-weight: bold; margin-bottom: 5px; color: #aaa;}
.config-group input[type="text"], .config-group select { width: 90%; padding: 10px; font-size: 16px; border-radius: 5px; border: 1px solid #444; background: #222; color: #fff; }
.msg { color: #0f0; font-weight: bold; margin-bottom: 15px; text-align: center; }
.save-btn { padding: 12px 24px; font-size: 16px; border-radius: 5px; cursor: pointer; background: #007bff; color: white; border: none; font-weight: bold; }
.save-btn:hover { background: #0056b3; }
</style>

<?php if(isset($_GET['msg']) && $_GET['msg'] === 'saved'): ?>
    <div class="msg">Configuration saved! Hard rebooting application...</div>
<?php endif; ?>

<h3 class="avail">System Settings</h3>
<form class="config-form" method="POST" action="?page=configuration">
    <div class="config-group">
        <label>Active Plugins</label>
        <div style="display: flex; flex-wrap: wrap; gap: 15px; padding-top: 5px;">
            <?php 
            $active_plugins = array_map('trim', explode(',', $config_data['plugins']));
            if (!empty($config_data['available_plugins'])) {
                foreach($config_data['available_plugins'] as $plugin) {
                    $checked = in_array(trim($plugin), $active_plugins) ? 'checked' : '';
                    echo "<label style=\"display:flex; align-items:center; font-weight:normal; color:#fff; cursor:pointer;\">";
                    echo "<input type=\"checkbox\" name=\"plugins[]\" value=\"".htmlspecialchars($plugin)."\" $checked style=\"width:auto; margin-right:5px;\"> ";
                    echo htmlspecialchars($plugin);
                    echo "</label>";
                }
            } else {
                echo "<input type=\"text\" name=\"plugins\" value=\"".htmlspecialchars($config_data['plugins'])."\" placeholder=\"e.g. Audio,Scripts,BLE\">";
            }
            ?>
        </div>
    </div>
    
    <div class="config-group" style="display:flex; gap:20px;">
        <div style="flex:1;">
            <label>Drive Controller Type</label>
            <select name="drive_type">
                <option value="odrive" <?php echo (($config_data['drive_type'] ?? '') == 'odrive') ? 'selected' : ''; ?>>ODrive</option>
                <option value="sabertooth" <?php echo (($config_data['drive_type'] ?? '') == 'sabertooth') ? 'selected' : ''; ?>>Sabertooth</option>
                <option value="vesc" <?php echo (($config_data['drive_type'] ?? '') == 'vesc') ? 'selected' : ''; ?>>VESC</option>
            </select>
        </div>
        <div style="flex:1;">
            <label>Drive Serial Port</label>
            <select name="drive_port">
                <option value="">-- Select Port --</option>
                <?php foreach($available_ports as $p): ?>
                    <option value="<?php echo htmlspecialchars($p); ?>" <?php echo ($drive_port === $p) ? 'selected' : ''; ?>><?php echo htmlspecialchars($p); ?></option>
                <?php endforeach; ?>
            </select>
        </div>
    </div>

    <div class="config-group" style="display:flex; gap:20px;">
        <div style="flex:1;">
            <label>Dome Controller Type</label>
            <select name="dome_type">
                <option value="Syren" <?php echo (($config_data['dome_type'] ?? '') == 'Syren') ? 'selected' : ''; ?>>Syren</option>
            </select>
        </div>
        <div style="flex:1;">
            <label>Dome Controller Serial Port</label>
            <select name="dome_port">
                <option value="">-- Select Port --</option>
                <?php foreach($available_ports as $p): ?>
                    <option value="<?php echo htmlspecialchars($p); ?>" <?php echo ($dome_port === $p) ? 'selected' : ''; ?>><?php echo htmlspecialchars($p); ?></option>
                <?php endforeach; ?>
            </select>
        </div>
    </div>
    
    <div class="config-group">
        <label>Active Servos (comma separated)</label>
        <input type="text" id="servos_input" name="servos" value="<?php echo htmlspecialchars($config_data['servos'] ?? ''); ?>" placeholder="e.g. dome,body" oninput="updateServoConfigList()">
    </div>

    <div id="dynamic_servos_container" class="config-group" style="display:flex; flex-wrap:wrap; gap:20px;">
        <!-- JS dynamically populates the fields here -->
    </div>

    <h3 class="avail" style="margin-top:40px;">Plugin Specific Configurations</h3>
    <?php if (empty($config_data['plugin_configs'])): ?>
        <p style="color:#aaa;">No dynamic configurations were found for currently active plugins.</p>
    <?php else: ?>
        <?php foreach (($config_data['plugin_configs'] ?? []) as $plugin_name => $sections): ?>
            <div class="config-group" style="padding:15px; border:1px solid #444; border-radius:8px; margin-bottom:15px; background: #1a1a1a;">
                <h4 style="margin-top:0; color:#4da6ff; margin-bottom: 20px;"><?php echo ucfirst($plugin_name); ?> Settings</h4>
                <?php foreach ($sections as $section_name => $keys): ?>
                    <?php if (count($sections) > 1): ?>
                        <h5 style="color:#888; border-bottom:1px solid #333; padding-bottom:5px;"><?php echo htmlspecialchars($section_name); ?></h5>
                    <?php endif; ?>
                    
                    <div style="display:flex; flex-wrap:wrap; gap:15px; margin-bottom:15px;">
                    <?php foreach ($keys as $k => $v): ?>
                        <div style="flex:1; min-width: 250px;">
                            <label style="color:#ccc;"><?php echo htmlspecialchars(ucfirst(str_replace('_', ' ', $k))); ?></label>
                            <input type="text" name="plugin_cfg__<?php echo htmlspecialchars($plugin_name); ?>__<?php echo htmlspecialchars($section_name); ?>__<?php echo htmlspecialchars($k); ?>" value="<?php echo htmlspecialchars($v); ?>">
                        </div>
                    <?php endforeach; ?>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php endforeach; ?>
    <?php endif; ?>

<script>
const existingServoAddrs = <?php echo json_encode($config_data['servo_addresses'] ?? []); ?>;

function updateServoConfigList() {
    const val = document.getElementById('servos_input').value;
    const list = val.split(',').map(s=>s.trim()).filter(s=>s);
    const container = document.getElementById('dynamic_servos_container');
    container.innerHTML = '';
    list.forEach(servo => {
        const addr = existingServoAddrs[servo] || '';
        container.innerHTML += `
        <div style="flex:1; min-width: 200px;">
            <label>${servo.charAt(0).toUpperCase() + servo.slice(1)} Servo Address (Hex)</label>
            <input type="text" name="servo_addr_${servo}" value="${addr}" placeholder="e.g. 0x40">
        </div>`;
    });
}
window.addEventListener('DOMContentLoaded', updateServoConfigList);
</script>

    <button type="submit" class="save-btn">Save & Restart System</button>
</form>

<br><hr style="border-color:#444;"/><br>

<h3 class="avail">Select your theme</h3>
<div class="items">
    <div class="item"><a href='?theme=blueprint'>Blueprint</a></div>
    <div class="item"><a href='?theme=galactic'>Galactic</a></div>
</div>

