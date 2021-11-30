# -*- coding: utf-8 -*-

"""Tests for `dqsegdb.urifunctions`
"""

from unittest import mock

from .. import urifunctions


def test_constructSegmentQueryURLTimeWindow():
    assert urifunctions.constructSegmentQueryURLTimeWindow(
        "https",
        "segments.ligo.org",
        "L1",
        "TEST-FLAG",
        1,
        "metadata",
        100,
        200,
    ) == (
        "https://segments.ligo.org"
        "/dq/L1/TEST-FLAG/1?s=100&e=200&include=metadata"
    )


def test_constructSegmentQueryURL():
    assert urifunctions.constructSegmentQueryURL(
        "https",
        "segments.ligo.org",
        "L1",
        "TEST-FLAG",
        "1",
        "metadata",
    ) == (
        "https://segments.ligo.org"
        "/dq/L1/TEST-FLAG/1?include=metadata"
    )


def test_constructVersionQueryURL():
    assert urifunctions.constructVersionQueryURL(
        "https",
        "segments.ligo.org",
        "L1",
        "TEST-FLAG",
    ) == (
        "https://segments.ligo.org"
        "/dq/L1/TEST-FLAG"
    )


def test_constructFlagQueryURL():
    assert urifunctions.constructFlagQueryURL(
        "https",
        "segments.ligo.org",
        "L1",
    ) == (
        "https://segments.ligo.org"
        "/dq/L1"
    )
