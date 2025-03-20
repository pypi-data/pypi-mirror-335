from typing import List, Dict, Optional, Union, Any
import json
import base64
from datetime import datetime
import re
from urllib.parse import urlparse


class BrowserTools:
    """Enhanced browser automation tools specifically for AI agents"""

    def __init__(self, page=None):
        self.page = page or browser_manager.current_page
        if not self.page:
            raise RuntimeError("No browser instance is running")

    async def extract_page_content(self) -> Dict[str, Any]:
        """
        Extract structured content from current page.
        Returns title, main text, links, and other key elements
        """
        return await self.page.evaluate("""() => {
            function extractText(element) {
                return element ? element.innerText.trim() : '';
            }

            return {
                title: document.title,
                url: window.location.href,
                mainText: extractText(document.querySelector('main')) || 
                         extractText(document.querySelector('article')) ||
                         document.body.innerText.substring(0, 1500),
                headings: Array.from(document.querySelectorAll('h1, h2, h3'))
                    .map(h => h.innerText.trim()),
                links: Array.from(document.querySelectorAll('a'))
                    .map(a => ({text: a.innerText.trim(), href: a.href}))
                    .filter(l => l.text && l.href),
                timestamp: new Date().toISOString()
            };
        }""")

    async def get_element_info(self, element: Union[str, ElementHandle, Locator]) -> Dict[str, Any]:
        """
        Get detailed information about an element
        """
        if isinstance(element, str):
            element = self.page.locator(f'text={element}')

        info = {
            'text': await element.text_content(),
            'tag': await element.evaluate('el => el.tagName.toLowerCase()'),
            'isVisible': await element.is_visible(),
            'attributes': await element.evaluate(
                'el => Object.fromEntries(Array.from(el.attributes).map(a => [a.name, a.value]))'),
            'boundingBox': await element.bounding_box(),
        }
        return info

    async def extract_structured_data(self) -> List[Dict[str, Any]]:
        """
        Extract JSON-LD, microdata, and other structured data from page
        """
        return await self.page.evaluate("""() => {
            const jsonLd = Array.from(document.querySelectorAll('script[type="application/ld+json"]'))
                .map(script => {
                    try {
                        return JSON.parse(script.textContent);
                    } catch (e) {
                        return null;
                    }
                })
                .filter(data => data);

            return jsonLd;
        }""")

    async def get_page_metrics(self) -> Dict[str, Any]:
        """
        Get various page metrics and statistics
        """
        metrics = {}

        # Performance metrics
        timing = await self.page.evaluate('() => performance.timing.toJSON()')
        metrics['performance'] = timing

        # Page statistics
        metrics['statistics'] = await self.page.evaluate("""() => ({
            images: document.images.length,
            links: document.links.length,
            forms: document.forms.length,
            scripts: document.scripts.length,
            wordCount: document.body.innerText.split(/\s+/).length
        })""")

        return metrics


class NavigationTools:
    """Tools for advanced navigation and browsing"""

    def __init__(self, page=None):
        self.page = page or browser_manager.current_page
        if not self.page:
            raise RuntimeError("No browser instance is running")

    async def smart_navigation(self, target: str) -> bool:
        """
        Intelligently navigate to target content using multiple strategies
        """
        strategies = [
            self._try_direct_link,
            self._try_button_click,
            self._try_menu_navigation,
            self._try_search
        ]

        for strategy in strategies:
            if await strategy(target):
                return True
        return False

    async def _try_direct_link(self, target: str) -> bool:
        try:
            link = self.page.locator(f'a:has-text("{target}")')
            if await link.count() > 0:
                await link.click()
                return True
        except:
            return False

    async def _try_button_click(self, target: str) -> bool:
        try:
            button = self.page.locator(f'button:has-text("{target}")')
            if await button.count() > 0:
                await button.click()
                return True
        except:
            return False

    async def _try_menu_navigation(self, target: str) -> bool:
        # Try common menu patterns
        menu_selectors = [
            'nav a', '.menu a', '.navigation a',
            '[role="navigation"] a', '.nav-links a'
        ]

        for selector in menu_selectors:
            try:
                menu_items = self.page.locator(selector)
                count = await menu_items.count()
                for i in range(count):
                    item = menu_items.nth(i)
                    if target.lower() in (await item.text_content()).lower():
                        await item.click()
                        return True
            except:
                continue
        return False

    async def _try_search(self, target: str) -> bool:
        # Try using search functionality if available
        search_selectors = [
            '[type="search"]',
            '[aria-label*="search" i]',
            '[placeholder*="search" i]'
        ]

        for selector in search_selectors:
            try:
                search = self.page.locator(selector)
                if await search.count() > 0:
                    await search.fill(target)
                    await self.page.keyboard.press('Enter')
                    return True
            except:
                continue
        return False


