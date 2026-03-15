<script>
  let importing = false;
  let message = "";
  let messageType = "";

  function exportAdif() {
    window.location.href = "/api/adif/export";
  }

  async function importAdif(event) {
    const file = event.target.files[0];
    if (!file) return;
    importing = true;
    message = "";
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch("/api/adif/import", {
        method: "POST",
        body: formData,
      });
      if (res.ok) {
        const data = await res.json();
        message = `Imported ${data.imported} contacts.${data.skipped ? ` Skipped ${data.skipped}.` : ""}`;
        messageType = "success";
      } else {
        const data = await res.json().catch(() => null);
        message = data?.detail || `Error: ${res.status} ${res.statusText}`;
        messageType = "error";
      }
    } catch (e) {
      message = `Network error: ${e.message}`;
      messageType = "error";
    }
    importing = false;
    event.target.value = "";
  }
</script>

<div class="export-import">
  <h2>Export</h2>
  <p>Download your logbook as an ADIF (.adi) file.</p>
  <button on:click={exportAdif}>Download ADIF</button>

  <h2>Import</h2>
  <p>Import contacts from an ADIF (.adi) file. Duplicate contacts are not detected.</p>
  <label class="file-label">
    <input type="file" accept=".adi,.adif,.ADI,.ADIF" on:change={importAdif} disabled={importing} />
    {importing ? "Importing..." : "Choose ADIF File"}
  </label>

  {#if message}
    <p class="message" class:error={messageType === "error"}>{message}</p>
  {/if}
</div>

<style>
  .export-import {
    max-width: 500px;
  }

  h2 {
    color: var(--accent);
    font-size: 1.2rem;
    margin: 1.5rem 0 0.5rem 0;
  }

  h2:first-child {
    margin-top: 0;
  }

  p {
    color: var(--text-muted);
    font-size: 0.9rem;
    margin: 0 0 0.75rem 0;
  }

  button {
    background: var(--accent);
    color: var(--bg);
    border: none;
    padding: 0.5rem 1.5rem;
    font-family: inherit;
    font-size: 0.9rem;
    font-weight: bold;
    border-radius: 3px;
    cursor: pointer;
  }

  button:hover {
    background: var(--accent-hover);
  }

  .file-label {
    display: inline-block;
    background: var(--accent);
    color: var(--bg);
    padding: 0.5rem 1.5rem;
    font-family: inherit;
    font-size: 0.9rem;
    font-weight: bold;
    border-radius: 3px;
    cursor: pointer;
  }

  .file-label:hover {
    background: var(--accent-hover);
  }

  .file-label input[type="file"] {
    display: none;
  }

  .message {
    color: var(--accent);
    font-weight: bold;
    margin-top: 1rem;
  }

  .message.error {
    color: var(--accent-error);
  }
</style>
