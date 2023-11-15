from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from datetime import datetime

class StaticViewSitemap(Sitemap):
	changefreq = 'daily'
	priority = 0.5
	
	def lastmod(self, item):
		return datetime.now()

	def items(self):
		return ['game']

	def location(self, item):
		return reverse(item)