class FormTools:
    """Tools for advanced form handling"""

    def __init__(self, page=None):
        self.page = page or browser_manager.current_page
        if not self.page:
            raise RuntimeError("No browser instance is running")

    async def smart_fill_form(self, data: Dict[str, str]) -> bool:
        """
        Intelligently fill form fields using various strategies
        """
        for field_name, value in data.items():
            if not await self._try_fill_field(field_name, value):
                print(f"Failed to fill field: {field_name}")
                return False
        return True

    async def _try_fill_field(self, field_name: str, value: str) -> bool:
        # Try multiple strategies to locate and fill the field
        selectors = [
            f'[name="{field_name}"]',
            f'[id*="{field_name}" i]',
            f'[aria-label*="{field_name}" i]',
            f'label:has-text("{field_name}") >> input',
            f'input[placeholder*="{field_name}" i]'
        ]

        for selector in selectors:
            try:
                field = self.page.locator(selector)
                if await field.count() > 0:
                    await field.fill(value)
                    return True
            except:
                continue
        return False

    async def extract_form_data(self) -> Dict[str, Any]:
        """
        Extract all form fields and their values from the page
        """
        return await self.page.evaluate("""() => {
            const forms = Array.from(document.forms);
            return forms.map(form => {
                const fields = Array.from(form.elements);
                return {
                    id: form.id,
                    action: form.action,
                    method: form.method,
                    fields: fields.map(field => ({
                        name: field.name,
                        type: field.type,
                        value: field.value,
                        isRequired: field.required,
                        isDisabled: field.disabled
                    }))
                };
            });
        }""")


class ContentTools:
    """Tools for content extraction and analysis"""

    def __init__(self, page=None):
        self.page = page or browser_manager.current_page
        if not self.page:
            raise RuntimeError("No browser instance is running")

    async def extract_table_data(self) -> List[Dict[str, Any]]:
        """
        Extract data from HTML tables
        """
        return await self.page.evaluate("""() => {
            return Array.from(document.querySelectorAll('table')).map(table => {
                const headers = Array.from(table.querySelectorAll('th'))
                    .map(th => th.innerText.trim());

                const rows = Array.from(table.querySelectorAll('tr'))
                    .map(tr => Array.from(tr.querySelectorAll('td'))
                        .map(td => td.innerText.trim()));

                return {
                    headers,
                    rows,
                    caption: table.caption ? table.caption.innerText.trim() : null
                };
            });
        }""")

    async def extract_lists(self) -> List[Dict[str, Any]]:
        """
        Extract data from ordered and unordered lists
        """
        return await self.page.evaluate("""() => {
            return Array.from(document.querySelectorAll('ul, ol')).map(list => ({
                type: list.tagName.toLowerCase(),
                items: Array.from(list.querySelectorAll('li'))
                    .map(li => li.innerText.trim())
            }));
        }""")

    async def get_main_content(self) -> str:
        """
        Extract main content while filtering out navigation, ads, etc.
        """
        return await self.page.evaluate("""() => {
            const articleContent = document.querySelector('article, [role="article"], .post-content, .article-content');
            if (articleContent) return articleContent.innerText;

            // Remove noisy elements
            const elementsToRemove = [
                'header',
                'footer',
                'nav',
                '[role="navigation"]',
                '.navigation',
                '.ads',
                '.sidebar',
                '#sidebar',
                '.menu',
                '.comments'
            ];

            const content = document.body.cloneNode(true);
            elementsToRemove.forEach(selector => {
                content.querySelectorAll(selector).forEach(el => el.remove());
            });

            return content.innerText.trim();
        }""")


