from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return ['home', 'login', 'password_reset']

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return {'home': 1.0, 'login': 0.9, 'password_reset': 0.8}[item]
