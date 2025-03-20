import argparse
import dns.resolver
import dns.query
import dns.zone
import time
import requests
from rich.console import Console
from rich.table import Table
from colorama import Fore, Style
import pyfiglet

console = Console()

DNS_RECORDS = ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA", "PTR"]

def dns_lookup(domain, record_type=None, server=None, doh=False):
    banner = pyfiglet.figlet_format("DNS LOOKUP")
    print(f"{Fore.BLUE}{banner}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Developed by: Ibrahem abo kila{Style.RESET_ALL}\n")
    resolver = dns.resolver.Resolver()
    if server:
        resolver.nameservers = [server]

    records_to_query = [record_type] if record_type else DNS_RECORDS

    table = Table(title=f"DNS Records for {domain}")
    table.add_column("Record Type", style="cyan")
    table.add_column("Result", style="magenta")
    table.add_column("Time (ms)", style="green")

    for rtype in records_to_query:
        try:
            start_time = time.time()
            if doh:
                result = dns_over_https(domain, rtype)
            else:
                answers = resolver.resolve(domain, rtype)
                result = "\n".join([str(ans) for ans in answers])
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)
            table.add_row(rtype, result, str(response_time))
        except dns.resolver.NoAnswer:
            table.add_row(rtype, "No record found", "-")
        except dns.resolver.NXDOMAIN:
            console.print(f"[red]Error: Domain {domain} does not exist[/red]")
            return
        except Exception as e:
            table.add_row(rtype, f"Error - {e}", "-")

    console.print(table)

def dns_over_https(domain, record_type):
    url = f"https://cloudflare-dns.com/dns-query?name={domain}&type={record_type}"
    headers = {"accept": "application/dns-json"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  
        
        data = response.json()
        return "\n".join([answer["data"] for answer in data.get("Answer", [])])
    
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def dns_axfr(domain, server):
    try:
        console.print(f"[yellow]Attempting AXFR on {domain} via {server}...[/yellow]")

        zone_transfer = dns.zone.from_xfr()
        zone = dns.zone.from_xfr(zone_transfer)

        if not zone:
            print("AXFR Failed: No data received.")
            return
        for name, node in zone_transfer.nodes.items():
            console.print(f"[cyan]{name}:[/cyan] {node.to_text()}")
    except dns.exception.DNSException as e:
        console.print(f"[red]AXFR Failed: {e}[/red]")

def main():
    parser = argparse.ArgumentParser(description="Advanced DNS Lookup Tool")
    parser.add_argument("-d", "--domain", nargs="+", required=True, help="Domain(s) to query")
    parser.add_argument("-t", "--type", help="DNS record type (e.g., A, AAAA, MX, TXT). Default: all", default=None)
    parser.add_argument("-s", "--server", help="Custom DNS server (e.g., 8.8.8.8)", default=None)
    parser.add_argument("--axfr", action="store_true", help="Attempt Zone Transfer (AXFR)")
    parser.add_argument("--doh", action="store_true", help="Use DNS-over-HTTPS (DoH)")

    args = parser.parse_args()

    for domain in args.domain:
        if args.axfr:
            if not args.server:
                console.print("[red]AXFR requires a custom DNS server (-s).[/red]")
            else:
                dns_axfr(domain, args.server)
        else:
            dns_lookup(domain, args.type, args.server, args.doh)
if __name__ == "__main__":
    main()