class SecurityTools:
    """Tools for security testing and validation"""

    def __init__(self, page=None):
        self.page = page or browser_manager.current_page
        if not self.page:
            raise RuntimeError("No browser instance is running")

    async def check_security_headers(self) -> Dict[str, str]:
        """
        Check security-related HTTP headers
        """
        response = await self.page.main_frame.response()
        if not response:
            return {}

        headers = await response.all_headers()
        security_headers = {
            'Content-Security-Policy',
            'X-Frame-Options',
            'X-XSS-Protection',
            'X-Content-Type-Options',
            'Strict-Transport-Security',
            'Referrer-Policy'
        }

        return {k: v for k, v in headers.items() if k in security_headers}

    async def check_forms_security(self) -> List[Dict[str, Any]]:
        """
        Check forms for basic security best practices
        """
        return await self.page.evaluate("""() => {
            return Array.from(document.forms).map(form => ({
                action: form.action,
                method: form.method,
                hasCSRF: !!form.querySelector('input[name*="csrf" i]'),
                isSecure: form.action.startsWith('https://'),
                autocompleteOff: form.autocomplete === 'off',
                hasPasswordField: !!form.querySelector('input[type="password"]')
            }));
        }""")


class AccessibilityTools:
    """Tools for accessibility testing and validation"""

    def __init__(self, page=None):
        self.page = page or browser_manager.current_page
        if not self.page:
            raise RuntimeError("No browser instance is running")

    async def check_accessibility(self) -> Dict[str, Any]:
        """
        Perform basic accessibility checks
        """
        return await self.page.evaluate("""() => {
            const results = {
                images: {
                    total: 0,
                    withoutAlt: 0
                },
                headings: {
                    order: [],
                    proper: true
                },
                landmarks: [],
                forms: {
                    withoutLabels: 0,
                    total: 0
                }
            };

            // Check images
            document.querySelectorAll('img').forEach(img => {
                results.images.total++;
                if (!img.alt) results.images.withoutAlt++;
            });

            // Check heading order
            document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(h => {
                const level = parseInt(h.tagName[1]);
                results.headings.order.push(level);
            });

            // Check landmarks
            document.querySelectorAll('[role]').forEach(el => {
                results.landmarks.push(el.getAttribute('role'));
            });

            // Check forms
            document.querySelectorAll('form').forEach(form => {
                results.forms.total++;
                const inputs = form.querySelectorAll('input, select, textarea');
                inputs.forEach(input => {
                    if (!input.id || !document.querySelector(`label[for="${input.id}"]`)) {
                        results.forms.withoutLabels++;
                    }
                });
            });

            return results;
        }""")


