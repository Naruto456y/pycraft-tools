import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
import requests

load_dotenv()
OAUTH_TOKEN = os.environ.get("SMART_HOME_TOKEN")   # токен лежит в .env, а не в коде
if not OAUTH_TOKEN:
    raise SystemExit("Не найден SMART_HOME_TOKEN: добавьте его в файл .env")
API_BASE = "https://api.iot.yandex.net/v1.0"

app = Flask(__name__)

HEADERS = {
    "Authorization": f"Bearer {OAUTH_TOKEN}",
    "Content-Type": "application/json"
}

HTML_PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Умный дом</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; padding: 20px; max-width: 1200px; margin: 0 auto; }
h1 { margin-bottom: 24px; color: #58a6ff; font-size: 1.6rem; }
.section { margin-bottom: 32px; }
.section-title { font-size: 1.15rem; font-weight: 600; margin-bottom: 14px; color: #f0f6fc; border-bottom: 1px solid #21262d; padding-bottom: 8px; }
.card { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 16px; margin-bottom: 12px; transition: border-color 0.2s; }
.card:hover { border-color: #58a6ff; }
.device-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.device-name { font-weight: 600; font-size: 1rem; color: #f0f6fc; min-width: 120px; }
.device-type { font-size: 0.8rem; color: #7d8590; }
.btn { background: #238636; color: #fff; border: none; padding: 7px 16px; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; transition: background 0.2s; }
.btn:hover { background: #2ea043; }
.btn.off { background: #da3633; }
.btn.off:hover { background: #f85149; }
.btn.scenario { background: #1f6feb; }
.btn.scenario:hover { background: #388bfd; }
input[type="range"] { width: 140px; accent-color: #58a6ff; }
.label { font-size: 0.85rem; color: #8b949e; display: inline-flex; align-items: center; gap: 6px; }
.value-display { font-size: 0.8rem; color: #58a6ff; min-width: 44px; text-align: right; }
.badge { font-size: 0.75rem; padding: 2px 8px; border-radius: 10px; background: #238636; color: #fff; }
.badge.inactive { background: #484f58; }
.notification { position: fixed; bottom: 20px; right: 20px; background: #161b22; border: 1px solid #30363d; color: #c9d1d9; padding: 14px 20px; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); display: none; z-index: 999; font-size: 0.9rem; max-width: 380px; }
.notification.show { display: block; animation: slideIn 0.3s ease; }
@keyframes slideIn { from { transform: translateX(400px); } to { transform: translateX(0); } }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 12px; }
</style>
</head>
<body>
<h1>&#127968; Управление умным домом</h1>

<div class="section">
<div class="section-title">Устройства</div>
<div class="grid" id="devices"></div>
</div>

<div class="section">
<div class="section-title">Группы</div>
<div class="grid" id="groups"></div>
</div>

<div class="section">
<div class="section-title">Сценарии</div>
<div class="grid" id="scenarios"></div>
</div>

<div class="notification" id="notif"></div>

<script>
function notify(msg, ok=true) {
  const el = document.getElementById('notif');
  el.textContent = msg;
  el.style.borderColor = ok ? '#238636' : '#da3633';
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 3000);
}

async function api(path, method='GET', body=null) {
  const opts = { method, headers: {'Content-Type':'application/json'} };
  if (body) opts.body = JSON.stringify(body);
  const r = await fetch(path, opts);
  return r.json();
}

async function loadData() {
  try {
    const data = await api('/api/info');
    if (data.error) { notify(data.error, false); return; }
    renderDevices(data.devices || []);
    renderGroups(data.groups || []);
    renderScenarios(data.scenarios || []);
  } catch(e) { notify('Ошибка: ' + e.message, false); }
}

function getCap(dev, type, inst) {
  return dev.capabilities?.find(c => c.type === type && (inst ? c.parameters?.instance === inst : true));
}

function renderDevices(devices) {
  const el = document.getElementById('devices');
  el.innerHTML = '';
  devices.forEach(d => {
    const card = document.createElement('div');
    card.className = 'card';
    const onOff = getCap(d, 'devices.capabilities.on_off');
    const bright = getCap(d, 'devices.capabilities.range', 'brightness');
    const color = getCap(d, 'devices.capabilities.color_setting');
    const isOn = onOff?.state?.value === true;
    const bVal = bright?.state?.value || 0;
    const cVal = color?.state?.value || 2700;
    let html = '<div class="device-row"><span class="device-name">' + d.name + '</span>';
    html += '<span class="device-type">' + d.type.replace('devices.types.','').replace(/\\./g,' ') + '</span>';
    if (onOff) html += '<button class="btn ' + (isOn?'off':'') + '" onclick="toggleDev(\\''+d.id+'\\','+!isOn+')">'+(isOn?'Выкл':'Вкл')+'</button>';
    if (bright) html += '<label class="label">&#9728; <input type="range" min="1" max="100" value="'+bVal+'" oninput="this.nextElementSibling.textContent=this.value+\'%\'" onchange="setDev(\\''+d.id+'\\',\\'devices.capabilities.range\\',\\'brightness\\','+ 'parseInt(this.value))"><span class="value-display">'+bVal+'%</span></label>';
    if (color && color.state) html += '<label class="label">&#127749; <input type="range" min="2700" max="6500" step="100" value="'+cVal+'" oninput="this.nextElementSibling.textContent=this.value+\'K\'" onchange="setDev(\\''+d.id+'\\',\\'devices.capabilities.color_setting\\',\\'temperature_k\\',' + 'parseInt(this.value))"><span class="value-display">'+cVal+'K</span></label>';
    if (!onOff && !bright && !color) html += '<span class="device-type">Нет управляемых функций</span>';
    html += '</div>';
    card.innerHTML = html;
    el.appendChild(card);
  });
}

function renderGroups(groups) {
  const el = document.getElementById('groups');
  el.innerHTML = '';
  groups.forEach(g => {
    const card = document.createElement('div');
    card.className = 'card';
    const onOff = g.capabilities?.find(c => c.type === 'devices.capabilities.on_off');
    const isOn = onOff?.state?.value === true;
    const bright = g.capabilities?.find(c => c.type === 'devices.capabilities.range' && c.parameters?.instance === 'brightness');
    const bVal = bright?.state?.value || 0;
    let html = '<div class="device-row"><span class="device-name">' + g.name + '</span>';
    html += '<span class="device-type">' + (g.devices?.length||0) + ' устройств</span>';
    if (onOff) html += '<button class="btn ' + (isOn?'off':'') + '" onclick="toggleGroup(\\''+g.id+'\\','+!isOn+')">'+(isOn?'Выкл':'Вкл')+'</button>';
    if (bright) html += '<label class="label">&#9728; <input type="range" min="1" max="100" value="'+bVal+'" oninput="this.nextElementSibling.textContent=this.value+\'%\'" onchange="setGroup(\\''+g.id+'\\',\\'devices.capabilities.range\\',\\'brightness\\',' + 'parseInt(this.value))"><span class="value-display">'+bVal+'%</span></label>';
    html += '</div>';
    card.innerHTML = html;
    el.appendChild(card);
  });
}

function renderScenarios(scenarios) {
  const el = document.getElementById('scenarios');
  el.innerHTML = '';
  scenarios.forEach(s => {
    const card = document.createElement('div');
    card.className = 'card';
    let triggers = (s.triggers||[]).map(t=>t.trigger.value).join(', ');
    let safeName = s.name.replace(/'/g, "\\'");
    let html = '<div class="device-row"><span class="device-name">' + s.name + '</span>';
    html += '<span class="badge ' + (s.is_active?'':'inactive') + '">' + (s.is_active?'активен':'выкл') + '</span>';
    if (triggers) html += '<span class="device-type">&#128172; ' + triggers + '</span>';
    html += '<button class="btn scenario" onclick="runScenario(\\''+s.id+'\\',\\''+safeName+'\\')">Запустить</button></div>';
    card.innerHTML = html;
    el.appendChild(card);
  });
}

async function toggleDev(id, val) { await postAction('/api/device', {device_id:id, capability:'devices.capabilities.on_off', instance:'on', value:val}); notify('Устройство ' + (val?'включено':'выключено')); setTimeout(loadData, 800); }
async function setDev(id, cap, inst, val) { await postAction('/api/device', {device_id:id, capability:cap, instance:inst, value:val}); notify('Значение изменено'); setTimeout(loadData, 800); }
async function toggleGroup(id, val) { await postAction('/api/group', {group_id:id, capability:'devices.capabilities.on_off', instance:'on', value:val}); notify('Группа ' + (val?'включена':'выключена')); setTimeout(loadData, 800); }
async function setGroup(id, cap, inst, val) { await postAction('/api/group', {group_id:id, capability:cap, instance:inst, value:val}); notify('Яркость изменена'); setTimeout(loadData, 800); }
async function runScenario(id, name) { await postAction('/api/scenario', {scenario_id:id}); notify('Сценарий запущен'); }

async function postAction(path, body) { try { const r = await api(path, 'POST', body); if (r.error) notify(r.error, false); } catch(e) { notify(e.message, false); } }

loadData();
setInterval(loadData, 30000);
</script>
</body>
</html>"""

@app.route("/")
def index():
    return HTML_PAGE

@app.route("/api/info", methods=["GET"])
def get_info():
    try:
        resp = requests.get(f"{API_BASE}/user/info", headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            return jsonify(resp.json())
        else:
            return jsonify({"error": f"API: {resp.status_code} - {resp.text}"}), resp.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 503

@app.route("/api/device", methods=["POST"])
def device_action():
    data = request.get_json()
    payload = {"devices": [{"id": data["device_id"], "capabilities": [{"type": data["capability"], "state": {"instance": data["instance"], "value": data["value"]}}]}]}
    try:
        resp = requests.post(f"{API_BASE}/devices/actions", headers=HEADERS, json=payload, timeout=10)
        return jsonify(resp.json() if resp.status_code == 200 else {"error": f"API: {resp.status_code}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 503

@app.route("/api/group", methods=["POST"])
def group_action():
    data = request.get_json()
    payload = {"groups": [{"id": data["group_id"], "capabilities": [{"type": data["capability"], "state": {"instance": data["instance"], "value": data["value"]}}]}]}
    try:
        resp = requests.post(f"{API_BASE}/groups/actions", headers=HEADERS, json=payload, timeout=10)
        return jsonify(resp.json() if resp.status_code == 200 else {"error": f"API: {resp.status_code}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 503

@app.route("/api/scenario", methods=["POST"])
def run_scenario():
    data = request.get_json()
    try:
        resp = requests.post(f"{API_BASE}/scenarios/{data['scenario_id']}/actions", headers=HEADERS, timeout=10)
        return jsonify(resp.json() if resp.status_code == 200 else {"error": f"API: {resp.status_code}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 503

if __name__ == "__main__":
    print("Server: http://127.0.0.1:8080")
    app.run(host="127.0.0.1", port=8080, debug=False)
