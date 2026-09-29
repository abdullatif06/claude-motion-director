// Demo scene 1 of 2: masked title rise, and a line that grows from the handoff dot
// and collapses back into it. Replace with the approved shot list.
MS.scene("intro", (s) => {
  const { L, u, w } = s;
  const cx = L.W / 2, cy = L.H / 2;
  const h = L.u * 1.2;          // line thickness = handoff dot size
  const full = L.u * 40;        // full line width

  s.el.innerHTML = `<h1 class="title intro-title">Motion Studio</h1><div class="line"></div>`;
  const title = s.$(".intro-title");
  const line = s.$(".line");

  // Layout (reframe, don't crop): title sits just above the centre line.
  Object.assign(title.style, { position: "absolute", left: 0, right: 0, bottom: `calc(50% + ${u(4)})`, fontSize: w(L.wide ? 7 : 10) });
  Object.assign(line.style, { top: cy - h / 2 + "px", height: h + "px" });

  // Words rise on the beat, then leave upward before the handoff.
  s.rise(title, 0.5, 1, 4.25);

  // The line: dot -> full width -> dot. Width has several targets, so it uses track().
  const widths = [[0, h], [s.at(2.5), full], [s.at(5), h]];
  s.frame((t) => {
    const wd = MS.track(t, widths, "snappy");
    line.style.left = cx - wd / 2 + "px";
    line.style.width = wd + "px";
  });
});
