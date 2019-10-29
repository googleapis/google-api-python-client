# Copyright 2014 Joe Gregorio
#
# Licensed under the MIT License

"""MIME-Type Parser

This module provides basic functions for handling mime-types. It can handle
matching mime-types against a list of media-ranges. See section 14.1 of the
HTTP specification [RFC 2616] for a complete explanation.

http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.1
"""
from __future__ import absolute_import
from functools import reduce
import six

__version__ = "0.1.3"
__author__ = "Joe Gregorio"
__email__ = "joe@bitworking.org"
__license__ = "MIT License"
__credits__ = ""


def parse_mime_type(mime_type):
    """Parses a mime-type into its component parts.

    Carves up a mime-type and returns a tuple of the (type, subtype, params)
    where 'params' is a dictionary of all the parameters for the media range.
    For example, the media range ``application/xhtml;q=0.5`` would get parsed
    into ``('application', 'xhtml', {'q', '0.5'})``.

    Args:
      mime_type (str): A mime-type.
    
    Returns:
      Tuple[str, str, dict]: Tuple of (type, subtype, params).

    """
    parts = mime_type.split(";")
    params = dict(
        [tuple([s.strip() for s in param.split("=", 1)]) for param in parts[1:]]
    )
    full_type = parts[0].strip()
    # Java URLConnection class sends an Accept header that includes a
    # single '*'. Turn it into a legal wildcard.
    if full_type == "*":
        full_type = "*/*"
    (type, subtype) = full_type.split("/")

    return (type.strip(), subtype.strip(), params)


def parse_media_range(range):
    """Parse a media-range into its component parts.

    Carves up a media range and returns a tuple of the (type, subtype,
    params) where 'params' is a dictionary of all the parameters for the media
    range.  For example, the media range ``application/*;q=0.5`` would get parsed
    into  ``('application', '*', {'q', '0.5'})``

    In addition this function also guarantees that there is a value for 'q'
    in the params dictionary, filling it in with a proper default if
    necessary.

    Args:
      range (str): A media-range.
    
    Returns:
      Tuple[str, str, dict]: A tuple of (type, subtype, params)
    """
    (type, subtype, params) = parse_mime_type(range)
    if (
        "q" not in params
        or not params["q"]
        or not float(params["q"])
        or float(params["q"]) > 1
        or float(params["q"]) < 0
    ):
        params["q"] = "1"

    return (type, subtype, params)


def fitness_and_quality_parsed(mime_type, parsed_ranges):
    """Find the best match for a mime-type amongst parsed media-ranges.

    Args:
      mime_type (str): A mime-type.
      parsed_ranges (List[Tuple[str, str, dict]]): A list of parsed media ranges.
    
    Returns:
      Tuple[int, float]: A tuple of the fitness value and the value of the 'q'
      quality parameter of the best match, or (-1, 0) if no match was found. 
    """
    best_fitness = -1
    best_fit_q = 0
    (target_type, target_subtype, target_params) = parse_media_range(mime_type)
    for (type, subtype, params) in parsed_ranges:
        type_match = type == target_type or type == "*" or target_type == "*"
        subtype_match = (
            subtype == target_subtype or subtype == "*" or target_subtype == "*"
        )
        if type_match and subtype_match:
            param_matches = reduce(
                lambda x, y: x + y,
                [
                    1
                    for (key, value) in six.iteritems(target_params)
                    if key != "q" and key in params and value == params[key]
                ],
                0,
            )
            fitness = (type == target_type) and 100 or 0
            fitness += (subtype == target_subtype) and 10 or 0
            fitness += param_matches
            if fitness > best_fitness:
                best_fitness = fitness
                best_fit_q = params["q"]

    return best_fitness, float(best_fit_q)


def quality_parsed(mime_type, parsed_ranges):
    """Find the best match for a mime-type amongst parsed media-ranges.

    Args:
      mime_type(str): A mime-type.
      parsed_ranges (List[Tuple[str, str, dict]]): A list of parsed media ranges.
    
    Returns:
      int: The 'q' quality parameter of the best match, 0 if no match was
      found. 
    """

    return fitness_and_quality_parsed(mime_type, parsed_ranges)[1]


def quality(mime_type, ranges):
    """Return the quality ('q') of a mime-type against a list of media-ranges.
    
    For example:

    >>> quality('text/html','text/*;q=0.3, text/html;q=0.7, text/html;level=1, text/html;level=2;q=0.4, */*;q=0.5')
    0.7

    Args:
      mime_type (str): A mime-type.
      ranges (str): List of media-ranges.
    
    Returns:
      float: The quality 'q' of a mime-type when compared against the
      media-ranges in ranges
    """
    parsed_ranges = [parse_media_range(r) for r in ranges.split(",")]

    return quality_parsed(mime_type, parsed_ranges)


def best_match(supported, header):
    """Takes a list of supported mime-types and finds the best match for all the
    media-ranges listed in header.

    >>> best_match(['application/xbel+xml', 'text/xml'],
                'text/*;q=0.5,*/*; q=0.1')
    'text/xml'

    Args:
      supported(List[str]): List of supported mime-types. The list of supported
        mime-types should be sorted in order of increasing desirability, in case
        of a situation where there is a tie.
      header (str): a string that conforms to the format of the HTTP Accept: header.
    
    Returns:
      str: The Mime-type with the highest quality ('q') from list of
      candidates.
    """
    split_header = _filter_blank(header.split(","))
    parsed_header = [parse_media_range(r) for r in split_header]
    weighted_matches = []
    pos = 0
    for mime_type in supported:
        weighted_matches.append(
            (fitness_and_quality_parsed(mime_type, parsed_header), pos, mime_type)
        )
        pos += 1
    weighted_matches.sort()

    return weighted_matches[-1][0][1] and weighted_matches[-1][2] or ""


def _filter_blank(i):
    for s in i:
        if s.strip():
            yield s
