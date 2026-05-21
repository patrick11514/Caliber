<script lang="ts">
  type Variant = {
    gene: string
    variant: string
    dbsnp: string
    chromosome: string
    position: number | null
    updated_at: string
    category: string
  }

  type SearchResponse = {
    results: Variant[]
  }

  let variantQuery = ''
  let geneQuery = ''
  let dbsnpQuery = ''
  let isSearching = false
  let errorMessage = ''
  let results: Variant[] = []
  let uploadFile: File | null = null
  let uploadMessage = ''
  let uploadError = ''
  let isUploading = false

  const runSearch = async () => {
    errorMessage = ''
    results = []
    const params = new URLSearchParams({
      variant: variantQuery.trim(),
      gene: geneQuery.trim(),
      dbsnp: dbsnpQuery.trim(),
    })

    if (![...params.values()].some((value) => value.length > 0)) {
      errorMessage = 'Enter at least one search field.'
      return
    }

    isSearching = true
    try {
      const response = await fetch(`/api/search/?${params.toString()}`)
      if (!response.ok) {
        throw new Error('Search failed. Please try again.')
      }
      const data = (await response.json()) as SearchResponse
      results = data.results
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : 'Search failed.'
    } finally {
      isSearching = false
    }
  }

  const clearSearch = () => {
    variantQuery = ''
    geneQuery = ''
    dbsnpQuery = ''
    errorMessage = ''
    results = []
  }

  const formatDate = (value: string) => {
    if (!value) {
      return '—'
    }
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) {
      return '—'
    }
    const day = String(date.getDate()).padStart(2, '0')
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const year = String(date.getFullYear())
    return `${day}-${month}-${year}`
  }

  const getCookie = (name: string) => {
    const cookie = document.cookie
      .split(';')
      .map((value) => value.trim())
      .find((value) => value.startsWith(`${name}=`))
    return cookie ? decodeURIComponent(cookie.split('=')[1]) : ''
  }

  const handleUpload = async () => {
    uploadMessage = ''
    uploadError = ''
    if (!uploadFile) {
      uploadError = 'Vyberte soubor pro nahrání.'
      return
    }

    const formData = new FormData()
    formData.append('file', uploadFile)

    isUploading = true
    try {
      const response = await fetch('/api/upload/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: formData,
      })
      if (!response.ok) {
        const payload = (await response.json()) as { error?: string }
        throw new Error(payload.error || 'Upload failed.')
      }
      const payload = (await response.json()) as { filename: string }
      uploadMessage = `Soubor ${payload.filename} byl nahrán.`
      uploadFile = null
    } catch (error) {
      uploadError = error instanceof Error ? error.message : 'Upload failed.'
    } finally {
      isUploading = false
    }
  }

  const categoryClass = (value: string) => {
    const code = value.trim()
    if (code === '0') return 'category c0'
    if (code === '1') return 'category c1'
    if (code === '2') return 'category c2'
    if (code === '3') return 'category c3'
    if (code === '4') return 'category c4'
    if (code === '5') return 'category c5'
    return 'category'
  }
</script>

<div class="page">
  <header class="topbar">
    <div class="brand">
      <div class="mark" aria-hidden="true">
        <span></span>
        <span></span>
        <span></span>
      </div>
      <div>
        <p class="eyebrow">Caliber</p>
        <h1>Clinical Variant Registry</h1>
      </div>
    </div>
    <div class="status">
      <span class="dot"></span>
      Data sync: 21 May 2026
    </div>
  </header>

  <section class="search">
    <div>
      <p class="label">Vyhledat podle varianty, genu nebo dbSNP</p>
      <form class="search-form" on:submit|preventDefault={runSearch}>
        <label class="field">
          <span>Varianta</span>
          <input
            type="text"
            placeholder="NM_004168.3:c.1396G>A nebo c.1396G>A"
            bind:value={variantQuery}
          />
        </label>
        <label class="field">
          <span>Gen</span>
          <input type="text" placeholder="BRCA1" bind:value={geneQuery} />
        </label>
        <label class="field">
          <span>dbSNP</span>
          <input type="text" placeholder="rs80357713" bind:value={dbsnpQuery} />
        </label>
        <div class="actions">
          <button type="submit" class="ghost" disabled={isSearching}>
            {isSearching ? 'Hledání...' : 'Vyhledat'}
          </button>
          <button type="button" class="ghost" on:click={clearSearch}>
            Vymazat hledání
          </button>
        </div>
      </form>
      {#if errorMessage}
        <p class="error">{errorMessage}</p>
      {/if}
    </div>
    <div class="card hero">
      <h2>Nahrání Excelu</h2>
      <p>
        Nahrajte Excel nebo CSV z vaší analýzy. Soubor uložíme
        a připravíme ke zpracování.
      </p>
      <div class="upload-panel">
        <input
          type="file"
          accept=".xlsx,.xls,.csv"
          on:change={(event) => {
            const target = event.currentTarget as HTMLInputElement
            uploadFile = target.files ? target.files[0] : null
          }}
        />
        <div class="hero-actions">
          <button type="button" class="ghost" disabled={isUploading} on:click={handleUpload}>
            {isUploading ? 'Nahrávám...' : 'Nahrát soubor'}
          </button>
        </div>
        {#if uploadMessage}
          <p class="success">{uploadMessage}</p>
        {/if}
        {#if uploadError}
          <p class="error">{uploadError}</p>
        {/if}
      </div>
    </div>
  </section>

  <section class="grid">
    <div class="card list">
      <div class="list-head">
        <div>
          <h2>Search results</h2>
          <p class="muted">Matching variants from your dataset</p>
        </div>
        <button type="button" class="ghost" on:click={runSearch}>
          Obnovit
        </button>
      </div>
      <div class="table">
        <div class="row head">
          <span>Gen</span>
          <span>Varianta</span>
          <span>dbSNP</span>
          <span>Chromozom</span>
          <span>Pozice</span>
          <span>Aktualizováno</span>
          <span>Kategorie</span>
        </div>
        {#if results.length === 0}
          <div class="row empty">
            <span class="muted">No results yet. Try a search above.</span>
          </div>
        {:else}
          {#each results as item}
            <div class="row">
              <span class="pill">{item.gene}</span>
              <span>{item.variant || '—'}</span>
              <span>{item.dbsnp || '—'}</span>
              <span>{item.chromosome || '—'}</span>
              <span>{item.position ?? '—'}</span>
              <span>{formatDate(item.updated_at)}</span>
              <span class={categoryClass(item.category)}>{item.category || '—'}</span>
            </div>
          {/each}
        {/if}
      </div>
    </div>

    <!-- <aside class="card side">
      <h2>Signals</h2>
      <p class="muted">Highlights from ClinVar sync and internal curation.</p>
      <div class="signal">
        <h3>12 new ClinVar updates</h3>
        <p>New classifications applied to BRCA1 and TP53 variants.</p>
      </div>
      <div class="signal">
        <h3>3 patients flagged</h3>
        <p>Awaiting confirmation on zygosity and lab notes.</p>
      </div>
      <div class="signal">
        <h3>Review backlog</h3>
        <p>18 variants still pending clinical sign-off.</p>
      </div>
      <button type="button" class="ghost full">Open review queue</button>
    </aside> -->
  </section>
</div>
