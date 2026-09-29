// Demo scene 2 of 2: the handoff dot stretches into a tab indicator that hops tab to
// tab (leading edge stiffer than trailing, so it stretches), under a log-space camera
// push, then collapses back into the dot. Last frame = first frame of the film: it loops.
MS.scene("tabs", (s) => {
  const { L, u, w } = s;
  const cx = L.W / 2, cy = L.H / 2;
  const h = L.u * 1.2;                                  // same dot as the intro's line
  const tabW = L.wide ? L.W * 0.14 : L.W * 0.26;        // fixed width: no text measuring
  const rowL = cx - 1.5 * tabW;

  s.el.innerHTML = `
    <div class="stage">
      <div class="tabrow"><div class="tab">Brief</div><div class="tab">Build</div><div class="tab">Ship</div></div>
      <div class="line"></div>
    </div>`;
  const stage = s.$(".stage");
  const row = s.$(".tabrow");
  const line = s.$(".line");

  Object.assign(row.style, { left: rowL + "px", bottom: `calc(50% + ${u(2)})` });
  s.$$(".tab").forEach((el) => Object.assign(el.style, { width: tabW + "px", fontSize: w(L.wide ? 2.6 : 4.6) }));
  Object.assign(line.style, { top: cy - h / 2 + "px", height: h + "px" });

  // Labels rise in after the dot opens, and leave before it closes.
  s.$$(".tab").forEach((tab) => s.rise(tab, 0.6, 1, 4.4));

  // Edges tracked separately: the leading edge is snappy, the trailing edge heavy.
  const left = [[0, cx - h / 2], [s.at(0.5), rowL], [s.at(2), rowL], [s.at(3), rowL + tabW], [s.at(4), rowL + 2 * tabW], [s.at(5), cx - h / 2]];
  const right = [[0, cx + h / 2], [s.at(0.5), rowL + 3 * tabW], [s.at(2), rowL + tabW], [s.at(3), rowL + 2 * tabW], [s.at(4), rowL + 3 * tabW], [s.at(5), cx + h / 2]];

  // Zoom only as far as the frame allows: the row must stay inside the safe area.
  const maxZoom = Math.min(1.3, (L.W - 2 * L.pad.x) / (tabW * 3));

  s.frame((t) => {
    const a = MS.track(t, left, "heavy"), b = MS.track(t, right, "snappy");
    line.style.left = Math.min(a, b) + "px";
    line.style.width = Math.max(h, Math.abs(b - a)) + "px";
    stage.style.transform = `scale(${MS.zoom(t, [[0, 1], [s.at(1), maxZoom], [s.at(4.2), 1]])})`;
  });
});
