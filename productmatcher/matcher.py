# -*- coding: utf-8 -*-

import logging
import argparse
import json
import copy
import string
from difflib import SequenceMatcher
from multiprocessing import Pool, cpu_count
from functools import partial

logger = logging.getLogger('productmatcher')


"""
This variable determine how strict the matching will be when comparing a
listing manufacturer with a product manufacturer
"""
MINIMUM_MANUFACTURER_MATCH_SCORE = 0.5


def parse_args():
    parser = argparse.ArgumentParser(prog='productmatcher')

    parser.add_argument('-l', "--listings",
                        help="Path to the listings file",
                        default='listings.txt')
    parser.add_argument('-p', "--products",
                        help="Path to the products file",
                        default='products.txt')
    parser.add_argument('-o', "--output",
                        help="Path to the output file", default='output.txt')
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Don't print progress")

    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    logging.basicConfig(level=(logging.WARN if args.quiet else logging.INFO))

    # Read products and listings files
    products = read_json_lines_file(args.products)
    listings = read_json_lines_file(args.listings)

    # Match products with listings
    results = match_products_with_listings(products, listings)

    # Write the result in a json lines file
    write_json_lines_file(args.output, results.values())


def read_json_lines_file(file_path):
    with open(file_path) as f:
        content = f.readlines()
    return [json.loads(line) for line in content]


def write_json_lines_file(output_file_path, content):
    with open(output_file_path, 'w') as output_file:
        output_file.write('\n'.join([json.dumps(line) for line in content]))


def match_products_with_listings(products, listings):
    results = {}

    # Create a normalized version of the keys used in the matching process
    # and group the products by manufacturer
    products_by_manufacturer = {}
    for product in products:
        normalize_keys(product, ['model', 'manufacturer', 'product_name'])
        products_by_manufacturer.setdefault(
            product['normalized_manufacturer'], []).append(product)

    # Compute matching products and listings in parallel
    pool = Pool(cpu_count())
    func = partial(match_products_with_listing, products_by_manufacturer)
    matching_results = pool.map(func, listings)

    # Gather results
    results = {}
    for product_name, listing in matching_results:
        if product_name is not None:
            results.setdefault(product_name,
                               {'product_name': product_name,
                                'listings': []}
                               )['listings'].append(listing)

    return results


def match_products_with_listing(products_by_manufacturer, listing):
    # Create a copy of the listing with normalized keys because we don't
    # want the normalized keys to appear in the result
    normalized_listing = copy.copy(listing)
    normalize_keys(normalized_listing, ['title', 'manufacturer'])
    product = find_matching_product(
        normalized_listing, products_by_manufacturer)
    # Return the match or None if none found
    return (product['product_name'], listing) if product else (None, None)


def normalize_keys(obj, keys):
    for key in keys:
        obj['normalized_{key}'.format(key=key)] = normalize(obj[key])


def normalize(s):
    for p in string.punctuation:
        s = s.replace(p, '')
    s = s.replace(' ', '')
    return s.lower().strip()


def find_matching_product(listing, products_by_manufacturer):
    logger.info("Trying to find a match for '{listing_name}'".format(
        listing_name=listing['title']))
    matching_product = None
    max_match_score = 0
    for manufacturer, products in products_by_manufacturer.items():
        # Check if the manufacturer is identical
        s = SequenceMatcher(None,
                            listing['normalized_manufacturer'],
                            manufacturer)
        if s.ratio() > MINIMUM_MANUFACTURER_MATCH_SCORE:
            for product in products:
                # Check that the product model appears in the listing title
                if product['normalized_model'] in listing['normalized_title']:
                    s = SequenceMatcher(None,
                                        listing['normalized_title'],
                                        product['normalized_product_name'])
                    match_score = s.ratio()
                    # Keep the most relevent matches
                    if match_score > max_match_score:
                        matching_product = product
                        max_match_score = match_score

    return matching_product
