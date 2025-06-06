from playwright.async_api import async_playwright
import base64
from urllib.parse import urljoin, urlparse
import re
from colorthief import ColorThief
from io import BytesIO
from typing import Dict, Any

# Universal improvements for intelligent_scraper.py with INTERACTIVE elements

async def extract_comprehensive_visual_context(page, url: str):
    """
    Universal visual context extraction for all website types
    """
    
    screenshot = await page.screenshot(type='png', full_page=True)
    
    # Universal Visual Analysis
    visual_analysis = await page.evaluate("""
        () => {
            const analysis = {
                hero_section: null,
                navigation: null,
                content_sections: [],      // Universal: Any organized content areas
                grid_layouts: [],          // Universal: Any grid-based layouts
                repeated_patterns: [],     // Universal: Repeated UI elements
                link_groups: [],          // Universal: Groups of related links
                content_blocks: [],       // Universal: Distinct content blocks
                interactive_elements: [], // Universal: Forms, buttons, inputs
                footer_content: null,
                floating_elements: [],
                image_regions: [],
                color_scheme: {
                    primary: null,
                    secondary: null,
                    accent: null,
                    background: null
                },
                typography: {
                    headings: [],
                    body_text_sample: '',
                    font_families: [],
                    custom_fonts: [],
                    font_weights: {},
                    font_sizes: {},
                    line_heights: {},
                    letter_spacing: {}
                },
                layout_style: 'unknown',
                content_density: 'unknown',
                site_structure: 'unknown'
            };
            
            // Universal hero section analysis
            const heroElements = Array.from(document.querySelectorAll('*')).filter(el => {
                const rect = el.getBoundingClientRect();
                return rect.top < 600 && rect.height > 100 && rect.width > 200;
            });
            
            if (heroElements.length > 0) {
                const heroTexts = heroElements.map(el => el.textContent?.trim()).filter(t => t && t.length > 10);
                analysis.hero_section = {
                    main_text: heroTexts[0] || '',
                    sub_text: heroTexts[1] || '',
                    has_cta: !!document.querySelector('button, .btn, [class*="button"], input[type="submit"]'),
                    has_search: !!document.querySelector('input[type="search"], input[name*="search"], [placeholder*="search" i]'),
                    has_form: !!document.querySelector('form'),
                    background_style: 'needs_analysis'
                };
            }

            const analyzeTypography = () => {
                const fontUsage = new Map();
                const customFonts = new Set();
                const fontWeights = new Map();
                const fontSizes = new Map();
                const lineHeights = new Map();
                const letterSpacing = new Map();
                const textStyles = new Map();

                // Check for Google Fonts, Adobe Fonts, or other web font services
                const linkElements = document.querySelectorAll('link');
                linkElements.forEach(link => {
                    const href = link.href || '';
                    if (href.includes('fonts.googleapis.com') || 
                        href.includes('fonts.adobe.com') || 
                        href.includes('use.typekit.net') ||
                        href.includes('fonts.bunny.net')) {
                        // Extract font names from Google Fonts URL
                        if (href.includes('fonts.googleapis.com')) {
                            const match = href.match(/family=([^&:]+)/);
                            if (match) {
                                const fonts = match[1].split('|').map(f => f.replace(/\\+/g, ' ').split(':')[0]);
                                fonts.forEach(font => customFonts.add(font));
                            }
                        }
                        analysis.typography.custom_fonts.push({
                            service: href.includes('googleapis') ? 'Google Fonts' : 
                                    href.includes('adobe') ? 'Adobe Fonts' : 
                                    href.includes('typekit') ? 'Adobe Fonts' : 'Other',
                            url: href
                        });
                    }
                });

                // Check @font-face declarations
                const styleSheets = Array.from(document.styleSheets);
                styleSheets.forEach(sheet => {
                    try {
                        const rules = Array.from(sheet.cssRules || sheet.rules || []);
                        rules.forEach(rule => {
                            if (rule instanceof CSSFontFaceRule) {
                                const fontFamily = rule.style.fontFamily?.replace(/['"]/g, '');
                                if (fontFamily) {
                                    customFonts.add(fontFamily);
                                }
                            }
                        });
                    } catch (e) {
                        // Cross-origin stylesheets might throw
                    }
                });

                const importantSelectors = [
                    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                    'p', 'a', 'button', '.btn', 'nav', 'body',
                    'span', 'div', 'li', 'td', 'th', 'label'
                ];

                importantSelectors.forEach(selector => {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(el => {
                        const style = window.getComputedStyle(el);
                            
                        // Font family
                        const fontFamily = style.fontFamily;
                        if (fontFamily) {
                            const count = fontUsage.get(fontFamily) || 0;
                            fontUsage.set(fontFamily, count + 1);
                        }
                            
                        // Font weight
                        const fontWeight = style.fontWeight;
                        if (fontWeight) {
                            const count = fontWeights.get(fontWeight) || 0;
                            fontWeights.set(fontWeight, count + 1);
                        }
                            
                        // Font size
                        const fontSize = style.fontSize;
                        if (fontSize) {
                            fontSizes.set(selector, fontSize);
                        }
                            
                         // Line height
                        const lineHeight = style.lineHeight;
                        if (lineHeight && lineHeight !== 'normal') {
                            lineHeights.set(selector, lineHeight);
                        }
                            
                            // Letter spacing
                        const letterSpacingValue = style.letterSpacing;
                        if (letterSpacingValue && letterSpacingValue !== 'normal') {
                            letterSpacing.set(selector, letterSpacingValue);
                        }
                            
                            // Text styles
                        const textTransform = style.textTransform;
                        const textDecoration = style.textDecoration;
                        if (textTransform !== 'none' || textDecoration !== 'none') {
                            textStyles.set(selector, {
                                transform: textTransform,
                                decoration: textDecoration
                            });
                        }
                    });
                });

                const sortedFonts = Array.from(fontUsage.entries())
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 10);
                
                const bodyStyle = window.getComputedStyle(document.body);
                const h1Style = document.querySelector('h1') ? 
                    window.getComputedStyle(document.querySelector('h1')) : null;
                const buttonStyle = document.querySelector('button, .btn, [role="button"]') ? 
                    window.getComputedStyle(document.querySelector('button, .btn, [role="button"]')) : null;
                    
                analysis.typography.font_stack = {
                    body: {
                        fontFamily: bodyStyle.fontFamily,
                        fontSize: bodyStyle.fontSize,
                        fontWeight: bodyStyle.fontWeight,
                        lineHeight: bodyStyle.lineHeight,
                        color: bodyStyle.color
                    },
                    headings: h1Style ? {
                        fontFamily: h1Style.fontFamily,
                        fontSize: h1Style.fontSize,
                        fontWeight: h1Style.fontWeight,
                        lineHeight: h1Style.lineHeight,
                        color: h1Style.color
                    } : null,
                    buttons: buttonStyle ? {
                        fontFamily: buttonStyle.fontFamily,
                        fontSize: buttonStyle.fontSize,
                        fontWeight: buttonStyle.fontWeight,
                        textTransform: buttonStyle.textTransform,
                        letterSpacing: buttonStyle.letterSpacing
                    } : null
                };

                analysis.typography.custom_fonts = Array.from(customFonts);
                analysis.typography.font_families = sortedFonts.map(([family, count]) => ({
                    family: family,
                    usage_count: count,
                    is_custom: Array.from(customFonts).some(cf => family.includes(cf))
                }));

                const sortedWeights = Array.from(fontWeights.entries())
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 5);
                analysis.typography.font_weights = Object.fromEntries(sortedWeights);

                analysis.typography.font_sizes = Object.fromEntries(
                    Array.from(fontSizes.entries()).slice(0, 15)
                );

                analysis.typography.line_heights = Object.fromEntries(
                    Array.from(lineHeights.entries()).slice(0, 10)
                );

                analysis.typography.letter_spacing = Object.fromEntries(
                    Array.from(letterSpacing.entries()).slice(0, 5)
                );

                analysis.typography.text_styles = Object.fromEntries(
                    Array.from(textStyles.entries()).slice(0, 10)
                );
             };              
            
            // Universal Grid Layout Detection
            const detectUniversalGrids = () => {
                const grids = [];
                
                // CSS Grid detection
                document.querySelectorAll('*').forEach(el => {
                    const style = window.getComputedStyle(el);
                    if (style.display === 'grid' || style.display === 'inline-grid') {
                        const children = Array.from(el.children);
                        if (children.length > 2) {
                            grids.push({
                                type: 'css_grid',
                                children_count: children.length,
                                columns: style.gridTemplateColumns,
                                items: children.slice(0, 6).map(child => ({
                                    text: child.textContent?.trim().slice(0, 50) || '',
                                    hasImage: !!child.querySelector('img, svg'),
                                    hasLink: !!child.querySelector('a'),
                                    className: child.className
                                }))
                            });
                        }
                    }
                });
                
                // Flexbox grid detection
                document.querySelectorAll('*').forEach(el => {
                    const style = window.getComputedStyle(el);
                    if (style.display === 'flex' && style.flexWrap === 'wrap') {
                        const children = Array.from(el.children);
                        if (children.length > 3) {
                            grids.push({
                                type: 'flex_grid',
                                children_count: children.length,
                                items: children.slice(0, 6).map(child => ({
                                    text: child.textContent?.trim().slice(0, 50) || '',
                                    hasImage: !!child.querySelector('img, svg'),
                                    hasLink: !!child.querySelector('a'),
                                    className: child.className
                                }))
                            });
                        }
                    }
                });
                
                // Card/tile pattern detection (common in modern sites)
                const cardPatterns = ['.card', '.tile', '.item', '.block', '.module', '[class*="card"]', '[class*="tile"]'];
                cardPatterns.forEach(pattern => {
                    const cards = document.querySelectorAll(pattern);
                    if (cards.length > 2) {
                        grids.push({
                            type: 'card_pattern',
                            pattern: pattern,
                            children_count: cards.length,
                            items: Array.from(cards).slice(0, 6).map(card => ({
                                text: card.textContent?.trim().slice(0, 50) || '',
                                hasImage: !!card.querySelector('img, svg'),
                                hasLink: !!card.querySelector('a'),
                                className: card.className
                            }))
                        });
                    }
                });
                
                return grids;
            };
            
            // Universal Content Section Detection
            const detectContentSections = () => {
                const sections = [];
                
                // Look for semantic sections
                document.querySelectorAll('section, article, .section, .content-section, [class*="section"]').forEach(section => {
                    const title = section.querySelector('h1, h2, h3, h4, h5, h6, .title, .heading')?.textContent?.trim();
                    const content = section.textContent?.trim();
                    
                    if (title && content && content.length > 50) {
                        sections.push({
                            title: title.slice(0, 50),
                            content_preview: content.slice(0, 200),
                            has_images: !!section.querySelector('img, svg'),
                            has_links: !!section.querySelector('a'),
                            has_buttons: !!section.querySelector('button, .btn'),
                            element_count: section.querySelectorAll('*').length
                        });
                    }
                });
                
                // Look for content blocks with specific patterns
                const contentSelectors = ['.content', '.main', '.body', '[class*="content"]', '[class*="block"]'];
                contentSelectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(block => {
                        const text = block.textContent?.trim();
                        if (text && text.length > 100) {
                            const heading = block.querySelector('h1, h2, h3, h4, h5, h6')?.textContent?.trim();
                            if (heading) {
                                sections.push({
                                    title: heading.slice(0, 50),
                                    content_preview: text.slice(0, 200),
                                    has_images: !!block.querySelector('img, svg'),
                                    has_links: !!block.querySelector('a'),
                                    selector: selector
                                });
                            }
                        }
                    });
                });
                
                return sections.slice(0, 8);
            };
            
            // Universal Link Group Detection
            const detectLinkGroups = () => {
                const linkGroups = [];
                
                // Navigation links
                const navs = document.querySelectorAll('nav, .nav, .navbar, .navigation, [role="navigation"]');
                navs.forEach(nav => {
                    const links = nav.querySelectorAll('a');
                    if (links.length > 1) {
                        linkGroups.push({
                            type: 'navigation',
                            count: links.length,
                            links: Array.from(links).slice(0, 8).map(link => ({
                                text: link.textContent?.trim(),
                                href: link.getAttribute('href')
                            }))
                        });
                    }
                });
                
                // Footer links
                const footers = document.querySelectorAll('footer, .footer, [role="contentinfo"]');
                footers.forEach(footer => {
                    const links = footer.querySelectorAll('a');
                    if (links.length > 3) {
                        linkGroups.push({
                            type: 'footer_links',
                            count: links.length,
                            links: Array.from(links).slice(0, 10).map(link => ({
                                text: link.textContent?.trim(),
                                href: link.getAttribute('href')
                            }))
                        });
                    }
                });
                
                // Grouped links (like language selectors, categories, etc.)
                const linkContainers = document.querySelectorAll('.links, .link-list, [class*="link"], ul, ol');
                linkContainers.forEach(container => {
                    const links = container.querySelectorAll('a');
                    if (links.length > 4 && links.length < 30) { // Reasonable range
                        linkGroups.push({
                            type: 'link_group',
                            count: links.length,
                            container: container.tagName,
                            links: Array.from(links).slice(0, 10).map(link => ({
                                text: link.textContent?.trim(),
                                href: link.getAttribute('href')
                            }))
                        });
                    }
                });
                
                return linkGroups;
            };
            
            // Universal Interactive Elements Detection
            const detectInteractiveElements = () => {
                const interactive = [];
                
                // Forms
                document.querySelectorAll('form').forEach(form => {
                    const inputs = form.querySelectorAll('input, textarea, select');
                    const buttons = form.querySelectorAll('button, input[type="submit"]');
                    
                    interactive.push({
                        type: 'form',
                        input_count: inputs.length,
                        button_count: buttons.length,
                        action: form.getAttribute('action') || '',
                        inputs: Array.from(inputs).slice(0, 5).map(input => ({
                            type: input.type || input.tagName.toLowerCase(),
                            placeholder: input.getAttribute('placeholder') || '',
                            name: input.getAttribute('name') || ''
                        }))
                    });
                });
                
                // Standalone buttons
                const buttons = document.querySelectorAll('button:not(form button), .btn, [role="button"]');
                if (buttons.length > 0) {
                    interactive.push({
                        type: 'buttons',
                        count: buttons.length,
                        buttons: Array.from(buttons).slice(0, 8).map(btn => ({
                            text: btn.textContent?.trim(),
                            className: btn.className
                        }))
                    });
                }
                
                return interactive;
            };
            
            // Universal Site Structure Analysis
            const analyzeSiteStructure = () => {
                const hasHeader = !!document.querySelector('header, .header, [role="banner"]');
                const hasNav = !!document.querySelector('nav, .nav, [role="navigation"]');
                const hasMain = !!document.querySelector('main, .main, [role="main"]');
                const hasAside = !!document.querySelector('aside, .sidebar, [role="complementary"]');
                const hasFooter = !!document.querySelector('footer, .footer, [role="contentinfo"]');
                
                if (hasHeader && hasNav && hasMain && hasFooter) {
                    return 'full_semantic';
                } else if (hasMain && (hasHeader || hasNav)) {
                    return 'content_focused';
                } else if (hasAside) {
                    return 'sidebar_layout';
                } else {
                    return 'simple';
                }
            };
            
            // Execute all analysis
            analyzeTypography();
            analysis.grid_layouts = detectUniversalGrids();
            analysis.content_sections = detectContentSections();
            analysis.link_groups = detectLinkGroups();
            analysis.interactive_elements = detectInteractiveElements();
            analysis.site_structure = analyzeSiteStructure();
            
            // Content density analysis
            const totalElements = document.querySelectorAll('*').length;
            const textElements = document.querySelectorAll('p, span, div, a, li').length;
            const linkElements = document.querySelectorAll('a').length;
            
            const density = textElements / Math.max(totalElements, 1);
            
            if (density > 0.3 && linkElements > 20) {
                analysis.content_density = 'high';
            } else if (density > 0.2) {
                analysis.content_density = 'medium';
            } else {
                analysis.content_density = 'low';
            }
            
            // Layout style detection
            const hasGrids = analysis.grid_layouts.length > 0;
            const hasFlex = Array.from(document.querySelectorAll('*')).some(el => 
                window.getComputedStyle(el).display === 'flex'
            );
            const hasFloating = Array.from(document.querySelectorAll('*')).some(el => 
                ['absolute', 'fixed'].includes(window.getComputedStyle(el).position)
            );
            
            if (hasFloating && analysis.image_regions.length > 3) {
                analysis.layout_style = 'creative_floating';
            } else if (hasGrids) {
                analysis.layout_style = 'grid_based';
            } else if (hasFlex) {
                analysis.layout_style = 'flexbox_based';
            } else {
                analysis.layout_style = 'traditional';
            }
            
            // Enhanced image analysis
            document.querySelectorAll('img, svg').forEach((img, index) => {
                const rect = img.getBoundingClientRect();
                const parentText = img.parentElement?.textContent?.trim() || '';
                const alt = img.getAttribute('alt') || '';
                const src = img.getAttribute('src') || '';
                
                const isLogo = alt.toLowerCase().includes('logo') || 
                             src.toLowerCase().includes('logo') ||
                             (rect.width < 200 && rect.height < 200 && rect.top < 400);
                
                analysis.image_regions.push({
                    index: index,
                    src: src,
                    alt: alt,
                    width: rect.width,
                    height: rect.height,
                    position: {
                        top: rect.top,
                        left: rect.left
                    },
                    context: parentText.slice(0, 100),
                    is_hero_image: rect.top < 600 && rect.width > 200,
                    is_logo: isLogo,
                    is_floating: window.getComputedStyle(img).position === 'absolute'
                });
            });
            
            // Color and typography analysis
            const computedStyle = window.getComputedStyle(document.body);
            analysis.color_scheme.background = computedStyle.backgroundColor;
            
            const prominentElements = document.querySelectorAll('h1, h2, button, .btn, nav, header, a');
            prominentElements.forEach(el => {
                const style = window.getComputedStyle(el);
                if (style.color && !analysis.color_scheme.primary) {
                    analysis.color_scheme.primary = style.color;
                }
                if (style.backgroundColor && style.backgroundColor !== 'rgba(0, 0, 0, 0)') {
                    if (!analysis.color_scheme.secondary) {
                        analysis.color_scheme.secondary = style.backgroundColor;
                    }
                }
            });
            
            document.querySelectorAll('h1, h2, h3').forEach(heading => {
                const style = window.getComputedStyle(heading);
                analysis.typography.headings.push({
                    text: heading.textContent?.trim() || '',
                    fontSize: style.fontSize,
                    fontWeight: style.fontWeight,
                    fontFamily: style.fontFamily
                });
            });
            
            const bodyText = document.querySelector('p')?.textContent?.trim() || '';
            analysis.typography.body_text_sample = bodyText.slice(0, 200);
            
            return analysis;
        }
    """)
    
    # Enhanced image descriptions
    image_descriptions = []
    for img_data in visual_analysis.get('image_regions', []):
        context = img_data.get('context', '').lower()
        alt_text = img_data.get('alt', '').lower()
        is_logo = img_data.get('is_logo', False)
        
        # Universal image type detection
        if is_logo or 'logo' in alt_text:
            img_type = "brand_logo"
        elif any(word in context for word in ['product', 'item', 'buy', 'shop']):
            img_type = "product_image"
        elif any(word in context for word in ['team', 'people', 'about', 'staff']):
            img_type = "people_photo"
        elif any(word in alt_text for word in ['icon', 'symbol']):
            img_type = "icon_image"
        elif img_data.get('is_hero_image'):
            img_type = "hero_visual"
        else:
            img_type = "content_image"
            
        image_descriptions.append({
            **img_data,
            'suggested_type': img_type,
            'placeholder_suggestion': f"https://picsum.photos/{int(img_data['width'])}/{int(img_data['height'])}"
        })
    
    return {
        **visual_analysis,
        'image_descriptions': image_descriptions,
        'site_category': classify_site_category_universal(visual_analysis, url),
        'screenshot_base64': base64.b64encode(screenshot).decode()
    }

