#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Statistics:
    def __init__(self):
        self.authors: dict = {}

    def __str__(self):
        return f"{'authors': '{[authors.keys()]}'}"

    def __repr__(self):
        return str(self.authors)
