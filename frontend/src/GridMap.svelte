<script>
  import { createEventDispatcher } from "svelte";
  export let value = "";

  const dispatch = createEventDispatcher();

  let level = "field"; // "field" or "square"
  let selectedField = "";

  // Maidenhead: 18 longitude fields (A-R) x 18 latitude fields (A-R)
  const LETTERS = "ABCDEFGHIJKLMNOPQR".split("");

  // Convert field to lon/lat of its SW corner
  function fieldToLonLat(lonIdx, latIdx) {
    return {
      lon: lonIdx * 20 - 180,
      lat: latIdx * 10 - 90,
    };
  }

  function squareToLonLat(fieldLonIdx, fieldLatIdx, sqLon, sqLat) {
    const base = fieldToLonLat(fieldLonIdx, fieldLatIdx);
    return {
      lon: base.lon + sqLon * 2,
      lat: base.lat + sqLat * 1,
    };
  }

  // Parse a grid value to determine what's selected
  $: parsedField = value.length >= 2 ? value.substring(0, 2).toUpperCase() : "";
  $: parsedSquare = value.length >= 4 ? value.substring(0, 4).toUpperCase() : "";

  let fieldLonIdx = 0;
  let fieldLatIdx = 0;

  function selectField(lonIdx, latIdx) {
    fieldLonIdx = lonIdx;
    fieldLatIdx = latIdx;
    selectedField = LETTERS[lonIdx] + LETTERS[latIdx];
    level = "square";
  }

  // SVG coordinates for the selected field (used for zoomed view)
  $: fieldX = (fieldLonIdx / 18) * 100;
  $: fieldY = ((17 - fieldLatIdx) / 18) * 100;
  $: fieldW = 100 / 18;
  $: fieldH = 100 / 18;

  function selectSquare(sqLon, sqLat) {
    const grid = selectedField + sqLon + sqLat;
    value = grid;
    dispatch("select", grid);
    level = "field";
  }

  function backToFields() {
    level = "field";
  }

  // Determine color for a field cell
  function fieldClass(lonIdx, latIdx) {
    const code = LETTERS[lonIdx] + LETTERS[latIdx];
    if (code === parsedField) return "selected";
    // Highlight land-heavy areas slightly
    return "";
  }

</script>

<div class="gridmap">
  {#if level === "field"}
    <div class="map-header">
      <span class="map-title">Select Grid Field</span>
      {#if parsedField}
        <span class="current">Current: {value}</span>
      {/if}
    </div>
    <svg viewBox="0 0 100 100" class="map-svg">
      <!-- World map background from Natural Earth / Wikimedia -->
      <image
        href="/world-map.jpg"
        x="0" y="0" width="100" height="100"
        preserveAspectRatio="none"
        opacity="0.4"
      />
      <!-- Grid fields -->
      {#each LETTERS as lonL, lonIdx}
        {#each LETTERS as latL, latIdx}
          {@const code = LETTERS[lonIdx] + LETTERS[latIdx]}
          {@const x = (lonIdx / 18) * 100}
          {@const y = ((17 - latIdx) / 18) * 100}
          {@const w = 100 / 18}
          {@const h = 100 / 18}
          <rect
            {x} {y} width={w} height={h}
            class="cell"
            class:selected={code === parsedField}
            on:click={() => selectField(lonIdx, latIdx)}
          />
          <text
            x={x + w / 2}
            y={y + h / 2}
            class="cell-label"
            class:selected-text={code === parsedField}
          >{code}</text>
        {/each}
      {/each}
    </svg>
  {:else}
    <div class="map-header">
      <button class="back-btn" on:click={backToFields}>← Back</button>
      <span class="map-title">{selectedField} — Select Square</span>
      {#if parsedSquare}
        <span class="current">Current: {value}</span>
      {/if}
    </div>
    <svg viewBox="{fieldX} {fieldY} {fieldW} {fieldH}" class="map-svg zoomed">
      <!-- Same world map, zoomed to field -->
      <image
        href="/world-map.jpg"
        x="0" y="0" width="100" height="100"
        preserveAspectRatio="none"
        opacity="0.4"
      />
      <!-- 10x10 square grid -->
      {#each Array(10) as _, lonIdx}
        {#each Array(10) as _, latIdx}
          {@const code = selectedField + lonIdx + (9 - latIdx)}
          {@const sx = fieldX + (lonIdx / 10) * fieldW}
          {@const sy = fieldY + (latIdx / 10) * fieldH}
          {@const sw = fieldW / 10}
          {@const sh = fieldH / 10}
          <rect
            x={sx} y={sy} width={sw} height={sh}
            class="cell"
            class:selected={code === parsedSquare}
            on:click={() => selectSquare(lonIdx, 9 - latIdx)}
          />
          <text
            x={sx + sw / 2}
            y={sy + sh / 2}
            class="sq-label"
            class:selected-text={code === parsedSquare}
          >{lonIdx}{9 - latIdx}</text>
        {/each}
      {/each}
    </svg>
  {/if}
</div>

<style>
  .gridmap {
    width: 100%;
    max-width: 600px;
  }

  .map-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .map-title {
    color: var(--accent);
    font-weight: bold;
    font-size: 0.9rem;
  }

  .current {
    color: var(--text-muted);
    font-size: 0.8rem;
    margin-left: auto;
  }

  .back-btn {
    background: var(--btn-secondary);
    color: var(--text);
    border: none;
    padding: 0.2rem 0.5rem;
    font-family: inherit;
    font-size: 0.75rem;
    border-radius: 3px;
    cursor: pointer;
  }

  .back-btn:hover {
    background: var(--btn-secondary-hover);
  }

  .map-svg {
    width: 100%;
    background: var(--bg-deep);
    border: 1px solid var(--border);
    border-radius: 4px;
  }

  .cell {
    fill: transparent;
    stroke: var(--border);
    stroke-width: 0.1;
    cursor: pointer;
    opacity: 0.8;
  }

  .cell:hover {
    fill: var(--accent);
    opacity: 0.3;
  }

  .cell.selected {
    fill: var(--accent);
    opacity: 0.4;
  }

  .cell-label {
    font-size: 1.8px;
    fill: var(--text-dim);
    text-anchor: middle;
    dominant-baseline: central;
    pointer-events: none;
    font-family: inherit;
  }

  .cell-label.selected-text {
    fill: var(--accent);
    font-weight: bold;
  }

  .sq-label {
    font-size: 0.25px;
    fill: var(--text-muted);
    text-anchor: middle;
    dominant-baseline: central;
    pointer-events: none;
    font-family: inherit;
  }

  .sq-label.selected-text {
    fill: var(--accent);
    font-weight: bold;
  }

</style>
