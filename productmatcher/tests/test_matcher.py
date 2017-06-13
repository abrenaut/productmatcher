# -*- coding: utf-8 -*-

import unittest
from productmatcher import matcher


class TestMatcher(unittest.TestCase):

    def setUp(self):
        self.products = [
            {'model': 'SX130 IS',
             'announced-date': '2010-08-18T20:00:00.000-04:00',
             'product_name': 'Canon_PowerShot_SX130_IS',
             'family': 'PowerShot', 'manufacturer': 'Canon'},
            {'model': 'DMC-TS3',
             'announced-date': '2011-01-24T19:00:00.000-05:00',
             'product_name': 'Panasonic-DMC-TS3',
             'family': 'Lumix', 'manufacturer': 'Panasonic'},
            {'model': 'DSC-W310',
             'announced-date': '2010-01-06T19:00:00.000-05:00',
             'product_name': 'Sony_Cyber-shot_DSC-W310',
             'family': 'Cyber-shot', 'manufacturer': 'Sony'}]
        self.listings = [
            {'currency': 'CAD', 'price': '35.99',
             'manufacturer': 'Neewer Electronics Accessories',
             'title': 'LED Flash Macro Ring Light (48 X LED) with 6 Adapter '
             'Rings for For Canon/Sony/Nikon/Sigma Lenses'},
            {'currency': 'CAD', 'price': '199.96',
             'manufacturer': 'Canon Canada',
             'title': 'Canon PowerShot SX130IS 12.1 MP'},
            {'currency': 'CAD', 'price': '209.00',
             'manufacturer': 'Canon Canada',
             'title': 'Canon PowerShot SX130IS 12.1 MP'},
            {'currency': 'CAD', 'price': '399.99', 'manufacturer': 'Panasonic',
             'title': 'Panasonic Lumix DMC-TS3'}]

    def test_normalize(self):
        normalized_str = matcher.normalize('Canon_PowerShot_SX130 IS')
        self.assertEqual(normalized_str, 'canonpowershotsx130is')

    def test_match_products_with_listings(self):
        results = matcher.match_products_with_listings(
            self.products, self.listings)
        self.assertEqual(
            2, len(results['Canon_PowerShot_SX130_IS']['listings']))
        self.assertEqual(
            1, len(results['Panasonic-DMC-TS3']['listings']))
        self.assertNotIn('Sony_Cyber-shot_DSC-W310', results.keys())
        self.assertEqual(2, len(results.keys()))