def classify_site_category_universal(visual_analysis, url: str) -> str:
    """Universal site classification based on content patterns"""
    
    hero_text = visual_analysis.get('hero_section', {}).get('main_text', '').lower()
    grid_layouts = visual_analysis.get('grid_layouts', [])
    link_groups = visual_analysis.get('link_groups', [])
    content_sections = visual_analysis.get('content_sections', [])
    interactive_elements = visual_analysis.get('interactive_elements', [])
    content_density = visual_analysis.get('content_density', 'low')
    
    # High-density content sites (like Wikipedia, documentation)
    if (content_density == 'high' and 
        len(link_groups) > 2 and 
        len(content_sections) > 3):
        return 'content_portal'
    
    # E-commerce/product sites
    elif any(word in hero_text for word in ['shop', 'buy', 'store', 'product', 'cart']):
        return 'ecommerce'
    
    # Tech/SaaS platforms
    elif any(word in hero_text for word in ['platform', 'deploy', 'build', 'api', 'developer']):
        return 'tech_platform'
    
    # Fashion/lifestyle brands
    elif any(word in hero_text for word in ['fashion', 'style', 'clothing', 'design']):
        return 'fashion_brand'
    
    # Portfolio/creative sites
    elif (visual_analysis.get('layout_style') == 'creative_floating' and 
          len(visual_analysis.get('image_regions', [])) > 5):
        return 'creative_showcase'
    
    # Blog/content sites
    elif any(word in hero_text for word in ['blog', 'article', 'news', 'post']):
        return 'content_site'
    
    # Business/corporate sites
    elif len(content_sections) > 2 and len(interactive_elements) > 0:
        return 'business_site'
    
    # Landing pages
    elif (len(interactive_elements) > 0 and 
          any(elem.get('type') == 'form' for elem in interactive_elements)):
        return 'landing_page'
    
    else:
        return 'general_site'


