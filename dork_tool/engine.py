"""
Dork Engine: Query Generators, Operator Catalogs, Live Query Analysis, Plain-English Explainer,
and Curated Security Templates for Domains, Emails, People, and Usernames.
Completely clean of emojis with professional security designations.
Version 1.2.0
"""

import re
import urllib.parse
from typing import List, Dict, Tuple, Any


class DorkEngine:
    """
    Catalog of advanced Google search operators, pre-configured dork templates,
    automatic query generator, live query analysis, and plain-English query explainer.
    """

    OPERATORS: Dict[str, Dict[str, str]] = {
        "site:": {"desc": "Limit results to a specific domain or host", "example": "site:target.com"},
        "inurl:": {"desc": "Search for text anywhere inside the URL", "example": "inurl:admin"},
        "intitle:": {"desc": "Search for text in the HTML title tag", "example": 'intitle:"login page"'},
        "intext:": {"desc": "Search for text anywhere on the webpage body", "example": 'intext:"password reset"'},
        "filetype:": {"desc": "Filter by file extension", "example": "filetype:pdf"},
        "ext:": {"desc": "Synonym for filetype:", "example": "ext:sql"},
        "allinurl:": {"desc": "Require all terms in URL", "example": "allinurl:admin config"},
        "allintitle:": {"desc": "Require all terms in page title", "example": "allintitle:dashboard login"},
        "allintext:": {"desc": "Require all terms in body text", "example": "allintext:confidential internal"},
        "cache:": {"desc": "View Google's cached snapshot of a URL", "example": "cache:example.com"},
        "link:": {"desc": "Find pages linking to a specified URL", "example": "link:target.com"},
        "related:": {"desc": "Find websites similar or related to target", "example": "related:target.com"},
        "info:": {"desc": "Get summary information about a domain", "example": "info:target.com"},
        "before:": {"desc": "Filter results indexed before date (YYYY-MM-DD)", "example": "before:2024-01-01"},
        "after:": {"desc": "Filter results indexed after date (YYYY-MM-DD)", "example": "after:2023-01-01"},
        "AROUND(N)": {"desc": "Find two words within N words of each other", "example": "confidential AROUND(3) password"},
        "\"exact phrase\"": {"desc": "Match an exact sequence of words", "example": '"index of /admin"'},
        "- (Exclude)": {"desc": "Exclude results containing word or operator", "example": "site:target.com -site:www.target.com"},
        "OR |": {"desc": "Match either term or expression", "example": "filetype:sql OR filetype:db"},
        "AND": {"desc": "Require both terms (default behavior)", "example": "admin AND login"}
    }

    TEMPLATES: Dict[str, List[Tuple[str, str]]] = {
        "Person & Identity OSINT": [
            ("Resumes & CVs (PDF / Word)", '(resume OR cv OR "curriculum vitae") (filetype:pdf OR filetype:docx OR filetype:doc)'),
            ("Social Media & Profiles", 'site:linkedin.com/in OR site:twitter.com OR site:x.com OR site:instagram.com OR site:facebook.com'),
            ("Email & Contact Discovery", '("@gmail.com" OR "@yahoo.com" OR "@outlook.com" OR "@proton.me" OR "contact:" OR "email me at")'),
            ("Speeches & Presentations", '(presentation OR speaker OR keynote OR slides OR conference) (filetype:pdf OR filetype:pptx)'),
            ("Court & Public Records", '(court OR lawsuit OR judgment OR legal OR affidavit OR certificate) filetype:pdf'),
            ("Bio & About Me Pages", '(intitle:"About Me" OR intitle:"Biography" OR intitle:"Who is" OR inurl:about-me OR inurl:bio)')
        ],
        "Email & Account OSINT": [
            ("Email Breach & Password Dumps", '(password OR leak OR breach OR credential OR dump OR hash OR combo)'),
            ("Pastebin & Public Gist Leaks", 'site:pastebin.com OR site:gist.github.com OR site:ghostbin.com'),
            ("Contact Lists & Spreadsheet Dumps", '(filetype:xls OR filetype:xlsx OR filetype:csv OR filetype:txt)'),
            ("User Registration & Profile Traces", '(inurl:profile OR inurl:user OR inurl:member OR inurl:author OR inurl:account)')
        ],
        "Username & Developer OSINT": [
            ("Developer & Repository Profiles", 'site:github.com OR site:gitlab.com OR site:bitbucket.org OR site:npmjs.com'),
            ("Community & Forum Profiles", 'site:reddit.com/user OR site:stackoverflow.com/users OR site:news.ycombinator.com/user'),
            ("PGP & GPG Public Keys", 'intext:"BEGIN PGP PUBLIC KEY BLOCK"')
        ],
        "Credentials & Secrets": [
            ("Exposed .env / Configuration Files", 'intitle:"Index of" intext:".env" OR intext:".git/config" OR intext:"wp-config.php"'),
            ("Database Connection Strings", 'intext:"mongodb+srv://" OR intext:"postgres://" OR intext:"mysql://" filetype:env OR filetype:txt'),
            ("Private Keys & Certificates", 'intext:"BEGIN RSA PRIVATE KEY" OR intext:"BEGIN OPENSSH PRIVATE KEY" filetype:key OR filetype:pem'),
            ("API Keys & Webhooks", 'intext:"AKIA" OR intext:"ghp_" OR intext:"xoxb-" OR intext:"eyJhbGciOi" filetype:json OR filetype:txt'),
            ("Password & Credential Logs", 'intext:"admin:admin" OR intext:"root:root" OR intext:"password=" filetype:log OR filetype:sql')
        ],
        "Cloud & Object Storage": [
            ("Public AWS S3 Buckets", 'site:s3.amazonaws.com OR site:s3-external-1.amazonaws.com intext:"Index of"'),
            ("Google Cloud Storage Buckets", 'site:storage.googleapis.com intext:"Index of"'),
            ("Azure Blob Storage Containers", 'site:blob.core.windows.net intext:"Index of"'),
            ("DigitalOcean Spaces", 'site:digitaloceanspaces.com intext:"Index of"')
        ],
        "Database & Backup Archives": [
            ("SQL Database Dumps", 'filetype:sql ("INSERT INTO" OR "CREATE TABLE") -site:github.com -site:stackoverflow.com'),
            ("SQLite & DB Data Files", 'filetype:db OR filetype:sqlite OR filetype:sqlite3 OR filetype:mdb'),
            ("Compressed Backup Archives", 'filetype:bak OR filetype:backup OR filetype:old OR filetype:tar.gz OR filetype:zip inurl:backup'),
            ("phpMyAdmin Export Dumps", 'intext:"phpMyAdmin SQL Dump" "Database:" filetype:sql')
        ],
        "Admin & Authentication Portals": [
            ("General Administrative Portals", 'inurl:admin OR inurl:login OR inurl:dashboard OR inurl:portal intitle:login'),
            ("cPanel & Webmail Interfaces", 'intitle:"cPanel" inurl:2082 OR inurl:2083 OR intitle:"Webmail" inurl:2095'),
            ("WordPress Admin Authentication", 'inurl:wp-login.php OR inurl:wp-admin intitle:"Log In"'),
            ("phpMyAdmin Management Interfaces", 'intitle:"phpMyAdmin" inurl:main.php OR inurl:index.php'),
            ("Django Admin Dashboards", 'intitle:"Site administration" inurl:admin/login')
        ],
        "DevOps, CI/CD & Monitoring": [
            ("Jenkins CI/CD Dashboards", 'intitle:"Dashboard [Jenkins]" "Manage Jenkins"'),
            ("Grafana Monitoring Panels", 'intitle:"Grafana" "Welcome to Grafana" inurl:login'),
            ("Kibana Analytics Interfaces", 'intitle:"Kibana" inurl:app/kibana'),
            ("Spring Boot Actuator Endpoints", 'inurl:/actuator/env OR inurl:/actuator/health OR inurl:/actuator/metrics'),
            ("Swagger / OpenAPI Specifications", 'intitle:"Swagger UI" OR inurl:swagger-ui.html OR inurl:v2/api-docs')
        ],
        "Vulnerabilities & Error Traces": [
            ("SQL Syntax Errors (SQLi Vector)", 'intext:"SQL syntax" OR intext:"mysql_fetch_array" OR intext:"ORA-01756" inurl:".php?id="'),
            ("PHP Fatal Errors & Stack Traces", 'intext:"Fatal error:" intext:"on line" intext:"/var/www/"'),
            ("Apache / Nginx Server Status", 'intitle:"Apache Status" "Server Version" OR intitle:"Nginx status"'),
            ("Exposed Diagnostic Log Files", 'filetype:log intext:"error" OR intext:"debug" OR intext:"failed login"')
        ],
        "Sensitive Directories & Infrastructure": [
            ("Open Directory Indexing", 'intitle:"Index of" ("parent directory" OR "name" OR "last modified")'),
            ("Exposed .git Repositories", 'inurl:"/.git" intitle:"Index of /"'),
            ("Docker Compose & Container Configs", 'filetype:yml OR filetype:yaml "docker-compose" "environment:"'),
            ("Configuration XML / INI / CONF", 'filetype:xml OR filetype:conf OR filetype:cnf OR filetype:ini inurl:config')
        ],
        "Network & Hardware Interfaces": [
            ("Network Cameras & Surveillance", 'intitle:"Live View / - AXIS" OR inurl:"view/index.shtml" OR intitle:"Network Camera"'),
            ("Network Hardware & Routers", 'intitle:"RouterOS" OR intitle:"MikroTik" OR intitle:"OpenWrt"')
        ]
    }

    CATEGORIES = [
        ("basic_info", "Basic Information", True, "Domain root, entity mentions, and indexed footprint"),
        ("files", "Sensitive Documents", True, "PDF, DOCX, XLSX, PPTX, CSV, resumes, and reports"),
        ("directories", "Directory Listings", True, "Exposed 'Index of' open directories and file trees"),
        ("login_pages", "Login & Auth Pages", True, "Admin portals, user logins, and profile endpoints"),
        ("vulnerabilities", "Error Logs & Leaks", True, "PHP errors, SQL syntax issues, debug traces, and breach dumps"),
        ("credentials", "Exposed Credentials", True, "Config files, .env, DB keys, password mentions, and API tokens"),
        ("backup_files", "Backup & DB Files", True, ".bak, .sql, .backup, .tar, .zip archives and data dumps"),
        ("subdomains", "Subdomains & Hosts", True, "Discover subdomains, cloud hostnames, and user pages"),
        ("technologies", "Frameworks & CMS", True, "WordPress, Drupal, Joomla, phpMyAdmin, and tech stacks"),
        ("cloud_storage", "Cloud Buckets", True, "AWS S3, Google Cloud Storage, Azure Blob"),
        ("social_media", "Social Media", False, "LinkedIn, Twitter/X, GitHub, Reddit, Instagram profiles"),
        ("email_harvest", "Email Harvesting", False, "Exposed emails, contact addresses, and directory listings"),
        ("person_search", "Person OSINT", False, "Resumes, CVs, biographies, background records, contact info"),
        ("code_repos", "Public Code Repos", False, "GitHub, GitLab, Bitbucket, Pastebin, and Gist leaks")
    ]

    @staticmethod
    def detect_target_type(target: str) -> str:
        """
        Intelligently detects whether the target is an EMAIL, DOMAIN, PERSON, or KEYWORD/USERNAME.
        Returns one of: 'EMAIL', 'DOMAIN', 'PERSON', 'KEYWORD'
        """
        t = target.strip()
        if not t:
            return "KEYWORD"

        # 1. Email Check
        if "@" in t and "." in t.split("@")[-1] and " " not in t:
            return "EMAIL"

        # 2. Domain / URL Check
        if t.startswith("http://") or t.startswith("https://"):
            return "DOMAIN"

        if ("." in t and " " not in t and "/" not in t and not t.startswith("@")
                and re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', t)):
            return "DOMAIN"

        # 3. Person Name Check (Multiple words with spaces)
        if " " in t:
            return "PERSON"

        # 4. Single token without dots or @ -> Username / Keyword
        return "KEYWORD"

    @staticmethod
    def clean_target_domain(target: str) -> str:
        """Sanitizes domain input into a clean hostname."""
        target = target.strip()
        if not target:
            return ""

        if target.startswith("http://") or target.startswith("https://"):
            parsed = urllib.parse.urlparse(target)
            domain = parsed.netloc or parsed.path
        elif "." in target and " " not in target and "@" not in target:
            domain = target
        else:
            return target

        # Strip port if present
        if ":" in domain:
            domain = domain.split(":")[0]

        # Strip leading www.
        if domain.lower().startswith("www."):
            domain = domain[4:]

        return domain.strip("/")

    @staticmethod
    def generate_dorks(target: str, selected_categories: List[str], target_type: str = "AUTO") -> List[Tuple[str, str]]:
        """
        Generates clean, syntactically correct Google Dork queries tailored to
        Domains, Emails, Person Names, and Usernames/Keywords.
        Returns a list of (category_name, dork_query) tuples.
        """
        target = target.strip()
        if not target:
            return []

        if target_type == "AUTO" or target_type not in ("DOMAIN", "EMAIL", "PERSON", "KEYWORD"):
            t_type = DorkEngine.detect_target_type(target)
        else:
            t_type = target_type

        dorks: List[Tuple[str, str]] = []

        # =====================================================================
        # TYPE 1: EMAIL ADDRESS (e.g. user@target.com)
        # =====================================================================
        if t_type == "EMAIL":
            email_parts = target.split("@")
            user_part = email_parts[0]
            domain_part = email_parts[1] if len(email_parts) > 1 else ""

            for cat_id in selected_categories:
                if cat_id == "basic_info":
                    dorks.append(("Basic Info", f'"{target}"'))
                    if domain_part:
                        dorks.append(("Basic Info", f'"{target}" -site:{domain_part}'))

                elif cat_id == "files":
                    exts = "ext:pdf OR ext:doc OR ext:docx OR ext:xls OR ext:xlsx OR ext:csv OR ext:txt"
                    dorks.append(("Sensitive Files", f'"{target}" ({exts})'))

                elif cat_id == "directories":
                    dorks.append(("Directory Listings", f'intitle:"Index of" "{target}"'))

                elif cat_id == "login_pages":
                    dorks.append(("Login Pages", f'"{target}" (inurl:login OR inurl:signin OR inurl:auth OR inurl:profile)'))

                elif cat_id == "vulnerabilities":
                    dorks.append(("Vulnerabilities & Leaks", f'"{target}" (password OR "pwd" OR "hash" OR leak OR breach OR dump OR combo)'))

                elif cat_id == "credentials":
                    dorks.append(("Credentials & Keys", f'"{target}" (filetype:env OR filetype:txt OR filetype:log OR filetype:sql OR filetype:conf)'))
                    dorks.append(("Credentials & Keys", f'"{target}" (API_KEY OR "password=" OR "secret" OR "bearer")'))

                elif cat_id == "backup_files":
                    dorks.append(("Backup Files", f'"{target}" (ext:sql OR ext:bak OR ext:tar OR ext:gz OR ext:csv OR ext:json)'))

                elif cat_id == "subdomains":
                    if domain_part:
                        dorks.append(("Subdomains", f"site:*.{domain_part} -site:www.{domain_part}"))
                    else:
                        dorks.append(("Subdomains", f'"{target}"'))

                elif cat_id == "technologies":
                    dorks.append(("Technologies & CMS", f'"{target}" ("Powered by WordPress" OR "Drupal" OR "Joomla" OR "phpMyAdmin")'))

                elif cat_id == "cloud_storage":
                    dorks.append(("Cloud Storage", f'site:s3.amazonaws.com "{target}"'))
                    dorks.append(("Cloud Storage", f'site:storage.googleapis.com "{target}"'))
                    dorks.append(("Cloud Storage", f'site:blob.core.windows.net "{target}"'))

                elif cat_id == "social_media":
                    dorks.append(("Social Media", f'site:linkedin.com OR site:twitter.com OR site:x.com "{target}"'))
                    dorks.append(("Social Media", f'site:facebook.com OR site:instagram.com OR site:reddit.com "{target}"'))
                    dorks.append(("Social Media", f'site:gravatar.com OR site:about.me "{target}"'))

                elif cat_id == "email_harvest":
                    dorks.append(("Email Harvest", f'"{target}"'))
                    if domain_part:
                        dorks.append(("Email Harvest", f'"{user_part}" site:{domain_part}'))

                elif cat_id == "person_search":
                    dorks.append(("Person OSINT", f'"{target}" (resume OR cv OR contact OR profile OR author)'))
                    dorks.append(("Person OSINT", f'"{target}" ("phone" OR "mobile" OR "address" OR "tel:")'))

                elif cat_id == "code_repos":
                    dorks.append(("Code Repos", f'site:github.com "{target}"'))
                    dorks.append(("Code Repos", f'site:gitlab.com "{target}"'))
                    dorks.append(("Code Repos", f'site:pastebin.com OR site:ghostbin.com "{target}"'))
                    dorks.append(("Code Repos", f'site:gist.github.com "{target}"'))

        # =====================================================================
        # TYPE 2: PERSON / FULL NAME (e.g. "John Doe")
        # =====================================================================
        elif t_type == "PERSON":
            for cat_id in selected_categories:
                if cat_id == "basic_info":
                    dorks.append(("Basic Info", f'"{target}"'))
                    dorks.append(("Basic Info", f'"{target}" (biography OR bio OR "about me" OR "about us")'))

                elif cat_id == "files":
                    dorks.append(("Sensitive Files", f'"{target}" (resume OR cv OR "curriculum vitae") (ext:pdf OR ext:doc OR ext:docx)'))
                    dorks.append(("Sensitive Files", f'"{target}" (presentation OR slides OR speech) (ext:pdf OR ext:ppt OR ext:pptx)'))

                elif cat_id == "directories":
                    dorks.append(("Directory Listings", f'intitle:"Index of" "{target}"'))

                elif cat_id == "login_pages":
                    dorks.append(("Login & User Pages", f'"{target}" (inurl:profile OR inurl:user OR inurl:author OR inurl:member)'))

                elif cat_id == "vulnerabilities":
                    dorks.append(("Vulnerabilities & Leaks", f'"{target}" (password OR leak OR breach OR credential OR dump)'))

                elif cat_id == "credentials":
                    dorks.append(("Credentials & Keys", f'"{target}" (API_KEY OR "secret" OR "token" OR "access key" OR password)'))

                elif cat_id == "backup_files":
                    dorks.append(("Backup Files", f'"{target}" (ext:sql OR ext:csv OR ext:xlsx OR ext:log OR ext:bak)'))

                elif cat_id == "subdomains":
                    dorks.append(("Subdomains & Blogs", f'"{target}" (site:github.io OR site:medium.com OR site:substack.com OR site:wordpress.com)'))

                elif cat_id == "technologies":
                    dorks.append(("Technologies & CMS", f'"{target}" ("authored by" OR "contributor" OR "maintainer" OR "developer")'))

                elif cat_id == "cloud_storage":
                    dorks.append(("Cloud Storage", f'site:s3.amazonaws.com "{target}"'))
                    dorks.append(("Cloud Storage", f'site:storage.googleapis.com "{target}"'))
                    dorks.append(("Cloud Storage", f'site:blob.core.windows.net "{target}"'))

                elif cat_id == "social_media":
                    dorks.append(("Social Media", f'site:linkedin.com/in "{target}"'))
                    dorks.append(("Social Media", f'site:twitter.com OR site:x.com "{target}"'))
                    dorks.append(("Social Media", f'site:github.com "{target}"'))
                    dorks.append(("Social Media", f'site:instagram.com OR site:facebook.com "{target}"'))

                elif cat_id == "email_harvest":
                    dorks.append(("Email Harvest", f'"{target}" ("@gmail.com" OR "@yahoo.com" OR "@outlook.com" OR "@proton.me" OR "email me at" OR "mailto:")'))

                elif cat_id == "person_search":
                    dorks.append(("Person OSINT", f'"{target}" (resume OR cv OR "curriculum vitae") ext:pdf'))
                    dorks.append(("Person OSINT", f'"{target}" (phone OR contact OR email OR "cell:")'))
                    dorks.append(("Person OSINT", f'"{target}" (court OR lawsuit OR arrest OR legal OR certificate OR license) filetype:pdf'))
                    dorks.append(("Person OSINT", f'"{target}" (conference OR keynote OR speaker OR podcast OR interview)'))

                elif cat_id == "code_repos":
                    dorks.append(("Code Repos", f'site:github.com "{target}"'))
                    dorks.append(("Code Repos", f'site:gitlab.com "{target}"'))
                    dorks.append(("Code Repos", f'site:pastebin.com "{target}"'))
                    dorks.append(("Code Repos", f'site:npmjs.com OR site:pypi.org "{target}"'))

        # =====================================================================
        # TYPE 3: KEYWORD / USERNAME (e.g. "johndoe99")
        # =====================================================================
        elif t_type == "KEYWORD":
            for cat_id in selected_categories:
                if cat_id == "basic_info":
                    dorks.append(("Basic Info", f'"{target}"'))

                elif cat_id == "files":
                    exts = "ext:pdf OR ext:doc OR ext:docx OR ext:xls OR ext:xlsx OR ext:csv OR ext:txt"
                    dorks.append(("Sensitive Files", f'"{target}" ({exts})'))

                elif cat_id == "directories":
                    dorks.append(("Directory Listings", f'intitle:"Index of" "{target}"'))

                elif cat_id == "login_pages":
                    dorks.append(("Login & User Pages", f'inurl:"{target}" (inurl:user OR inurl:profile OR inurl:author OR inurl:member)'))

                elif cat_id == "vulnerabilities":
                    dorks.append(("Vulnerabilities & Leaks", f'"{target}" (password OR leak OR breach OR combo OR dump)'))

                elif cat_id == "credentials":
                    dorks.append(("Credentials & Keys", f'"{target}" (API_KEY OR token OR secret OR password OR key)'))

                elif cat_id == "backup_files":
                    dorks.append(("Backup Files", f'"{target}" (ext:sql OR ext:bak OR ext:log OR ext:json OR ext:csv)'))

                elif cat_id == "subdomains":
                    dorks.append(("Subdomains & Hosts", f'"{target}" (site:*.github.io OR site:*.gitlab.io OR site:*.firebaseapp.com)'))

                elif cat_id == "technologies":
                    dorks.append(("Technologies & CMS", f'"{target}" ("maintainer" OR "developer" OR "contributor")'))

                elif cat_id == "cloud_storage":
                    dorks.append(("Cloud Storage", f'site:s3.amazonaws.com "{target}"'))
                    dorks.append(("Cloud Storage", f'site:storage.googleapis.com "{target}"'))

                elif cat_id == "social_media":
                    dorks.append(("Social Media", f'site:twitter.com/{target} OR site:x.com/{target}'))
                    dorks.append(("Social Media", f'site:github.com/{target}'))
                    dorks.append(("Social Media", f'site:reddit.com/user/{target}'))
                    dorks.append(("Social Media", f'site:instagram.com/{target} OR site:linkedin.com/in/{target}'))

                elif cat_id == "email_harvest":
                    dorks.append(("Email Harvest", f'"{target}@" OR "@{target}."'))

                elif cat_id == "person_search":
                    dorks.append(("Person OSINT", f'"{target}" (resume OR cv OR biography OR portfolio OR contact)'))

                elif cat_id == "code_repos":
                    dorks.append(("Code Repos", f'site:github.com "{target}"'))
                    dorks.append(("Code Repos", f'site:gitlab.com "{target}"'))
                    dorks.append(("Code Repos", f'site:pastebin.com "{target}"'))
                    dorks.append(("Code Repos", f'site:hub.docker.com/u/{target}'))

        # =====================================================================
        # TYPE 4: DOMAIN (e.g. "example.com")
        # =====================================================================
        else:
            clean_domain = DorkEngine.clean_target_domain(target)
            for cat_id in selected_categories:
                if cat_id == "basic_info":
                    dorks.append(("Basic Info", f"site:{clean_domain}"))
                    dorks.append(("Basic Info", f"info:{clean_domain}"))
                    dorks.append(("Basic Info", f'"{clean_domain}" -site:{clean_domain}'))

                elif cat_id == "files":
                    exts = "ext:pdf OR ext:doc OR ext:docx OR ext:xls OR ext:xlsx OR ext:ppt OR ext:pptx OR ext:csv OR ext:txt"
                    dorks.append(("Sensitive Files", f"site:{clean_domain} ({exts})"))

                elif cat_id == "directories":
                    dirs = 'intitle:"Index of" OR intitle:"Directory Listing" OR intitle:"Index of /"'
                    dorks.append(("Directory Listings", f"site:{clean_domain} ({dirs})"))

                elif cat_id == "login_pages":
                    logins = 'inurl:login OR inurl:signin OR inurl:admin OR inurl:portal OR inurl:auth OR intitle:"login" OR intitle:"sign in"'
                    dorks.append(("Login Pages", f"site:{clean_domain} ({logins})"))

                elif cat_id == "vulnerabilities":
                    vulns = 'inurl:".php?id=" OR inurl:".php?cat=" OR intext:"sql syntax near" OR intext:"syntax error has occurred" OR intext:"Warning: mysql_" OR intext:"Fatal error:"'
                    dorks.append(("Vulnerabilities & Errors", f"site:{clean_domain} ({vulns})"))

                elif cat_id == "credentials":
                    creds = 'filetype:env OR filetype:yml OR filetype:yaml OR filetype:conf OR filetype:ini OR intext:"DB_PASSWORD" OR intext:"api_key" OR intext:"BEGIN RSA PRIVATE KEY"'
                    dorks.append(("Credentials & Keys", f"site:{clean_domain} ({creds})"))

                elif cat_id == "backup_files":
                    backups = "ext:bak OR ext:backup OR ext:old OR ext:sql OR ext:tar OR ext:gz OR ext:zip OR ext:7z"
                    dorks.append(("Backup Files", f"site:{clean_domain} ({backups})"))

                elif cat_id == "subdomains":
                    dorks.append(("Subdomains", f"site:*.{clean_domain} -site:www.{clean_domain}"))

                elif cat_id == "technologies":
                    tech = 'inurl:wp-content OR inurl:wp-includes OR inurl:node_modules OR intext:"Powered by WordPress" OR intext:"Powered by Drupal"'
                    dorks.append(("Technologies & CMS", f"site:{clean_domain} ({tech})"))

                elif cat_id == "cloud_storage":
                    dorks.append(("Cloud Storage", f'site:s3.amazonaws.com "{clean_domain}"'))
                    dorks.append(("Cloud Storage", f'site:storage.googleapis.com "{clean_domain}"'))
                    dorks.append(("Cloud Storage", f'site:blob.core.windows.net "{clean_domain}"'))

                elif cat_id == "social_media":
                    dorks.append(("Social Media", f'site:linkedin.com/company OR site:linkedin.com/in "{clean_domain}"'))
                    dorks.append(("Social Media", f'site:twitter.com OR site:x.com "{clean_domain}"'))
                    dorks.append(("Social Media", f'site:reddit.com "{clean_domain}"'))

                elif cat_id == "email_harvest":
                    dorks.append(("Email Harvest", f'"@{clean_domain}" OR intext:"mailto:*@{clean_domain}"'))

                elif cat_id == "person_search":
                    dorks.append(("Person OSINT", f'"{clean_domain}" (resume OR cv OR "curriculum vitae") ext:pdf'))
                    dorks.append(("Person OSINT", f'"{clean_domain}" (biography OR "about me" OR contact)'))

                elif cat_id == "code_repos":
                    dorks.append(("Code Repos", f'site:github.com "{clean_domain}"'))
                    dorks.append(("Code Repos", f'site:gitlab.com "{clean_domain}"'))
                    dorks.append(("Code Repos", f'site:pastebin.com "{clean_domain}"'))

        return dorks

    @staticmethod
    def explain_query(query: str) -> str:
        """
        Translates a Google Dork search query into a clear, natural English description.
        Helps analysts understand exactly what results Google will return.
        """
        q = query.strip()
        if not q:
            return "Enter a search query or target above to see its natural English explanation."

        explanations = []

        # 1. Site / Domain Scope
        site_matches = re.findall(r'site:([^\s()]+)', q, re.IGNORECASE)
        if site_matches:
            if len(site_matches) == 1:
                explanations.append(f"on the website or domain '{site_matches[0]}'")
            else:
                explanations.append(f"restricted to domains ({', '.join(site_matches)})")

        # 2. In Title
        intitle_matches = re.findall(r'intitle:(?:"([^"]+)"|([^\s()]+))', q, re.IGNORECASE)
        if intitle_matches:
            terms = [m[0] or m[1] for m in intitle_matches]
            explanations.append(f"with ({', '.join(repr(t) for t in terms)}) in the page title")

        # 3. In URL
        inurl_matches = re.findall(r'inurl:(?:"([^"]+)"|([^\s()]+))', q, re.IGNORECASE)
        if inurl_matches:
            terms = [m[0] or m[1] for m in inurl_matches]
            explanations.append(f"with ({', '.join(repr(t) for t in terms)}) in the URL address")

        # 4. File Types / Extensions
        filetype_matches = re.findall(r'(?:filetype|ext):([^\s()]+)', q, re.IGNORECASE)
        if filetype_matches:
            explanations.append(f"matching file types (.{', .'.join(filetype_matches)})")

        # 5. In Body Text
        intext_matches = re.findall(r'intext:(?:"([^"]+)"|([^\s()]+))', q, re.IGNORECASE)
        if intext_matches:
            terms = [m[0] or m[1] for m in intext_matches]
            explanations.append(f"containing ({', '.join(repr(t) for t in terms)}) in the page content")

        # 6. Exact Phrases (quotes not preceded by operators)
        # Find all "exact phrase" that are not preceded by intext:, intitle:, inurl:
        quotes = re.findall(r'(?<!intext:)(?<!intitle:)(?<!inurl:)"([^"]+)"', q, re.IGNORECASE)
        if quotes:
            explanations.append(f"containing exact phrases ({', '.join(repr(p) for p in quotes)})")

        # 7. Exclusions
        exclusions = re.findall(r'-site:([^\s()]+)|-([a-zA-Z0-9_-]+)', q)
        if exclusions:
            ex_terms = [m[0] or m[1] for m in exclusions if m[0] or m[1]]
            if ex_terms:
                explanations.append(f"excluding results matching ({', '.join(ex_terms)})")

        if explanations:
            return "Searches Google for pages " + ", ".join(explanations) + "."
        else:
            return f"Searches Google for indexed pages matching terms: '{q}'."

    @staticmethod
    def analyze_query(query: str) -> Dict[str, Any]:
        """
        Analyzes a search query in real-time, detecting used operators, word counts,
        site scopes, complexity level, and plain-English explanation.
        """
        q = query.strip()
        if not q:
            return {
                "chars": 0,
                "words": 0,
                "operators": [],
                "target_site": "",
                "complexity": "Empty",
                "explanation": "Enter a search query or target above to see its natural English explanation.",
                "is_valid": False
            }

        known_ops = ["site:", "inurl:", "intitle:", "intext:", "filetype:", "ext:",
                     "allinurl:", "allintitle:", "allintext:", "cache:", "link:",
                     "related:", "info:", "before:", "after:"]

        detected_ops = []
        for op in known_ops:
            if op in q.lower():
                detected_ops.append(op)

        if " OR " in q or " | " in q:
            detected_ops.append("OR")
        if " -site:" in q or " -" in q:
            detected_ops.append("- (exclude)")

        # Detect site scope
        site_match = re.search(r'site:([^\s()]+)', q, re.IGNORECASE)
        target_site = site_match.group(1) if site_match else ""

        words = len(q.split())
        chars = len(q)

        # Complexity determination
        op_count = len(detected_ops)
        if op_count >= 3 or words >= 8:
            complexity = "Advanced"
        elif op_count >= 1 or words >= 4:
            complexity = "Moderate"
        else:
            complexity = "Simple"

        explanation = DorkEngine.explain_query(q)

        return {
            "chars": chars,
            "words": words,
            "operators": detected_ops,
            "target_site": target_site,
            "complexity": complexity,
            "explanation": explanation,
            "is_valid": chars > 0
        }