class SEOTools:
    """Tools for SEO analysis"""

    def __init__(self, page=None):
        self.page = page or browser_manager.current_page
        if not self.page:
            raise RuntimeError("No browser instance is running")

    async def analyze_seo(self) -> Dict[str, Any]:
        """
        Perform comprehensive SEO analysis
        """
        return await self.page.evaluate("""() => {
            const results = {
                title: {
                    text: document.title,
                    length: document.title.length,
                    isOptimalLength: document.title.length >= 30 && document.title.length <= 60
                },
                meta: {
                    description: document.querySelector('meta[name="description"]')?.content,
                    keywords: document.querySelector('meta[name="keywords"]')?.content,
                    robots: document.querySelector('meta[name="robots"]')?.content,
                    viewport: document.querySelector('meta[name="viewport"]')?.content,
                    charset: document.characterSet
                },
                headings: {
                    h1: Array.from(document.querySelectorAll('h1')).map(h => ({
                        text: h.innerText.trim(),
                        length: h.innerText.trim().length
                    })),
                    h2: Array.from(document.querySelectorAll('h2')).map(h => ({
                        text: h.innerText.trim(),
                        length: h.innerText.trim().length
                    }))
                },
                images: Array.from(document.images).map(img => ({
                    src: img.src,
                    alt: img.alt,
                    hasAlt: !!img.alt,
                    dimensions: {
                        width: img.width,
                        height: img.height
                    }
                })),
                links: {
                    internal: Array.from(document.links).filter(link => 
                        link.hostname === window.location.hostname
                    ).length,
                    external: Array.from(document.links).filter(link => 
                        link.hostname !== window.location.hostname
                    ).length,
                    hasNofollow: Array.from(document.links).filter(link => 
                        link.rel.includes('nofollow')
                    ).length
                },
                social: {
                    openGraph: {
                        title: document.querySelector('meta[property="og:title"]')?.content,
                        description: document.querySelector('meta[property="og:description"]')?.content,
                        image: document.querySelector('meta[property="og:image"]')?.content,
                        url: document.querySelector('meta[property="og:url"]')?.content
                    },
                    twitter: {
                        card: document.querySelector('meta[name="twitter:card"]')?.content,
                        title: document.querySelector('meta[name="twitter:title"]')?.content,
                        description: document.querySelector('meta[name="twitter:description"]')?.content,
                        image: document.querySelector('meta[name="twitter:image"]')?.content
                    }
                },
                performance: {
                    textToHtmlRatio: (() => {
                        const htmlSize = document.documentElement.outerHTML.length;
                        const textSize = document.body.innerText.length;
                        return (textSize / htmlSize * 100).toFixed(2);
                    })(),
                    hasAmp: !!document.querySelector('link[rel="amphtml"]'),
                    hasFavicon: !!document.querySelector('link[rel="icon"]') || 
                               !!document.querySelector('link[rel="shortcut icon"]')
                }
            };

            // Add canonical URL info
            const canonical = document.querySelector('link[rel="canonical"]');
            results.canonical = canonical ? canonical.href : null;

            return results;
        }""")

    async def check_keyword_density(self, keyword: str) -> Dict[str, Any]:
        """
        Analyze keyword density and placement
        """
        return await self.page.evaluate("""(keyword) => {
            const text = document.body.innerText.toLowerCase();
            const keywordLower = keyword.toLowerCase();

            const count = (text.match(new RegExp(keywordLower, 'g')) || []).length;
            const words = text.split(/\s+/).length;
            const density = (count / words * 100).toFixed(2);

            // Check keyword in important elements
            const results = {
                count: count,
                density: density,
                inTitle: document.title.toLowerCase().includes(keywordLower),
                inDescription: document.querySelector('meta[name="description"]')?.content.toLowerCase().includes(keywordLower) || false,
                inH1: Array.from(document.querySelectorAll('h1')).some(h => 
                    h.innerText.toLowerCase().includes(keywordLower)
                ),
                inFirstParagraph: document.querySelector('p')?.innerText.toLowerCase().includes(keywordLower) || false
            };

            return results;
        }""", keyword)