def classify_site_category(visual_analysis, url: str) -> str:
    """Classify the type of website for better prompting"""
    
    hero_text = visual_analysis.get('hero_section', {}).get('main_text', '').lower()
    image_count = len(visual_analysis.get('image_regions', []))
    layout_style = visual_analysis.get('layout_style', '')
    
    # Check URL patterns
    if any(domain in url for domain in ['vercel.com', 'netlify.com', 'github.com']):
        return 'developer_platform'
    elif any(word in hero_text for word in ['fashion', 'clothing', 'style', 'wear']):
        return 'fashion_brand'
    elif any(word in hero_text for word in ['platform', 'deploy', 'build', 'developer']):
        return 'tech_platform'
    elif layout_style == 'creative_floating' and image_count > 5:
        return 'creative_showcase'
    elif any(word in hero_text for word in ['blog', 'article', 'news']):
        return 'content_site'
    else:
        return 'business_site'

def fix_relative_urls(base_url: str, href: str) -> str:
    """
    Fix relative URLs to absolute URLs, preserving functionality
    """
    if not href:
        return href
    
    # Already absolute URL
    if href.startswith(('http://', 'https://', '//')):
        return href
    
    # Fragment/anchor links - keep as-is for page navigation
    if href.startswith('#'):
        return href
    
    # Email links
    if href.startswith('mailto:'):
        return href
    
    # Phone links
    if href.startswith('tel:'):
        return href
    
    # JavaScript links - keep as-is
    if href.startswith('javascript:'):
        return href
    
    # Relative URLs - convert to absolute
    try:
        return urljoin(base_url, href)
    except Exception:
        return href

