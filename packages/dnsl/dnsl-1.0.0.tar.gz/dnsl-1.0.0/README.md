# DNS Lookup Tool

![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Overview
DNS Lookup Tool is an advanced command-line utility for querying various DNS records, performing DNS-over-HTTPS (DoH) lookups, and attempting zone transfers (AXFR). It is designed for security professionals, network engineers, and penetration testers.

## Features
- Query different DNS record types (A, AAAA, CNAME, MX, NS, TXT, SOA, PTR)
- Perform DNS-over-HTTPS (DoH) queries
- Attempt DNS zone transfers (AXFR)
- Support for custom DNS servers
- Fast and detailed output with response times

## Installation
You can install the tool using pip:

```bash
pip install dnsl
```

Or, install from source:

```bash
git clone https://github.com/hemaabokila/dns_lookup.git
cd dns_lookup
pip install .
```

## Usage
After installation, you can use the tool from the command line:

```bash
dnsl -d example.com
```

### Available Options

```bash
usage: dnsl [-h] -d DOMAIN [DOMAIN ...] [-t TYPE] [-s SERVER] [--axfr] [--doh]

Advanced DNS Lookup Tool

optional arguments:
  -h, --help            Show this help message and exit
  -d, --domain DOMAIN   Domain(s) to query (Required)
  -t, --type TYPE       DNS record type (A, AAAA, MX, TXT, etc.)
  -s, --server SERVER   Custom DNS server (e.g., 8.8.8.8)
  --axfr                Attempt Zone Transfer (AXFR)
  --doh                 Use DNS-over-HTTPS (DoH)
```

### Examples
Query all DNS records for a domain:

```bash
dnsl -d example.com
```

Query a specific DNS record type:

```bash
dnsl -d example.com -t MX
```

Use a custom DNS server:

```bash
dnsl -d example.com -s 8.8.8.8
```

Perform a DNS-over-HTTPS (DoH) lookup:

```bash
dnsl -d example.com --doh
```

Attempt a zone transfer:

```bash
dnsl -d example.com --axfr -s ns1.example.com
```

## License
This project is licensed under the MIT License.

## Author
Developed by **Ibrahem abo kila**

