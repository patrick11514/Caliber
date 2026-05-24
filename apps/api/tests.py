from django.test import TestCase
from django.urls import reverse

from core.models import Gene, GeneVariant


class SearchVariantsTests(TestCase):
	def setUp(self):
		brca1 = Gene.objects.create(symbol="BRCA1")
		cftr = Gene.objects.create(symbol="CFTR")

		GeneVariant.objects.create(
			gene=brca1,
			variation_type="deletion",
			chromosome="chr17",
			position=43044295,
			hgvs_c="c.68_69delAG",
			hgvs_p="",
			dbsnp="rs80357713",
		)

		GeneVariant.objects.create(
			gene=cftr,
			variation_type="deletion",
			chromosome="chr7",
			position=117199644,
			hgvs_c="c.1521_1523delCTT",
			hgvs_p="p.Phe508del",
			dbsnp="rs113993960",
		)

	def test_empty_query_returns_no_results(self):
		response = self.client.get(reverse("search_variants"))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json(), {"results": []})

	def test_search_by_gene(self):
		response = self.client.get(
			reverse("search_variants"),
			{"gene": "brca"},
		)
		self.assertEqual(response.status_code, 200)
		results = response.json()["results"]
		self.assertEqual(len(results), 1)
		self.assertEqual(results[0]["gene"], "BRCA1")

	def test_search_by_dbsnp(self):
		response = self.client.get(
			reverse("search_variants"),
			{"dbsnp": "rs113"},
		)
		self.assertEqual(response.status_code, 200)
		results = response.json()["results"]
		self.assertEqual(len(results), 1)
		self.assertEqual(results[0]["dbsnp"], "rs113993960")

	def test_search_by_variant_hgvs(self):
		response = self.client.get(
			reverse("search_variants"),
			{"variant": "Phe508"},
		)
		self.assertEqual(response.status_code, 200)
		results = response.json()["results"]
		self.assertEqual(len(results), 1)
		self.assertEqual(results[0]["gene"], "CFTR")
