<script>
  import { onMount } from "svelte";

  let programs = [];
  let loading = false;
  let expandedPrograms = {};
  let expandedLocations = {};
  let locationsByPrefix = {};
  let parksByDescriptor = {};
  let loadingLocations = {};
  let loadingParks = {};
  let refreshingPrograms = false;
  let refreshingLocations = {};

  async function fetchPrograms() {
    loading = true;
    try {
      const res = await fetch("/api/pota/programs");
      if (res.ok) programs = await res.json();
    } catch {}
    loading = false;
  }

  async function toggleProgram(prefix) {
    if (expandedPrograms[prefix]) {
      expandedPrograms[prefix] = false;
      expandedPrograms = expandedPrograms;
      return;
    }
    expandedPrograms[prefix] = true;
    expandedPrograms = expandedPrograms;

    if (!locationsByPrefix[prefix]) {
      loadingLocations[prefix] = true;
      loadingLocations = loadingLocations;
      try {
        const res = await fetch(`/api/pota/programs/${prefix}/locations`);
        if (res.ok) locationsByPrefix[prefix] = await res.json();
      } catch {}
      loadingLocations[prefix] = false;
      loadingLocations = loadingLocations;
    }
  }

  async function toggleLocation(descriptor) {
    if (expandedLocations[descriptor]) {
      expandedLocations[descriptor] = false;
      expandedLocations = expandedLocations;
      return;
    }
    expandedLocations[descriptor] = true;
    expandedLocations = expandedLocations;

    if (!parksByDescriptor[descriptor]) {
      loadingParks[descriptor] = true;
      loadingParks = loadingParks;
      try {
        const res = await fetch(`/api/pota/locations/${descriptor}/parks`);
        if (res.ok) parksByDescriptor[descriptor] = await res.json();
      } catch {}
      loadingParks[descriptor] = false;
      loadingParks = loadingParks;
    }
  }

  async function refreshPrograms() {
    refreshingPrograms = true;
    try {
      await fetch("/api/pota/refresh/programs", { method: "POST" });
      locationsByPrefix = {};
      await fetchPrograms();
    } catch {}
    refreshingPrograms = false;
  }

  async function refreshLocationParks(descriptor, e) {
    e.stopPropagation();
    refreshingLocations[descriptor] = true;
    refreshingLocations = refreshingLocations;
    try {
      await fetch(`/api/pota/refresh/locations/${descriptor}`, { method: "POST" });
      const res = await fetch(`/api/pota/locations/${descriptor}/parks`);
      if (res.ok) parksByDescriptor[descriptor] = await res.json();
    } catch {}
    refreshingLocations[descriptor] = false;
    refreshingLocations = refreshingLocations;
    // Update park counts in location list
    const prefix = descriptor.split("-")[0];
    if (locationsByPrefix[prefix]) {
      try {
        const res = await fetch(`/api/pota/programs/${prefix}/locations`);
        if (res.ok) locationsByPrefix[prefix] = await res.json();
      } catch {}
    }
  }

  onMount(fetchPrograms);
</script>