class ScrapingTools:
    """Advanced tools for web scraping"""

    def __init__(self, page=None):
        self.page = page or browser_manager.current_page
        if not self.page:
            raise RuntimeError("No browser instance is running")

    async def extract_schema_data(self) -> List[Dict[str, Any]]:
        """
        Extract all schema.org structured data
        """
        return await self.page.evaluate("""() => {
            return Array.from(document.querySelectorAll('script[type="application/ld+json"]'))
                .map(script => {
                    try {
                        return JSON.parse(script.textContent);
                    } catch (e) {
                        return null;
                    }
                })
                .filter(data => data);
        }""")

    async def extract_products(self) -> List[Dict[str, Any]]:
        """
        Extract product information from e-commerce pages
        """
        return await self.page.evaluate("""() => {
            function extractPrice(element) {
                const priceText = element.innerText.match(/[\d,.]+/);
                return priceText ? priceText[0] : null;
            }

            const products = [];
            const productElements = document.querySelectorAll(
                '[itemtype*="Product"], .product, [class*="product"], [id*="product"]'
            );

            productElements.forEach(el => {
                const product = {
                    name: el.querySelector('[itemprop="name"], .product-name, .title, h1, h2, h3')?.innerText.trim(),
                    price: el.querySelector('[itemprop="price"], .price, .product-price')?.innerText.trim(),
                    currency: el.querySelector('[itemprop="priceCurrency"]')?.content,
                    description: el.querySelector('[itemprop="description"], .description')?.innerText.trim(),
                    image: el.querySelector('[itemprop="image"], img')?.src,
                    sku: el.querySelector('[itemprop="sku"]')?.content,
                    availability: el.querySelector('[itemprop="availability"]')?.content
                };

                if (product.name) {
                    products.push(product);
                }
            });

            return products;
        }""")

    async def extract_contact_info(self) -> Dict[str, Any]:
        """
        Extract contact information from the page
        """
        return await self.page.evaluate("""() => {
            function findEmails(text) {
                return text.match(/[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+/gi) || [];
            }

            function findPhones(text) {
                return text.match(/[\+]?\d{1,3}[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}/g) || [];
            }

            const pageText = document.body.innerText;

            return {
                emails: [...new Set(findEmails(pageText))],
                phones: [...new Set(findPhones(pageText))],
                address: document.querySelector('[itemprop="address"], .address, [class*="address"]')?.innerText.trim(),
                socialLinks: {
                    facebook: Array.from(document.querySelectorAll('a[href*="facebook.com"]')).map(a => a.href),
                    twitter: Array.from(document.querySelectorAll('a[href*="twitter.com"]')).map(a => a.href),
                    linkedin: Array.from(document.querySelectorAll('a[href*="linkedin.com"]')).map(a => a.href),
                    instagram: Array.from(document.querySelectorAll('a[href*="instagram.com"]')).map(a => a.href)
                }
            };
        }""")


class PerformanceTools:
    """Tools for performance monitoring and analysis"""

    def __init__(self, page=None):
        self.page = page or browser_manager.current_page
        if not self.page:
            raise RuntimeError("No browser instance is running")

    async def measure_performance(self) -> Dict[str, Any]:
        """
        Measure various performance metrics
        """
        metrics = {}

        # Get performance timing
        timing = await self.page.evaluate("""() => {
            const t = performance.timing;
            return {
                dnsLookup: t.domainLookupEnd - t.domainLookupStart,
                tcpConnection: t.connectEnd - t.connectStart,
                serverResponse: t.responseStart - t.requestStart,
                domLoad: t.domContentLoadedEventEnd - t.navigationStart,
                fullPageLoad: t.loadEventEnd - t.navigationStart
            };
        }""")
        metrics['timing'] = timing

        # Get resource timing
        resources = await self.page.evaluate("""() => {
            return performance.getEntriesByType('resource').map(r => ({
                name: r.name,
                type: r.initiatorType,
                duration: r.duration,
                size: r.transferSize
            }));
        }""")
        metrics['resources'] = resources

        # Memory usage (if available)
        try:
            memory = await self.page.evaluate("() => performance.memory")
            metrics['memory'] = memory
        except:
            metrics['memory'] = None

        return metrics

    async def analyze_network(self) -> Dict[str, Any]:
        """
        Analyze network requests and responses
        """
        client = await self.page.context.new_cdp_session(self.page)
        await client.send('Network.enable')

        # Collect network data for 5 seconds
        requests = []

        def handle_network_request(request):
            requests.append({
                'url': request.url,
                'method': request.method,
                'headers': request.headers,
                'resourceType': request.resource_type
            })

        self.page.on('request', handle_network_request)
        await asyncio.sleep(5)
        self.page.remove_listener('request', handle_network_request)

        return {
            'requestCount': len(requests),
            'requestsByType': {},
            'domains': list(set(urlparse(r['url']).netloc for r in requests)),
            'requests': requests
        }


