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
  let uploadFiles: File[] = []
  let uploadMessage = ''
  let uploadError = ''
  let isUploading = false
  let isDragActive = false
  let fileInputRef: HTMLInputElement | null = null

  const runSearch = async () => {
    errorMessage = ''
    results = []
    const params = new URLSearchParams({
      variant: variantQuery.trim(),
      gene: geneQuery.trim(),
      dbsnp: dbsnpQuery.trim(),
    })

    if (![...params.values()].some((value) => value.length > 0)) {
      errorMessage = 'Vyplňte alespoň jedno vyhledávací pole.'
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
    if (uploadFiles.length === 0) {
      uploadError = 'Vyberte soubor pro nahrání.'
      return
    }

    const formData = new FormData()
    uploadFiles.forEach((file) => formData.append('file', file))

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
      const payload = (await response.json()) as { filename?: string; filenames?: string[] }
      if (payload.filenames && payload.filenames.length > 0) {
        uploadMessage = `Nahráno souborů: ${payload.filenames.length}.`
      } else if (payload.filename) {
        uploadMessage = `Soubor ${payload.filename} byl nahrán.`
      } else {
        uploadMessage = 'Soubor(y) byly nahrány.'
      }
      uploadFiles = []
      if (fileInputRef) {
        fileInputRef.value = ''
      }
    } catch (error) {
      uploadError = error instanceof Error ? error.message : 'Upload failed.'
    } finally {
      isUploading = false
    }
  }

  const acceptFiles = (files: File[]) => {
    uploadMessage = ''
    uploadError = ''
    uploadFiles = files
  }

  const appendFiles = (files: File[]) => {
    if (files.length === 0) {
      return uploadFiles
    }
    uploadMessage = ''
    uploadError = ''
    const seen = new Set(uploadFiles.map((file) => `${file.name}-${file.size}-${file.lastModified}`))
    const merged = [...uploadFiles]
    files.forEach((file) => {
      const key = `${file.name}-${file.size}-${file.lastModified}`
      if (!seen.has(key)) {
        seen.add(key)
        merged.push(file)
      }
    })
    uploadFiles = merged
    return merged
  }

  const clearSelectedFile = () => {
    uploadMessage = ''
    uploadError = ''
    uploadFiles = []
    if (fileInputRef) {
      fileInputRef.value = ''
    }
  }

  const removeFile = (index: number) => {
    uploadFiles = uploadFiles.filter((_, itemIndex) => itemIndex !== index)
    if (uploadFiles.length === 0) {
      clearSelectedFile()
    }
  }

  const handleFileChange = (event: Event) => {
    const target = event.currentTarget as HTMLInputElement
    appendFiles(target.files ? Array.from(target.files) : [])
  }

  const handleDrop = (event: DragEvent) => {
    event.preventDefault()
    isDragActive = false
    const droppedFiles = event.dataTransfer?.files
      ? Array.from(event.dataTransfer.files)
      : []
    const mergedFiles = appendFiles(droppedFiles)
    if (fileInputRef) {
      const dataTransfer = new DataTransfer()
      mergedFiles.forEach((file) => dataTransfer.items.add(file))
      fileInputRef.files = dataTransfer.files
    }
  }

  const handleDragOver = (event: DragEvent) => {
    event.preventDefault()
    isDragActive = true
  }

  const handleDragLeave = () => {
    isDragActive = false
  }

  const openFileDialog = () => {
    fileInputRef?.click()
  }

  const handleDropzoneKeydown = (event: KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      openFileDialog()
    }
  }

  const categoryClass = (value: string) => {
    const code = value.trim()
    if (code === '0') return 'category c0'
    if (code === '1') return 'category c1'
    if (code === '1-2') return 'category c1-2'
    if (code === '2') return 'category c2'
    if (code === '2-3') return 'category c2-3'
    if (code === '3') return 'category c3'
    if (code === '3-4') return 'category c3-4'
    if (code === '4') return 'category c4'
    if (code === '4-5') return 'category c4-5'
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
        <h1>Klinický registr variant</h1>
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
      <h2>Nahrání Dat</h2>
      <p>
        Nahrajte Excel z vaší analýzy. Soubor bude zpracován a nahrán do databáze.
      </p>
      <div class="upload-panel">
        <div
          class={`dropzone ${isDragActive ? 'drag-active' : ''}`}
          role="button"
          tabindex="0"
          on:click={openFileDialog}
          on:keydown={handleDropzoneKeydown}
          on:dragover={handleDragOver}
          on:dragleave={handleDragLeave}
          on:drop={handleDrop}
        >
          <input
            bind:this={fileInputRef}
            class="file-input"
            type="file"
            accept=".xlsx,.xls,.csv"
            multiple
            on:change={handleFileChange}
          />
          <div class="dropzone-content">
            <span class="dropzone-title">Přetáhněte soubor nebo</span>
            <span class="browse-button">Vybrat soubor</span>
            <span class="dropzone-hint">Podporuje .xlsx, .xls, .csv</span>
          </div>
          <div class="file-meta">
            <span class="file-name">
              {uploadFiles.length > 0
                ? `Vybráno souborů: ${uploadFiles.length}`
                : 'Soubor nevybrán'}
            </span>
            {#if uploadFiles.length > 0}
              <button
                type="button"
                class="clear-file"
                aria-label="Odebrat všechny soubory"
                on:click|stopPropagation={clearSelectedFile}
              >
                Odebrat vše
              </button>
            {/if}
          </div>
          {#if uploadFiles.length > 0}
            <ul class="file-list">
              {#each uploadFiles as file, index}
                <li class="file-item">
                  <span>{file.name}</span>
                  <button
                    type="button"
                    class="remove-file"
                    aria-label={`Odebrat ${file.name}`}
                    on:click|stopPropagation={() => removeFile(index)}
                  >
                    Odebrat
                  </button>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
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
          <h2>Výsledky hledání</h2>
          <p class="muted">Shodující se varianty z vašeho datasetu</p>
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
            <span class="muted">Žádná shoda</span>
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
