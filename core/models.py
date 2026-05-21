from django.db import models


class Patient(models.Model):
    name = models.CharField(max_length=120)


class Gene(models.Model):
    symbol = models.CharField(max_length=32, unique=True)


class GeneVariant(models.Model):
    gene = models.ForeignKey(Gene, on_delete=models.PROTECT)

    chromosome = models.CharField(max_length=8)
    position = models.BigIntegerField()

    hgvs_c = models.CharField(max_length=120, blank=True)
    hgvs_p = models.CharField(max_length=120, blank=True)

    dbsnp = models.CharField(max_length=64, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["chromosome", "position", "ref", "alt"],
                name="unique_genomic_variant"
            )
        ]


class PatientVariant(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    variant = models.ForeignKey(GeneVariant, on_delete=models.CASCADE)

    exon = models.CharField(max_length=32, blank=True)
    gnomAD = models.CharField(max_length=64, blank=True)
    zygosity = models.CharField(max_length=32, blank=True)
    category = models.CharField(max_length=80, blank=True)
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = ("patient", "variant")

class ClinVarGeneVariant(models.Model):
    gene_variant = models.OneToOneField(
        GeneVariant,
        on_delete=models.CASCADE,
        related_name="clinvar_entry",
    )
    clinvar_id = models.CharField(max_length=64)
    clinvar_url = models.URLField(max_length=300)
    clinvar_category = models.CharField(max_length=80)
    
    def __str__(self):
        return f"ClinVarGeneVariant(clinvar_id={self.clinvar_id}, gene_variant={self.gene_variant})"