class UITestTools:
    """Tools for UI testing and validation"""

    def __init__(self, page=None):
        self.page = page or browser_manager.current_page
        if not self.page:
            raise RuntimeError("No browser instance is running")

    async def check_responsive_design(self, viewports: List[Dict[str, int]]) -> Dict[str, Any]:
        """
        Test page at different viewport sizes
        """
        results = {}
        original_viewport = await self.page.viewport_size()

        for viewport in viewports:
            await self.page.set_viewport_size(viewport)
            results[f"{viewport['width']}x{viewport['height']}"] = {
                'horizontalScroll': await self.page.evaluate("""() => 
                    document.documentElement.scrollWidth > window.innerWidth
                """),
                'elementsOutsideViewport': await self.page.evaluate("""() => {
                    const rect = el => el.getBoundingClientRect();
                    return Array.from(document.querySelectorAll('*')).filter(el => 
                        rect(el).left < 0 || rect(el).right > window.innerWidth
                    ).length;
                }""")
            }

        # Restore original viewport
        await self.page.set_viewport_size(original_viewport)
        return results

    async def validate_ui_elements(self) -> Dict[str, Any]:
        """
        Validate various UI elements for proper rendering and accessibility
        """
        return await self.page.evaluate("""() => {
            const results = {
                clickableElements: {
                    total: 0,
                    tooSmall: 0,
                    overlapping: 0
                },
                colorContrast: [],
                fontSizes: [],
                spacing: {
                    tooClose: 0
                }
            };

            // Check clickable elements
            const clickables = document.querySelectorAll('button, a, [role="button"], input[type="submit"]');
            clickables.forEach(el => {
                const rect = el.getBoundingClientRect();
                results.clickableElements.total++;

                // Check size (44x44 is recommended minimum touch target size)
                if (rect.width < 44 || rect.height < 44) {
                    results.clickableElements.tooSmall++;
                }
            });

            // Sample font sizes
            document.querySelectorAll('p, span, div, a').forEach(el => {
                const size = window.getComputedStyle(el).fontSize;
                if (!results.fontSizes.includes(size)) {
                    results.fontSizes.push(size);
                }
            });

            return results;
        }""")


