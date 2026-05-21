import os
import tempfile

import polars as pl
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from core.management.commands.init_db import parse_df, sheet_exists
from core.models import PatientVariant


def search_variants(request):
	variant = request.GET.get("variant", "").strip()
	gene = request.GET.get("gene", "").strip()
	dbsnp = request.GET.get("dbsnp", "").strip()

	if not (variant or gene or dbsnp):
		return JsonResponse({"results": []})

	filters = Q()
	if gene:
		filters &= Q(variant__gene__symbol__icontains=gene)
	if dbsnp:
		filters &= Q(variant__dbsnp__icontains=dbsnp)
	if variant:
		filters &= (
			Q(variant__hgvs_c__icontains=variant)
			| Q(variant__hgvs_p__icontains=variant)
			| Q(variant__variation_type__icontains=variant)
		)

	queryset = (
		PatientVariant.objects.select_related("variant__gene", "report")
		.filter(filters)
		.order_by("-report__updated_at")[:200]
	)

	results = [
		{
			"gene": item.variant.gene.symbol,
			"variant": item.variant.hgvs_c,
			"dbsnp": item.variant.dbsnp,
			"chromosome": item.variant.chromosome,
			"position": item.variant.position,
			"updated_at": item.report.updated_at.isoformat(),
			"category": item.category or "",
		}
		for item in queryset
	]

	return JsonResponse({"results": results})


@require_POST
def upload_variants_file(request):
	uploaded = request.FILES.get("file")
	if not uploaded:
		return JsonResponse({"error": "No file provided."}, status=400)

	allowed_extensions = {".xlsx", ".xls"}
	name = uploaded.name
	name_lower = name.lower()
	if not any(name_lower.endswith(ext) for ext in allowed_extensions):
		return JsonResponse({"error": "Unsupported file type."}, status=400)

	suffix = os.path.splitext(name_lower)[1]
	with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
		for chunk in uploaded.chunks():
			tmp_file.write(chunk)
		tmp_path = tmp_file.name

	try:
		if suffix == ".xlsx" and sheet_exists(tmp_path, "default"):
			df = pl.read_excel(tmp_path, sheet_name="default")
		else:
			try:
				df = pl.read_excel(tmp_path, sheet_name="Filtr JI")
			except Exception:
				df = pl.read_excel(tmp_path)

		with transaction.atomic():
			parse_df(df)
		row_count = df.height
	finally:
		os.unlink(tmp_path)

	return JsonResponse({"filename": name, "rows": row_count})
