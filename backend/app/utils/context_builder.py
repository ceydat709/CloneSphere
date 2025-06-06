import re
from typing import Dict, Any, List

def safe_string(item):
    """Safely convert any item to string"""
    if isinstance(item, dict):
        return item.get('text', item.get('name', item.get('label', str(item))))
    return str(item) if item is not None else ""

def safe_text_list(items):
    """Safely convert a list of mixed types to list of strings"""
    if not items:
        return []
    
    result = []
    for item in items:
        text = safe_string(item)
        if text and len(text.strip()) > 0 and len(text) < 300:
            result.append(text.strip())
    return result

def build_design_context(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "url": scraped_data.get("url", ""),
        "visual_summary": extract_visual_summary(scraped_data),
        "layout_structure": extract_layout_structure(scraped_data),
        "color_palette": extract_color_palette(scraped_data)[:15],
        "typography": extract_typography_summary(scraped_data),
        "key_elements": extract_key_elements(scraped_data),
        "responsive_info": extract_responsive_summary(scraped_data),
        "ui_patterns": extract_ui_patterns(scraped_data),
        "footer_analysis": extract_footer_analysis(scraped_data),
        "button_analysis": extract_button_analysis(scraped_data)
    }

def extract_visual_summary(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
    visual = scraped_data.get("visual", {})
    css_content = scraped_data.get("styles", {}).get("custom_css", "").lower()
    dom_content = str(scraped_data.get("dom", {})).lower()
    
    # Enhanced background detection
    bg_indicators = {
        "dark": ["#000", "#111", "#222", "#333", "black", "dark", "#1a1a1a", "#2d2d2d"],
        "light": ["#fff", "#f8f", "#fafafa", "white", "#ffffff", "#f5f5f5"]
    }
    
    dark_score = sum(1 for indicator in bg_indicators["dark"] if indicator in css_content + dom_content)
    light_score = sum(1 for indicator in bg_indicators["light"] if indicator in css_content + dom_content)
    
    # Enhanced background details
    background_details = extract_background_details(css_content, visual)
    
    return {
        "viewport_size": visual.get("viewport_size", {"width": 1920, "height": 1080}),
        "has_images": bool(visual.get("images")),
        "image_count": len(visual.get("images", [])),
        "primary_colors": visual.get("dominant_colors", [])[:8],
        "background_style": "dark" if dark_score > light_score else "light",
        "is_centered": any(x in css_content for x in ["center", "margin:auto", "mx-auto"]),
        "has_gradients": "gradient" in css_content,
        "has_animations": any(x in css_content for x in ["animation", "transition", "transform"]),
        "has_patterns": any(x in css_content for x in ["pattern", "texture", "repeat"]),
        "visual_style": determine_visual_style(css_content, dom_content),
        "background_details": background_details,
        "fonts_detected": visual.get("fonts_detected", [])
    }

def extract_background_details(css_content: str, visual: Dict[str, Any]) -> Dict[str, Any]:
    """Extract detailed background information"""
    return {
        "primary_bg": extract_primary_background_color(css_content),
        "has_background_image": "background-image" in css_content,
        "background_type": determine_background_type(css_content),
        "uses_transparency": "rgba" in css_content or "hsla" in css_content,
        "gradient_count": css_content.count("gradient")
    }

def extract_primary_background_color(css_content: str) -> str:
    """Extract the primary background color"""
    # Look for body background or common background patterns
    bg_patterns = [
        r'body\s*{[^}]*background(?:-color)?:\s*([^;]+)',
        r'\.bg-[^{]*{[^}]*background(?:-color)?:\s*([^;]+)',
        r'background(?:-color)?:\s*([^;]+)'
    ]
    
    for pattern in bg_patterns:
        matches = re.findall(pattern, css_content, re.IGNORECASE)
        if matches:
            color = matches[0].strip()
            if color and color != 'transparent':
                return color
    
    return "white"

def determine_background_type(css_content: str) -> str:
    """Determine the type of background used"""
    if "gradient" in css_content:
        return "gradient"
    elif "background-image" in css_content:
        return "image"
    elif any(x in css_content for x in ["pattern", "texture"]):
        return "pattern"
    else:
        return "solid"

def determine_visual_style(css_content: str, dom_content: str) -> str:
    """Determine the overall visual style"""
    modern_indicators = ["border-radius", "box-shadow", "transform", "transition", "flexbox", "grid"]
    minimal_indicators = ["clean", "minimal", "simple", "white"]
    corporate_indicators = ["professional", "business", "corporate"]
    
    modern_score = sum(1 for indicator in modern_indicators if indicator in css_content)
    minimal_score = sum(1 for indicator in minimal_indicators if indicator in dom_content)
    corporate_score = sum(1 for indicator in corporate_indicators if indicator in dom_content)
    
    if modern_score >= 3:
        return "modern"
    elif minimal_score >= 2:
        return "minimal"
    elif corporate_score >= 1:
        return "corporate"
    else:
        return "standard"

def extract_layout_structure(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
    html = scraped_data.get("dom", {}).get("html_outline", "").lower()
    text_content = str(scraped_data.get("text", {})).lower()
    
    counts = {
        "headers": html.count("<header") + html.count("<h1") + html.count("<h2"),
        "navs": html.count("<nav") + html.count("navigation"),
        "sections": html.count("<section") + html.count("<main") + html.count("<article"),
        "footers": html.count("<footer"),
        "forms": html.count("<form"),
        "buttons": html.count("<button") + text_content.count("button"),
        "asides": html.count("<aside") + html.count("sidebar"),
        "inputs": html.count("<input") + html.count("search"),
        "lists": html.count("<ul") + html.count("<ol") + html.count("<li"),
        "cards": html.count("card") + html.count("tile"),
        "containers": html.count("container") + html.count("wrapper")
    }
    
    # Detect layout patterns
    layout_patterns = []
    if counts["cards"] > 2:
        layout_patterns.append("card_grid")
    if counts["lists"] > 3:
        layout_patterns.append("list_heavy")
    if counts["sections"] > 4:
        layout_patterns.append("multi_section")
    if counts["asides"] > 0:
        layout_patterns.append("sidebar")
    
    return {
        "layout_type": determine_layout_type_generic(counts, html),
        "element_counts": counts,
        "page_title": scraped_data.get("dom", {}).get("title", ""),
        "has_sidebar": counts["asides"] > 0,
        "complexity": "complex" if sum(counts.values()) > 20 else "moderate" if sum(counts.values()) > 10 else "simple",
        "layout_patterns": layout_patterns,
        "has_search": counts["inputs"] > 0,
        "content_sections": max(counts["sections"], 1),
        "page_height": scraped_data.get("dom", {}).get("complexity", 0),
        "scroll_required": scraped_data.get("dom", {}).get("requires_scroll", False)
    }

def determine_layout_type_generic(counts: Dict[str, int], html: str) -> str:
    """Generic layout detection for any website"""
    if counts["headers"] and counts["navs"] and counts["footers"] and counts["sections"]:
        return "full_page_layout"
    elif counts["headers"] and counts["sections"] > 2:
        return "content_focused"
    elif counts["cards"] > 3:
        return "card_layout"
    elif counts["lists"] > counts["sections"]:
        return "list_layout"
    elif counts["forms"] > 0:
        return "form_layout"
    else:
        return "simple_layout"

def extract_color_palette(scraped_data: Dict[str, Any]) -> List[str]:
    css = scraped_data.get("styles", {}).get("custom_css", "")
    visual_colors = scraped_data.get("visual", {}).get("colors", [])
    
    # Extract all color formats
    hex_colors = re.findall(r'#[0-9a-fA-F]{3,8}', css)
    rgb_colors = re.findall(r'rgba?\([^)]+\)', css)
    hsl_colors = re.findall(r'hsla?\([^)]+\)', css)
    
    # Common web colors as fallback
    common_colors = ["#000000", "#ffffff", "#007bff", "#28a745", "#dc3545", "#ffc107"]
    
    all_colors = visual_colors + hex_colors + common_colors
    return list(dict.fromkeys(all_colors))[:15]

def extract_typography_summary(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
    css = scraped_data.get("styles", {}).get("custom_css", "")
    
    # Extract font families
    fonts = re.findall(r'font-family:\s*([^;]+)', css, re.IGNORECASE)
    sizes = re.findall(r'font-size:\s*([^;]+)', css, re.IGNORECASE)
    weights = re.findall(r'font-weight:\s*([^;]+)', css, re.IGNORECASE)
    
    # Clean up font names
    clean_fonts = []
    for font in fonts[:5]:
        clean_font = font.strip().replace('"', '').replace("'", '')
        clean_fonts.append(clean_font)
    
    return {
        "primary_fonts": clean_fonts or ["Arial, sans-serif"],
        "font_sizes": list(set(sizes))[:6],
        "font_weights": list(set(weights))[:4],
        "uses_web_fonts": any(x in css for x in ["googleapis.com", "@font-face", "typekit"]),
        "has_custom_fonts": "@font-face" in css
    }

def extract_key_elements(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
    text = scraped_data.get("text", {})
    
    # Extract comprehensive content SAFELY
    headings = safe_text_list(text.get("headings", []))
    nav_items = safe_text_list(text.get("navigation", []))
    buttons = safe_text_list(text.get("buttons", []))
    links = safe_text_list(text.get("links", []))
    paragraphs = safe_text_list(text.get("paragraphs", []))
    
    return {
        "headings": headings[:8],
        "nav_items": nav_items[:12],
        "button_labels": buttons[:10],
        "link_texts": [l for l in links if len(l) < 50][:10],
        "has_forms": bool(text.get("form_labels")),
        "primary_content": safe_string(text.get("main_content", ""))[:800],
        "footer_content": safe_string(text.get("footer", ""))[:400],
        "content_blocks": paragraphs[:5],
        "call_to_actions": [b for b in buttons if any(word in safe_string(b).lower() for word in ['get', 'start', 'try', 'buy', 'sign'])],
        "social_links": [l for l in links if any(social in safe_string(l).lower() for social in ['facebook', 'twitter', 'instagram', 'linkedin'])],
        "language_indicators": extract_language_elements(text)
    }

def extract_language_elements(text_data: Dict[str, Any]) -> List[str]:
    """Extract language-related elements"""
    all_text = str(text_data).lower()
    languages = []
    
    # Common language indicators
    lang_patterns = {
        "english": ["english", "en"],
        "spanish": ["español", "spanish", "es"],
        "french": ["français", "french", "fr"],
        "german": ["deutsch", "german", "de"],
        "italian": ["italiano", "italian", "it"],
        "portuguese": ["português", "portuguese", "pt"],
        "russian": ["русский", "russian", "ru"],
        "chinese": ["中文", "chinese", "zh"],
        "japanese": ["日本語", "japanese", "ja"],
        "korean": ["한국어", "korean", "ko"]
    }
    
    for lang, patterns in lang_patterns.items():
        if any(pattern in all_text for pattern in patterns):
            languages.append(lang)
    
    return languages

def extract_responsive_summary(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
    css = scraped_data.get("styles", {}).get("custom_css", "")
    
    return {
        "has_media_queries": "@media" in css,
        "uses_flexbox": "display:flex" in css or "display: flex" in css,
        "uses_grid": "display:grid" in css or "display: grid" in css,
        "framework": detect_css_framework_generic(scraped_data),
        "breakpoints": extract_breakpoints(css),
        "mobile_first": "min-width" in css
    }

def detect_css_framework_generic(scraped_data: Dict[str, Any]) -> str:
    """Detect CSS framework used"""
    content = (scraped_data.get("dom", {}).get("html_outline", "") + 
              scraped_data.get("styles", {}).get("custom_css", "")).lower()
    
    frameworks = {
        "bootstrap": ["bootstrap", "btn-", "col-", "container-fluid"],
        "tailwind": ["tailwind", "bg-", "text-", "p-", "m-", "w-", "h-"],
        "bulma": ["bulma", "is-", "has-"],
        "foundation": ["foundation", "grid-x"],
        "materialize": ["materialize", "material"],
        "semantic": ["semantic-ui", "ui "]
    }
    
    for framework, indicators in frameworks.items():
        if sum(1 for indicator in indicators if indicator in content) >= 2:
            return framework
    
    return "custom"

def extract_breakpoints(css: str) -> List[str]:
    """Extract responsive breakpoints"""
    breakpoints = re.findall(r'@media.*?\(.*?width:\s*([^)]+)\)', css)
    return list(set(breakpoints))[:5]

def extract_ui_patterns(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract common UI patterns"""
    html = scraped_data.get("dom", {}).get("html_outline", "").lower()
    css = scraped_data.get("styles", {}).get("custom_css", "").lower()
    
    patterns = {
        "has_hero_section": any(x in html for x in ["hero", "banner", "jumbotron"]),
        "has_carousel": any(x in html for x in ["carousel", "slider", "swiper"]),
        "has_modal": any(x in html for x in ["modal", "popup", "dialog"]),
        "has_dropdown": any(x in html for x in ["dropdown", "select"]),
        "has_tabs": any(x in html for x in ["tab", "tabs"]),
        "has_accordion": any(x in html for x in ["accordion", "collapse"]),
        "uses_icons": any(x in html for x in ["icon", "fa-", "material-icons"]),
        "has_sticky_elements": "position:sticky" in css or "position: sticky" in css,
        "has_parallax": "parallax" in css,
        "has_dark_mode": any(x in css for x in ["dark-mode", "theme-dark", "prefers-color-scheme"])
    }
    
    return patterns

def extract_footer_analysis(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze footer content and structure - SAFE VERSION"""
    html = scraped_data.get("dom", {}).get("html_outline", "").lower()
    text_data = scraped_data.get("text", {})
    css = scraped_data.get("styles", {}).get("custom_css", "").lower()
    
    # Check for footer presence
    has_footer = any(tag in html for tag in ["<footer", "footer", "site-footer"])
    
    # Extract footer-related content SAFELY
    footer_content = safe_string(text_data.get("footer", ""))
    footer_links = []
    
    # Look for common footer links in the navigation or links
    common_footer_terms = [
        "about", "contact", "privacy", "terms", "help", "support", 
        "careers", "blog", "sitemap", "legal", "cookie", "policy"
    ]
    
    all_links = safe_text_list(text_data.get("links", []))
    for link in all_links:
        if any(term in safe_string(link).lower() for term in common_footer_terms):
            footer_links.append(safe_string(link))
    
    # Extract copyright information
    copyright_text = ""
    all_text = safe_string(text_data).lower()
    copyright_patterns = [
        r'©[^.]*\d{4}[^.]*',
        r'copyright[^.]*\d{4}[^.]*',
        r'\d{4}[^.]*all rights reserved[^.]*'
    ]
    
    for pattern in copyright_patterns:
        matches = re.findall(pattern, all_text, re.IGNORECASE)
        if matches:
            copyright_text = matches[0]
            break
    
    # Determine footer background color
    footer_bg_patterns = [
        r'footer[^{]*{[^}]*background(?:-color)?:\s*([^;]+)',
        r'\.footer[^{]*{[^}]*background(?:-color)?:\s*([^;]+)',
        r'\.site-footer[^{]*{[^}]*background(?:-color)?:\s*([^;]+)'
    ]
    
    footer_bg = "#f8f9fa"  # Default
    for pattern in footer_bg_patterns:
        matches = re.findall(pattern, css, re.IGNORECASE)
        if matches:
            footer_bg = matches[0].strip()
            break
    
    # Count footer sections (typically columns)
    footer_sections = 1
    if "grid" in css and "footer" in css:
        grid_matches = re.findall(r'grid-template-columns:[^;]*', css)
        if grid_matches:
            footer_sections = len(grid_matches[0].split()) if grid_matches else 1
    elif "flex" in css and "footer" in css:
        footer_sections = 3  # Common flex footer layout
    
    return {
        "has_footer": has_footer,
        "footer_content": footer_content[:200],
        "links": footer_links[:10],
        "copyright": copyright_text or "© 2024 Company Name. All rights reserved.",
        "background_color": footer_bg,
        "sections": footer_sections,
        "has_social_links": any("social" in safe_string(link).lower() or social in safe_string(link).lower() 
                               for link in footer_links 
                               for social in ["facebook", "twitter", "instagram", "linkedin"]),
        "footer_style": determine_footer_style(css, html)
    }

def determine_footer_style(css: str, html: str) -> str:
    """Determine footer styling approach"""
    if "footer" in css:
        if "dark" in css or "#000" in css or "#333" in css:
            return "dark"
        elif "gradient" in css:
            return "gradient"
        else:
            return "light"
    return "minimal"

def extract_button_analysis(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze button styling and patterns - SAFE VERSION"""
    css = scraped_data.get("styles", {}).get("custom_css", "").lower()
    text_data = scraped_data.get("text", {})
    html = scraped_data.get("dom", {}).get("html_outline", "").lower()
    
    # Extract button labels SAFELY
    button_labels = safe_text_list(text_data.get("buttons", []))
    
    # Analyze button styling from CSS
    button_colors = []
    button_bg_patterns = [
        r'\.btn[^{]*{[^}]*background(?:-color)?:\s*([^;]+)',
        r'button[^{]*{[^}]*background(?:-color)?:\s*([^;]+)',
        r'\[type=.?button.?\][^{]*{[^}]*background(?:-color)?:\s*([^;]+)'
    ]
    
    for pattern in button_bg_patterns:
        matches = re.findall(pattern, css, re.IGNORECASE)
        button_colors.extend(matches)
    
    # Default button colors if none found
    if not button_colors:
        button_colors = ["#007bff", "#28a745", "#dc3545"]
    
    # Determine button style
    button_style = "solid"
    if "border:" in css and "background: transparent" in css:
        button_style = "outline"
    elif "border-radius" in css and "border:" in css:
        button_style = "rounded"
    elif "box-shadow" in css:
        button_style = "elevated"
    
    # Check for hover effects
    has_hover = any(selector in css for selector in [
        "button:hover", ".btn:hover", ":hover"
    ])
    
    # Count different button types
    button_types = {
        "primary": len([b for b in button_labels if any(word in safe_string(b).lower() for word in ["get", "start", "buy", "sign up"])]),
        "secondary": len([b for b in button_labels if any(word in safe_string(b).lower() for word in ["learn", "more", "about"])]),
        "action": len([b for b in button_labels if any(word in safe_string(b).lower() for word in ["submit", "send", "contact"])]),
        "navigation": len([b for b in button_labels if any(word in safe_string(b).lower() for word in ["next", "back", "previous"])])
    }
    
    return {
        "total_buttons": len(button_labels),
        "button_labels": button_labels[:8],
        "colors": button_colors[:5],
        "style": button_style,
        "has_hover": has_hover,
        "button_types": button_types,
        "uses_framework_buttons": any(framework in css for framework in ["btn-", ".button", ".ui-button"]),
        "has_icon_buttons": any(icon in html for icon in ["icon", "fa-", "material-icons"]),
        "primary_button_color": button_colors[0] if button_colors else "#007bff",
        "button_patterns": extract_button_patterns(css, button_labels)
    }

def extract_button_patterns(css: str, button_labels: List[str]) -> List[str]:
    """Extract common button patterns"""
    patterns = []
    
    if "gradient" in css:
        patterns.append("gradient_buttons")
    if "border-radius" in css:
        patterns.append("rounded_buttons")
    if "text-transform: uppercase" in css:
        patterns.append("uppercase_text")
    if "font-weight: bold" in css or "font-weight: 700" in css:
        patterns.append("bold_text")
    if any("cta" in safe_string(label).lower() or "call-to-action" in safe_string(label).lower() for label in button_labels):
        patterns.append("call_to_action")
    
    return patterns