class ContentAnalysisTools:
    """Tools for analyzing page content"""

    def __init__(self, page=None):
        self.page = page or browser_manager.current_page
        if not self.page:
            raise RuntimeError("No browser instance is running")

    async def analyze_readability(self) -> Dict[str, Any]:
        """
        Analyze text content readability
        """
        return await self.page.evaluate("""() => {
            function calculateReadingTime(text) {
                const wordsPerMinute = 200;
                const words = text.trim().split(/\s+/).length;
                return Math.ceil(words / wordsPerMinute);
            }

            const mainText = document.body.innerText;
            const sentences = mainText.split(/[.!?]+/);

            return {
                readingTime: calculateReadingTime(mainText),
                statistics: {
                    characters: mainText.length,
                    words: mainText.trim().split(/\s+/).length,
                    sentences: sentences.length,
                    averageSentenceLength: Math.round(
                        mainText.trim().split(/\s+/).length / sentences.length
                    ),
                    paragraphs: document.querySelectorAll('p').length
                },
                structure: {
                    headings: {
                        h1: document.querySelectorAll('h1').length,
                        h2: document.querySelectorAll('h2').length,
                        h3: document.querySelectorAll('h3').length
                    },
                    lists: {
                        unordered: document.querySelectorAll('ul').length,
                        ordered: document.querySelectorAll('ol').length
                    },
                    emphasis: {
                        bold: document.querySelectorAll('strong, b').length,
                        italic: document.querySelectorAll('em, i').length
                    }
                }
            };
        }""")

    async def find_broken_images(self) -> List[Dict[str, str]]:
        """
        Find broken image links and analyze image usage
        """
        return await self.page.evaluate("""() => {
            const images = Array.from(document.getElementsByTagName('img'));
            return images.map(img => ({
                src: img.src,
                alt: img.alt,
                dimensions: {
                    width: img.naturalWidth,
                    height: img.naturalHeight,
                    displayWidth: img.width,
                    displayHeight: img.height
                },
                loading: img.loading || 'eager',
                isBroken: !img.complete || !img.naturalWidth,
                isOptimized: img.src.includes('.webp') || img.srcset,
                hasDimensions: img.hasAttribute('width') && img.hasAttribute('height'),
                isScaled: img.width !== img.naturalWidth || img.height !== img.naturalHeight
            }));
        }""")

    async def extract_important_content(self) -> Dict[str, Any]:
        """
        Extract key content using various heuristics
        """
        return await self.page.evaluate("""() => {
            function getTextFromElement(element) {
                return element ? element.innerText.trim() : null;
            }

            // Helper to get text importance score
            function getImportanceScore(element) {
                let score = 0;
                // Size-based importance
                const style = window.getComputedStyle(element);
                const fontSize = parseInt(style.fontSize);
                score += fontSize - 12; // Base score on font size

                // Position-based importance
                const rect = element.getBoundingClientRect();
                score -= rect.top / 100; // Higher elements score better

                // Format-based importance
                if (element.tagName.match(/H[1-6]/)) score += 50 - parseInt(element.tagName[1]) * 10;
                if (style.fontWeight === 'bold' || style.fontWeight >= 500) score += 10;

                return score;
            }

            const content = {
                mainHeading: getTextFromElement(document.querySelector('h1')),
                keyPoints: [],
                importantPhrases: [],
                contentAreas: [],
                navigationStructure: []
            };

            // Extract key points from lists
            document.querySelectorAll('ul li, ol li').forEach(item => {
                if (item.innerText.length > 10 && item.innerText.length < 200) {
                    content.keyPoints.push(item.innerText.trim());
                }
            });

            // Find important phrases based on formatting
            document.querySelectorAll('p, span, div').forEach(element => {
                const text = element.innerText.trim();
                const score = getImportanceScore(element);

                if (score > 20 && text.length > 10 && text.length < 300) {
                    content.importantPhrases.push({
                        text: text,
                        score: score,
                        element: element.tagName.toLowerCase()
                    });
                }
            });

            // Identify main content areas
            document.querySelectorAll('article, [role="main"], main, .content, #content').forEach(area => {
                content.contentAreas.push({
                    type: area.tagName.toLowerCase(),
                    id: area.id,
                    className: area.className,
                    textLength: area.innerText.length,
                    hasImages: area.querySelectorAll('img').length > 0
                });
            });

            // Extract navigation structure
            document.querySelectorAll('nav, [role="navigation"]').forEach(nav => {
                const links = Array.from(nav.querySelectorAll('a')).map(a => ({
                    text: a.innerText.trim(),
                    href: a.href,
                    isActive: a.classList.contains('active') || a.getAttribute('aria-current') === 'page'
                }));

                content.navigationStructure.push({
                    position: nav.getBoundingClientRect().top < window.innerHeight / 2 ? 'header' : 'footer',
                    links: links
                });
            });

            return content;
        }""")

    async def analyze_content_hierarchy(self) -> Dict[str, Any]:
        """
        Analyze the content structure and hierarchy
        """
        return await self.page.evaluate("""() => {
            function buildHierarchy(element, depth = 0) {
                const children = Array.from(element.children);
                return {
                    tag: element.tagName.toLowerCase(),
                    type: element.getAttribute('role') || element.tagName.toLowerCase(),
                    id: element.id || null,
                    classes: Array.from(element.classList),
                    textContent: element.children.length === 0 ? element.textContent.trim() : null,
                    depth: depth,
                    children: children.map(child => buildHierarchy(child, depth + 1))
                };
            }

            return {
                hierarchy: buildHierarchy(document.body),
                sections: Array.from(document.querySelectorAll('section, article, aside, nav')).map(section => ({
                    type: section.tagName.toLowerCase(),
                    id: section.id,
                    heading: section.querySelector('h1, h2, h3, h4, h5, h6')?.innerText.trim(),
                    contentLength: section.innerText.length,
                    hasMedia: section.querySelectorAll('img, video, audio').length > 0
                }))
            };
        }""")

    async def extract_embedded_content(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract information about embedded content (videos, iframes, etc.)
        """
        return await self.page.evaluate("""() => {
            return {
                videos: Array.from(document.querySelectorAll('video, [class*="video"], [id*="video"]')).map(video => ({
                    type: video.tagName.toLowerCase(),
                    src: video.src || video.querySelector('source')?.src,
                    width: video.offsetWidth,
                    height: video.offsetHeight,
                    hasControls: video.hasAttribute('controls'),
                    isAutoplay: video.hasAttribute('autoplay')
                })),
                iframes: Array.from(document.querySelectorAll('iframe')).map(iframe => ({
                    src: iframe.src,
                    width: iframe.offsetWidth,
                    height: iframe.offsetHeight,
                    title: iframe.title,
                    isEmbedded: iframe.src.includes('youtube.com') || 
                               iframe.src.includes('vimeo.com') ||
                               iframe.src.includes('maps.google.com')
                })),
                audio: Array.from(document.querySelectorAll('audio')).map(audio => ({
                    src: audio.src || audio.querySelector('source')?.src,
                    hasControls: audio.hasAttribute('controls'),
                    isAutoplay: audio.hasAttribute('autoplay')
                }))
            };
        }""")

    async def analyze_text_patterns(self) -> Dict[str, Any]:
        """
        Analyze text patterns and content structure
        """
        return await self.page.evaluate("""() => {
            const fullText = document.body.innerText;

            // Find common patterns
            const patterns = {
                emails: fullText.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g) || [],
                phones: fullText.match(/[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}/g) || [],
                urls: fullText.match(/https?:\/\/[^\s]+/g) || [],
                dates: fullText.match(/\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4}/g) || [],
                prices: fullText.match(/[\$\€\£\¥](\d+|\d{1,3}(,\d{3})*)(\.\d+)?/g) || []
            };

            // Analyze text structure
            const paragraphs = Array.from(document.querySelectorAll('p')).map(p => ({
                length: p.innerText.length,
                wordsCount: p.innerText.trim().split(/\s+/).length,
                hasLinks: p.querySelectorAll('a').length > 0,
                hasEmphasis: p.querySelectorAll('strong, em, b, i').length > 0
            }));

            return {
                patterns,
                paragraphAnalysis: {
                    total: paragraphs.length,
                    averageLength: paragraphs.reduce((acc, p) => acc + p.length, 0) / paragraphs.length,
                    averageWordsCount: paragraphs.reduce((acc, p) => acc + p.wordsCount, 0) / paragraphs.length,
                    withLinks: paragraphs.filter(p => p.hasLinks).length,
                    withEmphasis: paragraphs.filter(p => p.hasEmphasis).length
                },
                vocabulary: {
                    uniqueWords: new Set(fullText.toLowerCase().match(/\b\w+\b/g)).size,
                    wordFrequency: Object.fromEntries(
                        Object.entries(
                            fullText.toLowerCase()
                                .match(/\b\w+\b/g)
                                .reduce((acc, word) => {
                                    acc[word] = (acc[word] || 0) + 1;
                                    return acc;
                                }, {})
                        ).sort((a, b) => b[1] - a[1]).slice(0, 20)
                    )
                }
            };
        }""")

    async def extract_code_samples(self) -> List[Dict[str, Any]]:
        """
        Extract and analyze code samples from the page
        """
        return await self.page.evaluate("""() => {
            return Array.from(document.querySelectorAll('pre, code')).map(element => {
                const language = element.className.match(/language-(\w+)/)?.[1] || 
                               element.getAttribute('data-language') ||
                               'plain';

                return {
                    code: element.textContent,
                    language: language,
                    isInline: element.tagName.toLowerCase() === 'code' && 
                             element.parentElement.tagName.toLowerCase() !== 'pre',
                    lineCount: element.textContent.split('\n').length
                };
            });
        }""")