async def intelligent_clone(url: str, mode: str = "classic", keep_interactive: bool = True):
    """
    Hybrid scraper that provides:
    - Classic mode: Simple, reliable HTML preservation
    - LLM modes: Enhanced context extraction for AI processing
    - NEW: keep_interactive flag to maintain button/link functionality
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        try:
            print(f"🌐 Loading: {url} (mode: {mode}, interactive: {keep_interactive})")
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Enhanced loading for LLM modes
            if mode in ["llm", "iterative"]:
                print("🔤 Enhanced loading for LLM mode...")
                await page.evaluate("""
                    () => {
                        return document.fonts.ready;
                    }
                """)
                await page.wait_for_timeout(2000)
                
                # Scroll to load lazy content for LLM analysis
                await page.evaluate("""
                    () => {
                        return new Promise((resolve) => {
                            let totalHeight = 0;
                            let distance = 300;
                            let scrollCount = 0;
                            const maxScrolls = 10; // Reduced for performance
                            
                            const scrollTimer = setInterval(() => {
                                const scrollHeight = document.body.scrollHeight;
                                window.scrollBy(0, distance);
                                totalHeight += distance;
                                scrollCount++;
                                
                                if (totalHeight >= scrollHeight || scrollCount >= maxScrolls) {
                                    clearInterval(scrollTimer);
                                    window.scrollTo(0, 0);
                                    setTimeout(resolve, 1000);
                                }
                            }, 200);
                        });
                    }
                """)
            
            print("💫 Inlining external stylesheets...")
            # Enhanced CSS inlining with error handling
            await page.add_script_tag(content="""
                (async () => {
                  const links = [...document.querySelectorAll('link[rel="stylesheet"]')];
                  console.log(`Found ${links.length} stylesheets to inline`);
                  
                  for (const link of links) {
                    try {
                      const href = link.href;
                      if (href && !href.includes('data:')) {
                        const res = await fetch(href);
                        if (res.ok) {
                          const css = await res.text();
                          const style = document.createElement('style');
                          style.textContent = css;
                          style.setAttribute('data-inlined-from', href);
                          link.replaceWith(style);
                        }
                      }
                    } catch (e) {
                      console.log(`Failed to inline: ${link.href}`);
                    }
                  }
                })();
            """)
            
            await page.wait_for_timeout(2000)
            
            print("🔗 Fixing relative URLs...")
            # Enhanced relative path fixing - KEEPING FUNCTIONALITY
            base_url_parsed = urlparse(url)
            base_domain = f"{base_url_parsed.scheme}://{base_url_parsed.netloc}"
            
            await page.evaluate(f"""
                () => {{
                    const baseUrl = '{url}';
                    const baseDomain = '{base_domain}';
                    
                    // Fix relative URLs while preserving functionality
                    const fixUrls = (attr, shouldPreserve = false) => {{
                        const elements = document.querySelectorAll(`[${{attr}}]`);
                        elements.forEach(el => {{
                            const val = el.getAttribute(attr);
                            if (val) {{
                                // Skip fragments, mailto, tel, javascript
                                if (val.startsWith('#') || val.startsWith('mailto:') || 
                                    val.startsWith('tel:') || val.startsWith('javascript:')) {{
                                    return;
                                }}
                                
                                // Fix relative URLs to absolute
                                if (val.startsWith('/') && !val.startsWith('//')) {{
                                    const newUrl = baseDomain + val;
                                    el.setAttribute(attr, newUrl);
                                    
                                    // For links, add target="_blank" to external links
                                    if (attr === 'href' && el.tagName === 'A') {{
                                        el.setAttribute('target', '_blank');
                                        el.setAttribute('rel', 'noopener noreferrer');
                                    }}
                                }} else if (!val.startsWith('http') && !val.startsWith('//')) {{
                                    // Handle relative paths
                                    try {{
                                        const newUrl = new URL(val, baseUrl).href;
                                        el.setAttribute(attr, newUrl);
                                        
                                        if (attr === 'href' && el.tagName === 'A') {{
                                            el.setAttribute('target', '_blank');
                                            el.setAttribute('rel', 'noopener noreferrer');
                                        }}
                                    }} catch (e) {{
                                        // Keep original if URL parsing fails
                                    }}
                                }}
                            }}
                        }});
                    }};
                    
                    // Fix all URL attributes
                    fixUrls('src');
                    fixUrls('href', true); // Preserve link functionality
                    fixUrls('action');
                    
                    // Fix CSS url() references
                    const styles = document.querySelectorAll('style');
                    styles.forEach(style => {{
                        if (style.textContent) {{
                            style.textContent = style.textContent.replace(
                                /url\\(['"]?\\/([^'")\\s]+)['"]?\\)/g,
                                `url('${{baseDomain}}/$1')`
                            );
                        }}
                    }});
                }}
            """)
            
            # CONDITIONAL interactive element handling
            if keep_interactive:
                print("✅ Keeping interactive elements functional...")
                # Only add safety measures, don't disable functionality
                await page.evaluate("""
                    () => {
                        // Add safety attributes to forms without disabling them
                        document.querySelectorAll('form').forEach(form => {
                            // Add novalidate to prevent browser validation issues
                            form.setAttribute('novalidate', '');
                            
                            // If form has no action, prevent submission
                            if (!form.getAttribute('action')) {
                                form.addEventListener('submit', (e) => {
                                    e.preventDefault();
                                    console.log('Form submission prevented - no action specified');
                                    return false;
                                });
                            }
                        });
                        
                        // Add click tracking for buttons (optional)
                        document.querySelectorAll('button, input[type="button"], input[type="submit"]').forEach(btn => {
                            btn.addEventListener('click', (e) => {
                                console.log('Button clicked:', btn.textContent || btn.value);
                                // Don't prevent default - let button work normally
                            });
                        });
                        
                        // Add click tracking for links
                        document.querySelectorAll('a').forEach(link => {
                            link.addEventListener('click', (e) => {
                                console.log('Link clicked:', link.href);
                                // Don't prevent default - let link work normally
                            });
                        });
                    }
                """)
            else:
                print("🔒 Disabling interactive elements...")
                await page.evaluate("""
                    () => {
                        // Disable all links
                        document.querySelectorAll('a').forEach(link => {
                            const href = link.getAttribute('href');
                            if (href && !href.startsWith('#')) {
                                link.setAttribute('data-original-href', href);
                                link.setAttribute('href', '#');
                            }
                            link.addEventListener('click', (e) => {
                                e.preventDefault();
                                return false;
                            });
                        });
                        
                        // Disable all forms
                        document.querySelectorAll('form').forEach(form => {
                            form.addEventListener('submit', (e) => {
                                e.preventDefault();
                                return false;
                            });
                            form.setAttribute('onsubmit', 'return false;');
                        });
                        
                        // Disable all buttons
                        document.querySelectorAll('button, input[type="button"], input[type="submit"]').forEach(btn => {
                            btn.addEventListener('click', (e) => {
                                e.preventDefault();
                                return false;
                            });
                            btn.setAttribute('onclick', 'return false;');
                        });
                    }
                """)
            
            await page.wait_for_timeout(1000)
            
            # Get final processed HTML
            html = await page.content()
            
            print("📸 Taking screenshot...")
            screenshot = await page.screenshot(
                type='png', 
                full_page=True,
                animations='disabled'
            )
            
            # Extract layout info
            title = await page.title()
            layout_info = await page.evaluate("""
                () => {
                    return {
                        has_nav: document.querySelector('nav') !== null,
                        has_header: document.querySelector('header') !== null,
                        has_main: document.querySelector('main') !== null,
                        has_footer: document.querySelector('footer') !== null,
                        has_sidebar: document.querySelector('aside, .sidebar') !== null,
                        has_forms: document.querySelector('form') !== null,
                        has_search: document.querySelector('input[type="search"], [placeholder*="search" i]') !== null,
                        element_count: document.querySelectorAll('*').length,
                        image_count: document.querySelectorAll('img').length,
                        link_count: document.querySelectorAll('a').length,
                        button_count: document.querySelectorAll('button, input[type="button"], input[type="submit"]').length,
                        interactive_preserved: true // Flag to indicate interactivity status
                    };
                }
            """)
            
            # Enhanced content extraction for LLM modes
            enhanced_data = {}
            if mode in ["llm", "iterative"]:
                print("📊 Enhanced visual analysis for LLM...")
                
                # NEW: Comprehensive visual context extraction
                visual_context = await extract_comprehensive_visual_context(page, url)
                
                # Extract text content with interactive element details
                content_data = await page.evaluate("""
                    () => {
                        const extractText = (selector, limit = 50) => {
                            try {
                                return Array.from(document.querySelectorAll(selector))
                                    .slice(0, limit)
                                    .map(el => el.textContent?.trim())
                                    .filter(text => text && text.length > 0 && text.length < 200);
                            } catch (e) {
                                return [];
                            }
                        };
                        
                        const extractInteractiveElements = () => {
                            const interactive = {
                                buttons: [],
                                links: [],
                                forms: []
                            };
                            
                            // Extract button details with their actions
                            const buttonSelectors = ['button', '[role="button"]', 'input[type="button"]', 'input[type="submit"]', '.btn'];
                            buttonSelectors.forEach(selector => {
                                document.querySelectorAll(selector).forEach(el => {
                                    const text = el.textContent?.trim() || el.value?.trim() || el.alt?.trim();
                                    const onclick = el.getAttribute('onclick') || '';
                                    const type = el.type || 'button';
                                    const className = el.className || '';
                                    
                                    if (text && text.length < 100) {
                                        interactive.buttons.push({
                                            text,
                                            type,
                                            onclick,
                                            className,
                                            hasForm: !!el.closest('form')
                                        });
                                    }
                                });
                            });
                            
                            // Extract link details with their destinations
                            document.querySelectorAll('a[href]').forEach(link => {
                                const text = link.textContent?.trim();
                                const href = link.getAttribute('href');
                                const target = link.getAttribute('target') || '';
                                const className = link.className || '';
                                
                                if (text && text.length < 100 && href) {
                                    interactive.links.push({
                                        text,
                                        href,
                                        target,
                                        className,
                                        isExternal: href.startsWith('http') && !href.includes(window.location.hostname),
                                        isAnchor: href.startsWith('#')
                                    });
                                }
                            });
                            
                            // Extract form details
                            document.querySelectorAll('form').forEach(form => {
                                const action = form.getAttribute('action') || '';
                                const method = form.getAttribute('method') || 'GET';
                                const inputs = Array.from(form.querySelectorAll('input, textarea, select')).map(input => ({
                                    type: input.type || input.tagName.toLowerCase(),
                                    name: input.name || '',
                                    placeholder: input.placeholder || '',
                                    required: input.required || false
                                }));
                                
                                interactive.forms.push({
                                    action,
                                    method,
                                    inputs,
                                    hasSubmitButton: !!form.querySelector('button[type="submit"], input[type="submit"]')
                                });
                            });
                            
                            return interactive;
                        };
                        
                        return {
                            headings: extractText('h1, h2, h3, h4, h5, h6', 20),
                            paragraphs: extractText('p', 30),
                            interactive_elements: extractInteractiveElements(),
                            navigation: extractText('nav a, .nav a, .navbar a', 30),
                            footer: document.querySelector('footer, .footer')?.textContent?.trim()?.slice(0, 500) || '',
                            main_content: document.querySelector('main, .main, #main')?.textContent?.slice(0, 2000) || '',
                            meta_description: document.querySelector('meta[name="description"]')?.getAttribute('content') || '',
                            title: document.title || ''
                        };
                    }
                """)
                
                # Extract color palette
                try:
                    color_thief = ColorThief(BytesIO(screenshot))
                    palette = color_thief.get_palette(color_count=8, quality=1)
                    hex_colors = [f'#{r:02x}{g:02x}{b:02x}' for r, g, b in palette]
                except Exception as e:
                    print(f"⚠️ Color extraction failed: {e}")
                    hex_colors = ['#000000', '#ffffff', '#007bff', '#28a745', '#dc3545', '#ffc107']
                
                # Extract styles info
                styles_info = await page.evaluate("""
                    () => {
                        const styles = Array.from(document.querySelectorAll('style')).map(s => s.textContent).join(' ');
                        return {
                            custom_css: styles.slice(0, 10000), // Limit size
                            has_animations: styles.includes('animation') || styles.includes('transition'),
                            has_gradients: styles.includes('gradient'),
                            framework_detected: styles.includes('bootstrap') ? 'bootstrap' : 
                                              styles.includes('tailwind') ? 'tailwind' : 'custom'
                        };
                    }
                """)
                
                enhanced_data = {
                    "text": content_data,
                    "visual": {
                        "colors": hex_colors,
                        "screenshot_base64": base64.b64encode(screenshot).decode(),
                        "viewport_size": {"width": 1920, "height": 1080}
                    },
                    "styles": styles_info,
                    "visual_context": visual_context,  # NEW: Enhanced visual context
                    "dom": {
                        "html_outline": html[:10000],  # First 10k chars
                        "title": title,
                        "complexity": layout_info.get('element_count', 0),
                        "requires_scroll": len(html) > 50000
                    },
                    "interactivity": {
                        "preserved": keep_interactive,
                        "button_count": len(content_data.get('interactive_elements', {}).get('buttons', [])),
                        "link_count": len(content_data.get('interactive_elements', {}).get('links', [])),
                        "form_count": len(content_data.get('interactive_elements', {}).get('forms', []))
                    }
                }
            
            print(f"✅ {mode.capitalize()} scraping completed successfully!")
            print(f"🔗 Interactive elements: {'PRESERVED' if keep_interactive else 'DISABLED'}")
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            raise e
        finally:
            await browser.close()

        # Build response based on mode
        base_response = {
            "success": True,
            "title": title,
            "html": html,
            "screenshot_base64": base64.b64encode(screenshot).decode(),
            "layout": layout_info,
            "metadata": {
                "url": url,
                "mode": mode,
                "interactive_preserved": keep_interactive,
                "extraction_timestamp": "2024-current",
                "content_loaded": True,
                "links_fixed": True,
                "css_inlined": True,
                "elements_status": "preserved" if keep_interactive else "disabled"
            }
        }
        
        # Add enhanced data for LLM modes
        if mode in ["llm", "iterative"]:
            base_response.update(enhanced_data)
        
        return base_response

# Usage examples:
"""
# For interactive clone (buttons/links work):
result = await intelligent_clone("https://example.com", mode="llm", keep_interactive=True)

# For static clone (original behavior):
result = await intelligent_clone("https://example.com", mode="llm", keep_interactive=False)

# Classic mode with interactivity:
result = await intelligent_clone("https://example.com", mode="classic", keep_interactive=True)
"""