<section class="parks">
  <div class="parks-header">
    <h2>POTA Parks</h2>
    <button class="refresh-btn" on:click={refreshPrograms} disabled={refreshingPrograms} title="Refresh all programs & locations">
      {refreshingPrograms ? "..." : "↻"}
    </button>
  </div>

  {#if loading}
    <p class="loading">Fetching programs...</p>
  {:else}
    <div class="tree">
      {#each programs as prog}
        <div class="tree-node">
          <!-- svelte-ignore a11y-click-events-have-key-events -->
          <!-- svelte-ignore a11y-no-static-element-interactions -->
          <div class="tree-row program-row" on:click={() => toggleProgram(prog.prefix)}>
            <span class="chevron" class:expanded={expandedPrograms[prog.prefix]}>▶</span>
            <span class="prefix">{prog.prefix}</span>
            <span class="name">{prog.name}</span>
            {#if prog.location_count > 0}
              <span class="badge">{prog.location_count} loc</span>
            {/if}
          </div>

          {#if expandedPrograms[prog.prefix]}
            <div class="children">
              {#if loadingLocations[prog.prefix]}
                <p class="loading indent">Loading locations...</p>
              {:else if locationsByPrefix[prog.prefix]}
                {#each locationsByPrefix[prog.prefix] as loc}
                  <div class="tree-node">
                    <!-- svelte-ignore a11y-click-events-have-key-events -->
                    <!-- svelte-ignore a11y-no-static-element-interactions -->
                    <div class="tree-row location-row" on:click={() => toggleLocation(loc.descriptor)}>
                      <span class="chevron" class:expanded={expandedLocations[loc.descriptor]}>▶</span>
                      <span class="descriptor">{loc.descriptor}</span>
                      <span class="name">{loc.name}</span>
                      {#if loc.park_count > 0}
                        <span class="badge">{loc.park_count} parks</span>
                      {/if}
                      <button class="refresh-btn small" on:click={(e) => refreshLocationParks(loc.descriptor, e)} disabled={refreshingLocations[loc.descriptor]} title="Refresh parks for {loc.descriptor}">
                        {refreshingLocations[loc.descriptor] ? "..." : "↻"}
                      </button>
                    </div>

                    {#if expandedLocations[loc.descriptor]}
                      <div class="children">
                        {#if loadingParks[loc.descriptor]}
                          <p class="loading indent">Fetching parks...</p>
                        {:else if parksByDescriptor[loc.descriptor]}
                          {#if parksByDescriptor[loc.descriptor].length === 0}
                            <p class="empty indent">No parks found</p>
                          {:else}
                            {#each parksByDescriptor[loc.descriptor] as park}
                              <div class="tree-row park-row">
                                <span class="park-ref">{park.reference}</span>
                                <span class="park-name">{park.name}</span>
                                {#if park.grid}
                                  <span class="park-grid">{park.grid}</span>
                                {/if}
                                {#if park.activations}
                                  <span class="park-stat">{park.activations} act</span>
                                {/if}
                              </div>
                            {/each}
                          {/if}
                        {/if}
                      </div>
                    {/if}
                  </div>
                {/each}
              {/if}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</section>

<style>
  .parks {
    padding: 0;
  }

  .parks-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  h2 {
    margin: 0;
    color: var(--accent);
    font-size: 1.2rem;
  }

  .loading {
    color: var(--text-muted);
    font-style: italic;
  }

  .empty {
    color: var(--text-dim);
    font-style: italic;
  }

  .indent {
    margin-left: 2rem;
  }

  .tree {
    display: flex;
    flex-direction: column;
  }

  .tree-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0.4rem;
    cursor: pointer;
    border-radius: 3px;
    white-space: nowrap;
    overflow: hidden;
  }

  .tree-row:hover {
    background: var(--row-hover);
  }

  .park-row {
    cursor: default;
    padding-left: 1rem;
  }

  .children {
    margin-left: 1.2rem;
  }

  .chevron {
    display: inline-block;
    font-size: 0.7rem;
    transition: transform 0.15s;
    color: var(--text-dim);
    width: 0.8rem;
    flex-shrink: 0;
  }

  .chevron.expanded {
    transform: rotate(90deg);
  }

  .prefix, .descriptor {
    color: var(--accent-callsign);
    font-weight: bold;
    flex-shrink: 0;
  }

  .name {
    color: var(--text);
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .badge {
    font-size: 0.75rem;
    color: var(--text-dim);
    background: var(--bg-deep);
    padding: 0.05rem 0.4rem;
    border-radius: 8px;
    flex-shrink: 0;
  }

  .park-ref {
    color: var(--accent-vfo);
    font-weight: bold;
    flex-shrink: 0;
    min-width: 7ch;
  }

  .park-name {
    color: var(--text);
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .park-grid {
    color: var(--text-muted);
    font-size: 0.85rem;
    flex-shrink: 0;
  }

  .park-stat {
    color: var(--text-dim);
    font-size: 0.8rem;
    flex-shrink: 0;
  }

  .refresh-btn {
    background: none;
    border: 1px solid var(--border);
    color: var(--text-muted);
    font-size: 1rem;
    cursor: pointer;
    border-radius: 3px;
    padding: 0.1rem 0.4rem;
    line-height: 1;
  }

  .refresh-btn:hover:not(:disabled) {
    background: var(--row-hover);
    color: var(--text);
  }

  .refresh-btn:disabled {
    opacity: 0.5;
    cursor: default;
  }

  .refresh-btn.small {
    font-size: 0.8rem;
    padding: 0 0.3rem;
    margin-left: auto;
  }
</style>
