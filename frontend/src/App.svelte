<script lang="ts">
  type Variant = {
    gene: string
    variant: string
    category: string
    chrom: string
    coordinate: string
    status: string
  }

  const highlights = [
    { label: 'Patients', value: '1,284' },
    { label: 'Genes', value: '3,940' },
    { label: 'Variants', value: '12,311' },
    { label: 'ClinVar Links', value: '7,502' },
  ]

  const variants: Variant[] = [
    {
      gene: 'BRCA1',
      variant: 'c.68_69delAG',
      category: 'Pathogenic',
      chrom: '17',
      coordinate: '43044295',
      status: 'Reviewed',
    },
    {
      gene: 'CFTR',
      variant: 'p.Phe508del',
      category: 'Pathogenic',
      chrom: '7',
      coordinate: '117199644',
      status: 'Reviewed',
    },
    {
      gene: 'TP53',
      variant: 'c.215C>G',
      category: 'Likely pathogenic',
      chrom: '17',
      coordinate: '7579472',
      status: 'Pending',
    },
    {
      gene: 'APOE',
      variant: 'c.388T>C',
      category: 'Risk factor',
      chrom: '19',
      coordinate: '44908684',
      status: 'Reviewed',
    },
  ]
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
      <p class="label">Find by gene, variant, patient, or ClinVar ID</p>
      <div class="search-row">
        <input type="search" placeholder="BRCA1, c.68_69delAG, ClinVar 17661" />
        <button type="button">Search</button>
      </div>
      <div class="chips">
        <button type="button">Pathogenic</button>
        <button type="button">Likely pathogenic</button>
        <button type="button">Risk factor</button>
        <button type="button">Reviewed</button>
      </div>
    </div>
    <div class="card hero">
      <h2>Curated for rapid triage</h2>
      <p>
        Track patient-linked variants, maintain ClinVar mappings, and surface the
        evidence trail in one consistent workspace.
      </p>
      <div class="hero-actions">
        <button type="button" class="ghost">Upload CSV</button>
        <button type="button">New patient</button>
      </div>
    </div>
  </section>

  <section class="metrics">
    {#each highlights as stat}
      <div class="metric">
        <p>{stat.label}</p>
        <h3>{stat.value}</h3>
      </div>
    {/each}
  </section>

  <section class="grid">
    <div class="card list">
      <div class="list-head">
        <div>
          <h2>Recent variants</h2>
          <p class="muted">Latest curated entries across patients</p>
        </div>
        <button type="button" class="ghost">View all</button>
      </div>
      <div class="table">
        <div class="row head">
          <span>Gene</span>
          <span>Variant</span>
          <span>Category</span>
          <span>Chrom</span>
          <span>Coordinate</span>
          <span>Status</span>
        </div>
        {#each variants as item}
          <div class="row">
            <span class="pill">{item.gene}</span>
            <span>{item.variant}</span>
            <span>{item.category}</span>
            <span>{item.chrom}</span>
            <span>{item.coordinate}</span>
            <span class={item.status === 'Reviewed' ? 'tag ok' : 'tag pending'}>
              {item.status}
            </span>
          </div>
        {/each}
      </div>
    </div>

    <aside class="card side">
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
    </aside>
  </section>
</div>
