"""
Technical Website Analyzer - Advanced Security & Bug Detection
Features:
- 🔒 Security vulnerability scanning
- 🐛 Bug detection and reporting
- ⚡ Performance analysis
- 🔍 Technology stack detection
- 📊 SEO & Accessibility audit
- 🌐 Network & DNS analysis
"""

import logging
import requests
import ssl
import socket
from typing import Dict, List, Optional
from urllib.parse import urlparse
import re
from datetime import datetime
import json

try:
    from bs4 import BeautifulSoup
    BS_AVAILABLE = True
except ImportError:
    BS_AVAILABLE = False

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """Advanced technical analysis and security scanning for websites"""
    
    def __init__(self):
        self.session = self._create_session()
        self.vulnerabilities = []
        self.bugs = []
        self.performance_metrics = {}
        
        logger.info("✅ Technical Analyzer initialized")
    
    def _create_session(self) -> requests.Session:
        """Create configured session"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        return session
    
    def analyze_website(self, url: str, deep_scan: bool = True) -> Dict:
        """
        🔍 Complete technical analysis of website
        
        Args:
            url: Website URL to analyze
            deep_scan: Enable deep security scanning
        
        Returns:
            Comprehensive analysis report
        """
        logger.info(f"🔬 Starting technical analysis: {url}")
        
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = 'https://' + url
            parsed_url = urlparse(url)
        
        report = {
            'url': url,
            'domain': parsed_url.netloc,
            'timestamp': datetime.now().isoformat(),
            'security': {},
            'performance': {},
            'technologies': {},
            'bugs': [],
            'seo': {},
            'accessibility': {},
            'recommendations': []
        }
        
        try:
            # 1. Security Analysis
            logger.info("🔒 Security scanning...")
            report['security'] = self._security_scan(url, deep_scan)
            
            # 2. Performance Analysis
            logger.info("⚡ Performance testing...")
            report['performance'] = self._performance_analysis(url)
            
            # 3. Technology Detection
            logger.info("🔍 Detecting technologies...")
            report['technologies'] = self._detect_technologies(url)
            
            # 4. SEO Analysis
            logger.info("📊 SEO audit...")
            report['seo'] = self._seo_analysis(url)
            
            # 5. Accessibility Check
            logger.info("♿ Accessibility check...")
            report['accessibility'] = self._accessibility_check(url)
            
            # 6. Bug Detection
            logger.info("🐛 Bug detection...")
            report['bugs'] = self._detect_bugs(url, report)
            
            # 7. Generate Recommendations
            report['recommendations'] = self._generate_recommendations(report)
            
            # Calculate overall score
            report['overall_score'] = self._calculate_score(report)
            
            logger.info(f"✅ Analysis complete | Score: {report['overall_score']}/100")
            return report
        
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            return {
                'url': url,
                'error': str(e),
                'success': False
            }
    
    def _security_scan(self, url: str, deep: bool) -> Dict:
        """🔒 Security vulnerability scanning"""
        security = {
            'https_enabled': False,
            'ssl_valid': False,
            'ssl_info': {},
            'security_headers': {},
            'vulnerabilities': [],
            'risk_level': 'Unknown'
        }
        
        try:
            # Check HTTPS
            security['https_enabled'] = url.startswith('https://')
            
            if not security['https_enabled']:
                security['vulnerabilities'].append({
                    'severity': 'HIGH',
                    'type': 'No HTTPS',
                    'description': 'Website not using secure HTTPS connection',
                    'recommendation': 'Enable HTTPS with valid SSL certificate'
                })
            
            # SSL Certificate Check
            if security['https_enabled']:
                parsed = urlparse(url)
                hostname = parsed.netloc
                
                try:
                    context = ssl.create_default_context()
                    with socket.create_connection((hostname, 443), timeout=10) as sock:
                        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            cert = ssock.getpeercert()
                            security['ssl_valid'] = True
                            security['ssl_info'] = {
                                'issuer': dict(x[0] for x in cert.get('issuer', [])),
                                'subject': dict(x[0] for x in cert.get('subject', [])),
                                'version': cert.get('version'),
                                'expires': cert.get('notAfter')
                            }
                except Exception as ssl_error:
                    security['ssl_valid'] = False
                    security['vulnerabilities'].append({
                        'severity': 'HIGH',
                        'type': 'SSL Certificate Issue',
                        'description': f'SSL certificate error: {str(ssl_error)[:100]}',
                        'recommendation': 'Fix SSL certificate configuration'
                    })
            
            # Security Headers Check
            response = self.session.get(url, timeout=15, allow_redirects=True)
            headers = response.headers
            
            required_headers = {
                'Strict-Transport-Security': 'HSTS not enabled - forces HTTPS',
                'X-Content-Type-Options': 'MIME type sniffing possible',
                'X-Frame-Options': 'Clickjacking attacks possible',
                'X-XSS-Protection': 'XSS protection not enabled',
                'Content-Security-Policy': 'No CSP - XSS/injection risks',
                'Referrer-Policy': 'Referrer information may leak'
            }
            
            for header, risk in required_headers.items():
                if header in headers:
                    security['security_headers'][header] = {
                        'present': True,
                        'value': headers[header]
                    }
                else:
                    security['security_headers'][header] = {
                        'present': False
                    }
                    security['vulnerabilities'].append({
                        'severity': 'MEDIUM',
                        'type': f'Missing {header}',
                        'description': risk,
                        'recommendation': f'Add {header} header'
                    })
            
            # Cookie Security
            if 'Set-Cookie' in headers:
                cookies = headers.get('Set-Cookie', '')
                if 'Secure' not in cookies:
                    security['vulnerabilities'].append({
                        'severity': 'MEDIUM',
                        'type': 'Insecure Cookies',
                        'description': 'Cookies not marked as Secure',
                        'recommendation': 'Add Secure flag to cookies'
                    })
                if 'HttpOnly' not in cookies:
                    security['vulnerabilities'].append({
                        'severity': 'MEDIUM',
                        'type': 'Cookie XSS Risk',
                        'description': 'Cookies not marked as HttpOnly',
                        'recommendation': 'Add HttpOnly flag to cookies'
                    })
            
            # Deep Scan
            if deep and BS_AVAILABLE:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check for mixed content
                if security['https_enabled']:
                    http_resources = soup.find_all(['img', 'script', 'link'], src=re.compile(r'^http://'))
                    if http_resources:
                        security['vulnerabilities'].append({
                            'severity': 'MEDIUM',
                            'type': 'Mixed Content',
                            'description': f'Found {len(http_resources)} HTTP resources on HTTPS page',
                            'recommendation': 'Use HTTPS for all resources'
                        })
                
                # Check for inline JavaScript
                inline_scripts = soup.find_all('script', src=False)
                if len(inline_scripts) > 5:
                    security['vulnerabilities'].append({
                        'severity': 'LOW',
                        'type': 'Inline JavaScript',
                        'description': f'{len(inline_scripts)} inline scripts found - potential XSS risk',
                        'recommendation': 'Move scripts to external files with CSP'
                    })
            
            # Risk Level
            high_count = sum(1 for v in security['vulnerabilities'] if v['severity'] == 'HIGH')
            medium_count = sum(1 for v in security['vulnerabilities'] if v['severity'] == 'MEDIUM')
            
            if high_count > 2:
                security['risk_level'] = 'CRITICAL'
            elif high_count > 0:
                security['risk_level'] = 'HIGH'
            elif medium_count > 3:
                security['risk_level'] = 'MEDIUM'
            elif medium_count > 0:
                security['risk_level'] = 'LOW'
            else:
                security['risk_level'] = 'MINIMAL'
        
        except Exception as e:
            logger.error(f"Security scan error: {e}")
            security['error'] = str(e)
        
        return security
    
    def _performance_analysis(self, url: str) -> Dict:
        """⚡ Performance and speed analysis"""
        performance = {
            'response_time_ms': 0,
            'status_code': 0,
            'page_size_kb': 0,
            'redirects': 0,
            'server_info': {},
            'issues': []
        }
        
        try:
            import time
            start = time.time()
            response = self.session.get(url, timeout=30, allow_redirects=True)
            elapsed = (time.time() - start) * 1000
            
            performance['response_time_ms'] = round(elapsed, 2)
            performance['status_code'] = response.status_code
            performance['page_size_kb'] = round(len(response.content) / 1024, 2)
            performance['redirects'] = len(response.history)
            
            # Server Info
            performance['server_info'] = {
                'server': response.headers.get('Server', 'Unknown'),
                'powered_by': response.headers.get('X-Powered-By', 'Unknown'),
                'encoding': response.encoding
            }
            
            # Performance Issues
            if elapsed > 3000:
                performance['issues'].append({
                    'type': 'Slow Response',
                    'description': f'Page load took {elapsed:.0f}ms (>3s)',
                    'severity': 'HIGH'
                })
            elif elapsed > 1500:
                performance['issues'].append({
                    'type': 'Moderate Speed',
                    'description': f'Page load took {elapsed:.0f}ms (>1.5s)',
                    'severity': 'MEDIUM'
                })
            
            if performance['page_size_kb'] > 5000:
                performance['issues'].append({
                    'type': 'Large Page Size',
                    'description': f'Page size is {performance["page_size_kb"]:.1f}KB (>5MB)',
                    'severity': 'HIGH'
                })
            elif performance['page_size_kb'] > 2000:
                performance['issues'].append({
                    'type': 'Heavy Page',
                    'description': f'Page size is {performance["page_size_kb"]:.1f}KB (>2MB)',
                    'severity': 'MEDIUM'
                })
            
            if performance['redirects'] > 2:
                performance['issues'].append({
                    'type': 'Multiple Redirects',
                    'description': f'{performance["redirects"]} redirects detected',
                    'severity': 'MEDIUM'
                })
        
        except Exception as e:
            logger.error(f"Performance analysis error: {e}")
            performance['error'] = str(e)
        
        return performance
    
    def _detect_technologies(self, url: str) -> Dict:
        """🔍 Detect web technologies and frameworks"""
        technologies = {
            'server': 'Unknown',
            'frameworks': [],
            'cms': 'Unknown',
            'analytics': [],
            'libraries': [],
            'languages': []
        }
        
        try:
            response = self.session.get(url, timeout=15)
            headers = response.headers
            html = response.text
            
            # Server Detection
            technologies['server'] = headers.get('Server', 'Unknown')
            
            # Framework Detection
            if 'X-Powered-By' in headers:
                powered_by = headers['X-Powered-By']
                technologies['frameworks'].append(powered_by)
            
            # CMS Detection (WordPress, Joomla, Drupal, etc.)
            cms_patterns = {
                'WordPress': ['/wp-content/', '/wp-includes/', 'wp-json'],
                'Joomla': ['/components/com_', '/templates/system/'],
                'Drupal': ['/sites/default/', 'Drupal.settings'],
                'Shopify': ['cdn.shopify.com', 'Shopify.theme'],
                'Wix': ['wix.com', 'static.parastorage.com']
            }
            
            for cms, patterns in cms_patterns.items():
                if any(pattern in html for pattern in patterns):
                    technologies['cms'] = cms
                    break
            
            # Analytics Detection
            analytics_patterns = {
                'Google Analytics': ['google-analytics.com', 'gtag.js', 'ga.js'],
                'Google Tag Manager': ['googletagmanager.com', 'gtm.js'],
                'Facebook Pixel': ['facebook.net/en_US/fbevents.js', 'fbq('],
                'Hotjar': ['hotjar.com/c/hotjar-']
            }
            
            for analytics, patterns in analytics_patterns.items():
                if any(pattern in html for pattern in patterns):
                    technologies['analytics'].append(analytics)
            
            # JavaScript Libraries
            lib_patterns = {
                'jQuery': ['jquery', 'jQuery'],
                'React': ['react.js', 'React.createElement'],
                'Vue.js': ['vue.js', 'Vue.component'],
                'Angular': ['angular.js', 'ng-app'],
                'Bootstrap': ['bootstrap.min.css', 'bootstrap.min.js']
            }
            
            for lib, patterns in lib_patterns.items():
                if any(pattern in html for pattern in patterns):
                    technologies['libraries'].append(lib)
            
            # Language Detection
            if 'X-Powered-By' in headers:
                tech = headers['X-Powered-By'].lower()
                if 'php' in tech:
                    technologies['languages'].append('PHP')
                elif 'asp.net' in tech:
                    technologies['languages'].append('ASP.NET')
            
            if 'Server' in headers:
                server = headers['Server'].lower()
                if 'nginx' in server:
                    technologies['languages'].append('Nginx')
                elif 'apache' in server:
                    technologies['languages'].append('Apache')
        
        except Exception as e:
            logger.error(f"Technology detection error: {e}")
            technologies['error'] = str(e)
        
        return technologies
    
    def _seo_analysis(self, url: str) -> Dict:
        """📊 SEO optimization check"""
        seo = {
            'title': None,
            'description': None,
            'keywords': None,
            'h1_count': 0,
            'images_without_alt': 0,
            'issues': [],
            'score': 0
        }
        
        try:
            if not BS_AVAILABLE:
                return seo
            
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Title
            title_tag = soup.find('title')
            if title_tag:
                seo['title'] = title_tag.get_text().strip()
                if len(seo['title']) < 30:
                    seo['issues'].append('Title too short (<30 chars)')
                elif len(seo['title']) > 60:
                    seo['issues'].append('Title too long (>60 chars)')
            else:
                seo['issues'].append('Missing title tag')
            
            # Meta Description
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            if desc_tag:
                seo['description'] = desc_tag.get('content', '')
                if len(seo['description']) < 120:
                    seo['issues'].append('Meta description too short')
            else:
                seo['issues'].append('Missing meta description')
            
            # Keywords
            keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
            if keywords_tag:
                seo['keywords'] = keywords_tag.get('content', '')
            
            # H1 Tags
            h1_tags = soup.find_all('h1')
            seo['h1_count'] = len(h1_tags)
            if seo['h1_count'] == 0:
                seo['issues'].append('No H1 tag found')
            elif seo['h1_count'] > 1:
                seo['issues'].append(f'Multiple H1 tags ({seo["h1_count"]})')
            
            # Images without ALT
            images = soup.find_all('img')
            seo['images_without_alt'] = sum(1 for img in images if not img.get('alt'))
            if seo['images_without_alt'] > 0:
                seo['issues'].append(f'{seo["images_without_alt"]} images without alt text')
            
            # Calculate SEO Score
            max_score = 100
            if not seo['title']:
                max_score -= 20
            if not seo['description']:
                max_score -= 20
            if seo['h1_count'] != 1:
                max_score -= 15
            if seo['images_without_alt'] > 0:
                max_score -= min(20, seo['images_without_alt'] * 2)
            
            seo['score'] = max(0, max_score)
        
        except Exception as e:
            logger.error(f"SEO analysis error: {e}")
            seo['error'] = str(e)
        
        return seo
    
    def _accessibility_check(self, url: str) -> Dict:
        """♿ Accessibility compliance check"""
        accessibility = {
            'issues': [],
            'score': 100
        }
        
        try:
            if not BS_AVAILABLE:
                return accessibility
            
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Language attribute
            html_tag = soup.find('html')
            if not html_tag or not html_tag.get('lang'):
                accessibility['issues'].append('Missing lang attribute in <html>')
                accessibility['score'] -= 15
            
            # Form labels
            inputs = soup.find_all('input', type=['text', 'email', 'password'])
            for inp in inputs:
                if not inp.get('aria-label') and not soup.find('label', attrs={'for': inp.get('id')}):
                    accessibility['issues'].append(f'Input without label: {inp.get("name", "unknown")}')
                    accessibility['score'] -= 5
            
            # ARIA landmarks
            if not soup.find(['main', 'header', 'footer', 'nav']):
                accessibility['issues'].append('No semantic HTML5 elements found')
                accessibility['score'] -= 10
        
        except Exception as e:
            logger.error(f"Accessibility check error: {e}")
            accessibility['error'] = str(e)
        
        return accessibility
    
    def _detect_bugs(self, url: str, report: Dict) -> List[Dict]:
        """🐛 Detect potential bugs and issues"""
        bugs = []
        
        # From Security Vulnerabilities
        for vuln in report.get('security', {}).get('vulnerabilities', []):
            bugs.append({
                'category': 'Security',
                'severity': vuln['severity'],
                'issue': vuln['type'],
                'description': vuln['description'],
                'fix': vuln['recommendation']
            })
        
        # From Performance Issues
        for issue in report.get('performance', {}).get('issues', []):
            bugs.append({
                'category': 'Performance',
                'severity': issue['severity'],
                'issue': issue['type'],
                'description': issue['description'],
                'fix': 'Optimize page resources and caching'
            })
        
        # From SEO Issues
        for issue in report.get('seo', {}).get('issues', []):
            bugs.append({
                'category': 'SEO',
                'severity': 'LOW',
                'issue': 'SEO Issue',
                'description': issue,
                'fix': 'Follow SEO best practices'
            })
        
        return bugs
    
    def _generate_recommendations(self, report: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Security
        if report['security'].get('risk_level') in ['HIGH', 'CRITICAL']:
            recommendations.append('🔒 CRITICAL: Address security vulnerabilities immediately')
        
        if not report['security'].get('https_enabled'):
            recommendations.append('Enable HTTPS with valid SSL certificate')
        
        # Performance
        if report['performance'].get('response_time_ms', 0) > 2000:
            recommendations.append('⚡ Optimize server response time (<2s)')
        
        if report['performance'].get('page_size_kb', 0) > 2000:
            recommendations.append('Reduce page size with compression and optimization')
        
        # SEO
        if report['seo'].get('score', 0) < 70:
            recommendations.append('📊 Improve SEO: Add meta tags, H1, and alt text')
        
        # Accessibility
        if report['accessibility'].get('score', 100) < 80:
            recommendations.append('♿ Improve accessibility for better user experience')
        
        return recommendations
    
    def _calculate_score(self, report: Dict) -> int:
        """Calculate overall website score (0-100)"""
        scores = []
        
        # Security Score (30%)
        risk_levels = {'MINIMAL': 100, 'LOW': 85, 'MEDIUM': 70, 'HIGH': 50, 'CRITICAL': 30}
        security_score = risk_levels.get(report['security'].get('risk_level', 'CRITICAL'), 30)
        scores.append(security_score * 0.30)
        
        # Performance Score (25%)
        response_time = report['performance'].get('response_time_ms', 5000)
        if response_time < 1000:
            perf_score = 100
        elif response_time < 2000:
            perf_score = 80
        elif response_time < 3000:
            perf_score = 60
        else:
            perf_score = 40
        scores.append(perf_score * 0.25)
        
        # SEO Score (25%)
        seo_score = report['seo'].get('score', 50)
        scores.append(seo_score * 0.25)
        
        # Accessibility Score (20%)
        access_score = report['accessibility'].get('score', 50)
        scores.append(access_score * 0.20)
        
        return round(sum(scores))
    
    def format_report_for_article(self, report: Dict) -> str:
        """Format technical report for article inclusion"""
        sections = []
        
        sections.append(f"# Technical Analysis: {report['domain']}")
        sections.append(f"\n**Overall Score:** {report['overall_score']}/100")
        sections.append(f"**Analysis Date:** {report['timestamp']}")
        
        # Security Section
        sections.append("\n## 🔒 Security Analysis")
        security = report['security']
        sections.append(f"- **Risk Level:** {security.get('risk_level', 'Unknown')}")
        sections.append(f"- **HTTPS Enabled:** {'✅ Yes' if security.get('https_enabled') else '❌ No'}")
        sections.append(f"- **SSL Valid:** {'✅ Yes' if security.get('ssl_valid') else '❌ No'}")
        
        if security.get('vulnerabilities'):
            sections.append(f"\n**Vulnerabilities Found:** {len(security['vulnerabilities'])}")
            for vuln in security['vulnerabilities'][:5]:
                sections.append(f"- [{vuln['severity']}] {vuln['type']}: {vuln['description']}")
        
        # Performance Section
        sections.append("\n## ⚡ Performance Metrics")
        perf = report['performance']
        sections.append(f"- **Response Time:** {perf.get('response_time_ms', 0):.0f}ms")
        sections.append(f"- **Page Size:** {perf.get('page_size_kb', 0):.1f}KB")
        sections.append(f"- **Status Code:** {perf.get('status_code', 0)}")
        sections.append(f"- **Server:** {perf.get('server_info', {}).get('server', 'Unknown')}")
        
        # Technologies
        sections.append("\n## 🔍 Detected Technologies")
        tech = report['technologies']
        sections.append(f"- **CMS:** {tech.get('cms', 'Unknown')}")
        if tech.get('frameworks'):
            sections.append(f"- **Frameworks:** {', '.join(tech['frameworks'])}")
        if tech.get('libraries'):
            sections.append(f"- **Libraries:** {', '.join(tech['libraries'])}")
        
        # Recommendations
        if report.get('recommendations'):
            sections.append("\n## 💡 Recommendations")
            for rec in report['recommendations']:
                sections.append(f"- {rec}")
        
        return '\n'.join(sections)
