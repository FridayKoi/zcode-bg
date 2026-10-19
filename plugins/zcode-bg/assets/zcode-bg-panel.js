/* zcode-bg 设置面板 v0.8
 * 架构：每令牌独立深浅色调（文件层 CSS），面板只写 alpha 变量（--zcode-bg-a-*）。
 * 侧栏：按"宽度特征"定位——从 purpose-section 上溯，取最宽的窄列（<45% 窗宽）。
 */
(function () {
  if (window.__zcodeBgPanel) return;
  window.__zcodeBgPanel = true;

  var PANEL_VER = 8;
  try {
    if (localStorage.getItem('zcodeBgOvVer') !== String(PANEL_VER)) {
      localStorage.removeItem('zcodeBgOverrides');
      localStorage.setItem('zcodeBgOvVer', String(PANEL_VER));
    }
  } catch (e) {}

  var LS_OV = 'zcodeBgOverrides', LS_WP = 'zcodeBgWallpaper';
  var LS_SLOTS = 'zcodeBgSlots', LS_PURE = 'zcodeBgPure';
  /* 纯净模式用的"原版底色"（深/浅各一套），覆盖全部令牌让界面回到 ZCode 默认 */
  var ORIG_DARK = { background: '22,22,22,1', card: '43,43,43,1', sidebar: '13,13,13,1',
                    menu: '13,13,13,1', input: '43,43,43,1', surface: '13,13,13,.03' };
  var ORIG_LIGHT = { background: '248,248,248,1', card: '255,255,255,1', sidebar: '255,255,255,1',
                     menu: '255,255,255,1', input: '255,255,255,1', surface: '255,255,255,.5' };
  var TOKEN_OF = {
    background: ['--color-background', '--color-background-alt', '--color-background-win-alt',
                 '--color-header', '--color-panel', '--color-neutral-900'],
    card: ['--color-card', '--color-card-selected'],
    sidebar: ['--color-sidebar', '--color-neutral-950'],
    menu: ['--color-menu', '--color-popover'],
    input: ['--color-input', '--color-input-focused'],
    surface: ['--color-surface']
  };
  var pureOn = false, resetBtn = null;
  var PRESETS = {
    subtle:    { background: .55, card: .68, sidebar: .62, menu: .72, input: .75, surface: .60, overlay: .16 },
    balanced:  { background: .42, card: .55, sidebar: .50, menu: .60, input: .62, surface: .48, overlay: .10 },
    immersive: { background: .28, card: .40, sidebar: .34, menu: .45, input: .52, surface: .34, overlay: .06 }
  };
  var SLIDERS = ['background', 'card', 'sidebar', 'surface', 'menu', 'input', 'overlay'];
  var LABELS = { background: '工作区底色', card: '工作区卡片', sidebar: '侧栏独立底色',
                 surface: '分组小组件', menu: '菜单 / 弹层', input: '输入框', overlay: '整体压暗' };

  function load(k, fb) { try { return JSON.parse(localStorage.getItem(k)) || fb; } catch (e) { return fb; } }
  function save(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }

  function varName(k) {
    return (k === 'overlay') ? '--zcode-bg-overlay'
      : (k === 'sidebar') ? '--zcode-bg-sidebar'
      : '--zcode-bg-a-' + k;
  }
  function applyOverride(k, a) {
    document.documentElement.style.setProperty(varName(k), a, 'important');
  }
  function applyAll(ov) { for (var k in ov) applyOverride(k, ov[k]); }
  function applyWallpaper(dataUrl) {
    var s = document.documentElement.style;
    if (dataUrl) {
      s.setProperty('background', 'url("' + dataUrl + '") center / cover no-repeat fixed', 'important');
      s.setProperty('background-color', '#151515', 'important');
    } else {
      s.removeProperty('background');
      s.removeProperty('background-color');
    }
  }
  function bootApply() {
    if (load(LS_PURE, false)) { applyPure(true); return; }
    applyAll(load(LS_OV, {}));
    var wp = load(LS_WP, null);
    if (wp) applyWallpaper(wp);
  }

  function currentThemeDark() {
    return (document.documentElement.className || '').indexOf('dark') !== -1;
  }
  function updatePureUI() {
    if (resetBtn) {
      resetBtn.textContent = pureOn ? '退出纯净模式，恢复主题壁纸'
                                    : '恢复 ZCode 原版外观（无壁纸）';
    }
  }
  function applyPure(on) {
    var s = document.documentElement.style;
    if (on) {
      var tbl = currentThemeDark() ? ORIG_DARK : ORIG_LIGHT;
      Object.keys(TOKEN_OF).forEach(function (k) {
        var v = tbl[k] || tbl.background;
        TOKEN_OF[k].forEach(function (vn) {
          s.setProperty(vn, 'rgba(' + v + ')', 'important');
        });
      });
      s.setProperty('background', 'none', 'important');
      s.setProperty('--zcode-bg-overlay', 0, 'important');
      s.setProperty('--zcode-bg-sidebar', 1, 'important');
      pureOn = true;
      save(LS_PURE, true);
    } else {
      Object.keys(TOKEN_OF).forEach(function (k) {
        TOKEN_OF[k].forEach(function (vn) { s.removeProperty(vn); });
      });
      s.removeProperty('background');
      s.removeProperty('background-color');
      s.removeProperty('--zcode-bg-overlay');
      s.removeProperty('--zcode-bg-sidebar');
      pureOn = false;
      save(LS_PURE, false);
      applyAll(load(LS_OV, {}));
      var wp = load(LS_WP, null);
      if (wp) applyWallpaper(wp);
    }
    updatePureUI();
  }

  /* ---------- 侧栏独立底色：宽度特征定位 + 清理误画的祖先 ---------- */
  function paintSidebar() {
    var ps = document.querySelector('.group\\/purpose-section');
    if (!ps) return;
    var W = window.innerWidth || 1280;
    var t = ps, best = null;
    while (t && t !== document.body) {
      var r = t.getBoundingClientRect();
      if (r.width > 0 && r.width < W * 0.45) best = t;
      else if (best) break;   // 越往上越宽，一旦超宽立即停：best 即侧栏柱子
      t = t.parentElement;
    }
    if (!best) return;
    best.style.setProperty('background',
      'rgba(var(--zcode-bg-tint-sidebar), var(--zcode-bg-sidebar, .5))', 'important');
    best.style.setProperty('border-right', '1px solid rgba(128, 128, 138, .18)', 'important');
    // 清理历史版本误画在祖先包裹层上的内联背景
    var anc = best.parentElement;
    while (anc && anc !== document.body) {
      var bg = anc.style && anc.style.background;
      if (bg && bg.indexOf('zcode-bg-tint') !== -1) {
        anc.style.removeProperty('background');
        anc.style.removeProperty('border-right');
      }
      anc = anc.parentElement;
    }
  }

  /* ---------- 工具栏按钮 ---------- */
  var panelEl, panelVisible = false;
  function togglePanel(force) {
    panelVisible = (force != null) ? force : !panelVisible;
    panelEl.style.display = panelVisible ? 'block' : 'none';
  }

  var PALETTE_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/></svg>';

  function makeToolbarButton(donor) {
    var btn = document.createElement('button');
    if (donor) {
      var cls = donor.getAttribute('class');
      if (cls) btn.setAttribute('class', cls);
    } else {
      btn.style.cssText = 'display:inline-flex;align-items:center;justify-content:center;' +
        'width:28px;height:28px;border-radius:6px;background:rgba(255,255,255,.06);' +
        'border:none;color:#bbb;cursor:pointer;';
    }
    btn.type = 'button';
    btn.title = '背景设置 (zcode-bg)';
    btn.innerHTML = PALETTE_SVG;
    btn.addEventListener('click', function (e) { e.stopPropagation(); togglePanel(); });
    return btn;
  }

  function findAnchorButton() {
    var w = window.innerWidth || 1280;
    var all = document.querySelectorAll('*');
    var boxes = [];
    for (var i = 0; i < all.length; i++) {
      var e = all[i];
      if (e.id === 'zcode-bg-toolbar-btn' || e.id === 'zcode-bg-float-btn') continue;
      if (e.closest && e.closest('#zcode-bg-panel')) continue;
      var r = e.getBoundingClientRect();
      if (r.width < 20 || r.width > 90 || r.height < 20 || r.height > 50) continue;
      if (r.top < -2 || r.top > 48) continue;
      if (r.left < w * 0.5) continue;
      boxes.push(e);
    }
    boxes = boxes.filter(function (e) { return boxes.indexOf(e.parentElement) === -1; });
    boxes.sort(function (a, b) {
      return a.getBoundingClientRect().left - b.getBoundingClientRect().left;
    });
    return boxes.length >= 2 ? boxes[1] : null;
  }

  function makeFloatButton() {
    var btn = document.getElementById('zcode-bg-float-btn');
    if (btn) return btn;
    btn = makeToolbarButton(null);
    btn.id = 'zcode-bg-float-btn';
    btn.style.cssText += 'position:fixed;top:8px;right:12px;z-index:2147483000;';
    (document.body || document.documentElement).appendChild(btn);
    return btn;
  }

  function tick() {
    if (!document.getElementById('zcode-bg-toolbar-btn')) {
      var anchor = findAnchorButton();
      if (anchor && anchor.parentNode) {
        var btn = makeToolbarButton(anchor);
        btn.id = 'zcode-bg-toolbar-btn';
        anchor.parentNode.insertBefore(btn, anchor);
        var f = document.getElementById('zcode-bg-float-btn');
        if (f) f.remove();
      } else {
        tick.tries = (tick.tries || 0) + 1;
        if (tick.tries > 10 && !document.getElementById('zcode-bg-float-btn')) makeFloatButton();
      }
    }
    paintSidebar();
    if (themeLine) {
      var cls = (document.documentElement.className || '').slice(0, 70) || '(无类名)';
      themeLine.textContent = '主题检测: html.' + cls;
    }
  }

  /* ---------- 面板 ---------- */
  var CSS = {
    panel: 'position:fixed;top:44px;right:56px;z-index:2147483000;width:318px;max-height:78vh;' +
           'overflow:auto;border-radius:16px;border:1px solid rgba(255,255,255,.10);' +
           'background:rgba(22,22,28,.97);backdrop-filter:blur(14px);color:#e6e8ef;' +
           'font:12.5px/1.65 system-ui,"Segoe UI",sans-serif;padding:16px;display:none;' +
           'box-shadow:0 12px 48px rgba(0,0,0,.45);',
    title: 'display:flex;align-items:center;gap:8px;font-weight:700;font-size:14px;margin:0 2px 4px;',
    ver: 'font-size:10px;opacity:.35;font-weight:400;',
    close: 'margin-left:auto;cursor:pointer;opacity:.55;font-size:13px;width:24px;height:24px;' +
           'display:flex;align-items:center;justify-content:center;border-radius:8px;',
    card: 'background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.06);' +
          'border-radius:12px;padding:12px;margin-top:10px;',
    h: 'margin:0 0 8px;font-weight:600;font-size:11px;letter-spacing:.1em;opacity:.5;' +
       'text-transform:uppercase;',
    row: 'display:flex;align-items:center;gap:10px;margin:7px 0;',
    label: 'width:78px;flex:none;opacity:.92;font-size:12px;',
    range: 'flex:1;accent-color:#7aa2f7;height:3px;cursor:pointer;',
    val: 'min-width:40px;text-align:center;background:rgba(255,255,255,.09);' +
         'border-radius:7px;padding:2px 4px;font-variant-numeric:tabular-nums;font-size:11px;',
    probe: 'white-space:pre-line;font:10px/1.5 Consolas,monospace;opacity:.75;margin-top:8px;' +
           'background:rgba(0,0,0,.28);border-radius:8px;padding:8px;max-height:130px;overflow:auto;',
    hint: 'margin-top:12px;opacity:.38;font-size:10.5px;line-height:1.5;'
  };

  var STYLE_TEXT =
    '#zcode-bg-panel .zbg-presets{display:flex;gap:6px;}' +
    '#zcode-bg-panel .zbg-preset{flex:1;text-align:center;cursor:pointer;' +
    'border:1px solid rgba(255,255,255,.16);background:rgba(255,255,255,.07);color:#e6e8ef;' +
    'border-radius:9px;padding:7px 0;font-size:11.5px;transition:all .15s;}' +
    '#zcode-bg-panel .zbg-preset:hover{background:rgba(122,162,247,.22);border-color:rgba(122,162,247,.55);}' +
    '#zcode-bg-panel .zbg-preset.active{background:rgba(122,162,247,.30);border-color:#7aa2f7;' +
    'box-shadow:0 0 0 1px rgba(122,162,247,.35) inset;}' +
    '#zcode-bg-panel .zbg-btn{display:inline-flex;align-items:center;justify-content:center;' +
    'cursor:pointer;border:1px solid rgba(255,255,255,.16);background:rgba(255,255,255,.07);' +
    'color:#e6e8ef;border-radius:9px;padding:6px 12px;font-size:11.5px;transition:all .15s;}' +
    '#zcode-bg-panel .zbg-btn:hover{background:rgba(255,255,255,.14);border-color:rgba(255,255,255,.25);}' +
    '#zcode-bg-panel .zbg-file{display:none;}' +
    '#zcode-bg-panel .zbg-filebtn{width:100%;}' +
    '#zcode-bg-panel .zbg-row2{display:flex;gap:8px;margin-top:8px;}' +
    '#zcode-bg-panel .zbg-num{width:54px;flex:none;text-align:center;background:rgba(255,255,255,.09);' +
    'border:1px solid rgba(255,255,255,.14);border-radius:7px;color:#e6e8ef;font-size:11px;' +
    'padding:3px 2px;font-variant-numeric:tabular-nums;outline:none;}' +
    '#zcode-bg-panel .zbg-num:focus{border-color:#7aa2f7;}' +
    '#zcode-bg-panel .zbg-link{display:flex;align-items:center;gap:8px;margin:2px 0 10px;' +
    'padding:9px 10px;border-radius:10px;background:rgba(122,162,247,.10);' +
    'border:1px solid rgba(122,162,247,.25);}' +
    '#zcode-bg-panel .zbg-link .zbg-num{background:rgba(122,162,247,.12);}' +
    '#zcode-bg-panel .zbg-linklabel{font-size:11.5px;flex:none;opacity:.95;}' +
    '#zcode-bg-panel .zbg-slot{display:flex;align-items:center;gap:6px;margin:4px 0;}' +
    '#zcode-bg-panel .zbg-slotlabel{width:48px;font-size:11px;opacity:.75;flex:none;}' +
    '#zcode-bg-panel .zbg-slotinfo{flex:1;font-size:10px;opacity:.45;overflow:hidden;' +
    'text-overflow:ellipsis;white-space:nowrap;}' +
    '#zcode-bg-panel .zbg-mini{padding:3px 8px;font-size:10.5px;border-radius:7px;}' +
    '#zcode-bg-panel .zbg-btn:disabled{opacity:.3;cursor:default;}';

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  var probeOut, probing = false, ov, sliders = {}, presetBtns = [], themeLine;

  function setPresetActive(name) {
    presetBtns.forEach(function (b) { b.classList.toggle('active', b.dataset.name === name); });
  }

  function clampAlpha(a) {
    return Math.round(Math.max(0, Math.min(0.95, a)) * 100) / 100;
  }

  function setKnob(k, a) {
    if (pureOn) applyPure(false);
    a = clampAlpha(a);
    ov[k] = a;
    applyOverride(k, a);
    save(LS_OV, ov);
    if (sliders[k]) {
      sliders[k].range.value = a;
      sliders[k].num.value = a;
    }
    setPresetActive(null);
  }

  function makeSliderRow(k, cur) {
    var row = el('div', CSS.row);
    row.appendChild(el('span', CSS.label, LABELS[k] || k));
    var r = document.createElement('input');
    r.type = 'range'; r.min = 0; r.max = 0.95; r.step = 0.01; r.value = cur;
    r.style.cssText = CSS.range;
    var num = document.createElement('input');
    num.type = 'number'; num.min = 0; num.max = 0.95; num.step = 0.01;
    num.className = 'zbg-num'; num.value = cur;
    r.oninput = function () { setKnob(k, parseFloat(r.value)); };
    num.oninput = function () {
      var a = parseFloat(num.value);
      if (!isNaN(a)) setKnob(k, a);
    };
    num.onblur = function () {
      var a = parseFloat(num.value);
      num.value = isNaN(a) ? ((ov[k] != null) ? ov[k] : PRESETS.balanced[k]) : clampAlpha(a);
    };
    row.appendChild(r); row.appendChild(num);
    sliders[k] = { range: r, num: num };
    return row;
  }

  function buildPanel() {
    var style = document.createElement('style');
    style.id = 'zcode-bg-style';
    style.textContent = STYLE_TEXT;
    document.head.appendChild(style);

    panelEl = document.createElement('div');
    panelEl.id = 'zcode-bg-panel';
    panelEl.style.cssText = CSS.panel;
    ov = load(LS_OV, {});

    var title = el('div', CSS.title);
    title.appendChild(el('span', null, '🎨'));
    title.appendChild(el('span', null, '背景主题'));
    title.appendChild(el('span', CSS.ver, 'v' + PANEL_VER));
    var x = el('span', CSS.close, '✕');
    x.onclick = function () { togglePanel(false); };
    title.appendChild(x);
    panelEl.appendChild(title);

    /* 预设卡片 */
    var sec1 = el('div', CSS.card);
    sec1.appendChild(el('div', CSS.h, '预设'));
    var presetRow = el('div', 'zbg-presets');
    Object.keys(PRESETS).forEach(function (name) {
      var b = el('button', 'zbg-preset', name);
      b.dataset.name = name;
      presetBtns.push(b);
      b.onclick = function () {
        ov = {};
        var p = PRESETS[name];
        Object.keys(p).forEach(function (k) { setKnob(k, p[k]); });
        save(LS_OV, ov);
        setPresetActive(name);
        lr.value = p.background; ln.value = p.background;
      };
      presetRow.appendChild(b);
    });
    sec1.appendChild(presetRow);

    /* 我的预设：5 个槽位（仅存透明度，不含壁纸） */
    var slots = load(LS_SLOTS, []);
    while (slots.length < 5) slots.push(null);
    var slotWrap = el('div', 'margin-top:12px;');
    slotWrap.appendChild(el('div', CSS.h, '我的预设（5 槽 · 仅存透明度）'));
    for (var si = 0; si < 5; si++) (function (idx) {
      var row = el('div', 'zbg-slot');
      row.appendChild(el('span', 'zbg-slotlabel', '槽位' + (idx + 1)));
      var info = el('span', 'zbg-slotinfo', '空');
      var saveBtn = el('button', 'zbg-btn zbg-mini', '保存');
      var applyBtn = el('button', 'zbg-btn zbg-mini', '应用');
      function render() {
        var s = slots[idx];
        info.textContent = s
          ? ('bg ' + Number(s.background).toFixed(2) + ' · 侧 ' + Number(s.sidebar).toFixed(2) +
             ' · 卡 ' + Number(s.card).toFixed(2))
          : '空';
        applyBtn.disabled = !s;
      }
      saveBtn.onclick = function () {
        var snap = {};
        SLIDERS.forEach(function (k) { snap[k] = (ov[k] != null) ? ov[k] : PRESETS.balanced[k]; });
        slots[idx] = snap;
        save(LS_SLOTS, slots);
        render();
      };
      applyBtn.onclick = function () {
        var snap = slots[idx];
        if (!snap) return;
        if (pureOn) applyPure(false);
        ov = {};
        Object.keys(snap).forEach(function (k) {
          if (SLIDERS.indexOf(k) !== -1) setKnob(k, snap[k]);
        });
        save(LS_OV, ov);
        setPresetActive(null);
        if (snap.background != null) { lr.value = snap.background; ln.value = snap.background; }
      };
      row.appendChild(info); row.appendChild(saveBtn); row.appendChild(applyBtn);
      slotWrap.appendChild(row);
      render();
    })(si);
    sec1.appendChild(slotWrap);
    panelEl.appendChild(sec1);

    /* 透明度卡片 */
    var sec2 = el('div', CSS.card);
    sec2.appendChild(el('div', CSS.h, '透明度（0 全透 → 0.95 实心）'));

    /* 联动总控：工作区 + 侧栏 */
    var linkRow = el('div', 'zbg-link');
    linkRow.appendChild(el('span', 'zbg-linklabel', '工作区+侧栏联动'));
    var linkInit = (ov.background != null) ? ov.background : PRESETS.balanced.background;
    var lr = document.createElement('input');
    lr.type = 'range'; lr.min = 0; lr.max = 0.95; lr.step = 0.01; lr.value = linkInit;
    lr.style.cssText = CSS.range;
    var ln = document.createElement('input');
    ln.type = 'number'; ln.min = 0; ln.max = 0.95; ln.step = 0.01;
    ln.className = 'zbg-num'; ln.value = linkInit;
    function applyLinked(a) {
      a = clampAlpha(a);
      ln.value = a;
      setKnob('background', a);
      setKnob('sidebar', a);
    }
    lr.oninput = function () { applyLinked(parseFloat(lr.value)); };
    ln.oninput = function () { var a = parseFloat(ln.value); if (!isNaN(a)) { lr.value = a; applyLinked(a); } };
    linkRow.appendChild(lr); linkRow.appendChild(ln);
    sec2.appendChild(linkRow);

    SLIDERS.forEach(function (k) {
      var cur = (ov[k] != null) ? ov[k] : PRESETS.balanced[k];
      sec2.appendChild(makeSliderRow(k, cur));
    });
    sec2.appendChild(el('div', 'opacity:.38;font-size:10.5px;margin-top:6px;',
      '侧栏=左侧栏独立底色 · 卡片=工作区消息/文件卡片 · 菜单=右键可见'));
    panelEl.appendChild(sec2);

    /* 壁纸卡片 */
    var sec3 = el('div', CSS.card);
    sec3.appendChild(el('div', CSS.h, '壁纸'));
    var file = document.createElement('input');
    file.type = 'file'; file.accept = 'image/*'; file.className = 'zbg-file';
    file.id = 'zcode-bg-file';
    file.onchange = function () {
      var f = file.files && file.files[0];
      if (!f) return;
      var url = URL.createObjectURL(f);
      var img = new Image();
      img.onload = function () {
        // 自动压缩：最长边 2560，高质量 JPEG；仍过大再降一档质量
        var maxW = 2560;
        var scale = Math.min(1, maxW / img.naturalWidth);
        var w = Math.max(1, Math.round(img.naturalWidth * scale));
        var h = Math.max(1, Math.round(img.naturalHeight * scale));
        var cv = document.createElement('canvas');
        cv.width = w; cv.height = h;
        var ctx = cv.getContext('2d');
        ctx.drawImage(img, 0, 0, w, h);
        var data = null;
        try { data = cv.toDataURL('image/jpeg', 0.85); } catch (e) {}
        URL.revokeObjectURL(url);
        if (!data) { alert('这张图片处理失败，换一张试试'); return; }
        if (data.length > 4.2 * 1024 * 1024) data = cv.toDataURL('image/jpeg', 0.7);
        if (pureOn) applyPure(false);
        applyWallpaper(data);
        save(LS_WP, data);
        // 校验是否真的存进去了（超出 localStorage 配额会静默失败）
        try {
          if (localStorage.getItem(LS_WP) !== JSON.stringify(data)) {
            alert('壁纸已应用，但保存失败（存储空间不足），重启后会丢失。建议换一张尺寸小些的图。');
          }
        } catch (e) {}
      };
      img.onerror = function () {
        URL.revokeObjectURL(url);
        alert('无法读取这张图片格式，换一张试试');
      };
      img.src = url;
    };
    sec3.appendChild(file);
    var fileBtn = el('button', 'zbg-btn zbg-filebtn', '选择本地图片作为壁纸');
    fileBtn.onclick = function () { file.click(); };
    sec3.appendChild(fileBtn);
    var wpReset = el('button', 'zbg-btn zbg-filebtn', '恢复文件层壁纸');
    wpReset.style.marginTop = '8px';
    wpReset.onclick = function () { save(LS_WP, null); applyWallpaper(null); };
    sec3.appendChild(wpReset);
    panelEl.appendChild(sec3);

    /* 诊断卡片 */
    var sec4 = el('div', CSS.card);
    sec4.appendChild(el('div', CSS.h, '诊断'));
    var probeBtn = el('button', 'zbg-btn', '取色探针');
    probeBtn.onclick = function () {
      probing = !probing;
      probeBtn.textContent = probing ? '探测中…点界面任意处' : '取色探针';
      document.body.style.cursor = probing ? 'crosshair' : '';
    };
    sec4.appendChild(probeBtn);
    probeOut = el('div', CSS.probe, '点探针再点任意区域，列出 12 层祖先的类名与背景。');
    sec4.appendChild(probeOut);
    resetBtn = el('button', 'zbg-btn zbg-filebtn', '恢复 ZCode 原版外观（无壁纸）');
    resetBtn.style.marginTop = '8px';
    resetBtn.onclick = function () { applyPure(!pureOn); };
    sec4.appendChild(resetBtn);
    updatePureUI();
    panelEl.appendChild(sec4);
    panelEl.appendChild(el('div', CSS.hint,
      '调整即时生效并自动保存；面板值优先于文件层，"全部恢复默认"回到文件层。'));
    themeLine = el('div', CSS.hint, '主题检测: …');
    panelEl.appendChild(themeLine);
    (document.body || document.documentElement).appendChild(panelEl);

    setPresetActive(ov && Object.keys(ov).length ? null : 'balanced');
  }

  /* 点击面板外自动收起；探针模式优先 */
  document.addEventListener('click', function (e) {
    if (!probing) {
      if (panelVisible && panelEl && !panelEl.contains(e.target) &&
          !(e.target.closest && e.target.closest('#zcode-bg-toolbar-btn,#zcode-bg-float-btn'))) {
        togglePanel(false);
      }
      return;
    }
    if (panelEl.contains(e.target)) return;
    e.preventDefault(); e.stopPropagation();
    probing = false;
    document.body.style.cursor = '';
    var out = [], t = e.target, i = 0;
    while (t && i < 12) {
      var cs = getComputedStyle(t);
      var cls = (typeof t.className === 'string' && t.className)
        ? t.className.split(/\s+/).slice(0, 3).join('.') : '';
      var bits = ['<' + t.tagName.toLowerCase() + '>' + (cls ? '.' + cls : '')];
      if (cs.backgroundColor && cs.backgroundColor !== 'rgba(0, 0, 0, 0)')
        bits.push('bg:' + cs.backgroundColor);
      if (cs.backgroundImage && cs.backgroundImage !== 'none')
        bits.push('img:' + cs.backgroundImage.slice(0, 60));
      out.push(bits.join(' '));
      t = t.parentElement; i++;
    }
    probeOut.textContent = out.join('\n');
    var btns = panelEl.querySelectorAll('.zbg-btn');
    for (var j = 0; j < btns.length; j++)
      if (btns[j].textContent.indexOf('探测') === 0 || btns[j].textContent.indexOf('取色') === 0)
        btns[j].textContent = '取色探针';
  }, true);

  buildPanel();
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      bootApply(); tick(); setInterval(tick, 2000);
    });
  } else {
    bootApply(); tick(); setInterval(tick, 2000);
  }
})();
