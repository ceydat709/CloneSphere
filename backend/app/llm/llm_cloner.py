import json
import os
import re
from typing import Dict, Any, List, Optional, Tuple
from anthropic import Anthropic
from app.utils.context_builder import build_design_context
from app.utils.render_and_capture import render_generated_html
from app.utils.image_compare import compare_base64_images
import traceback

class WebsiteCloner:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.max_iterations = 3
        self.quality_threshold = 0.85
        self.last_scraped_data = None  # Store for refinement analysis

    def filter_meaningful_images(self, image_descriptions: List[Dict]) -> Dict[str, List[Dict]]:
        """Filter images into smart categories based on importance and size"""
        
        meaningful_images = []
        logos = []
        tiny_icons = []
        
        for img in image_descriptions:
            width = img.get('width', 0)
            height = img.get('height', 0)
            src = img.get('src', '')  # Get the ACTUAL URL
            alt = img.get('alt', '').lower()
            context = img.get('context', '').lower()
            
            # Calculate area for importance
            area = width * height
            
            # Use actual URL if available, otherwise use placeholder
            actual_url = src if src and not src.startswith('data:') else f"https://picsum.photos/{int(width) if width > 0 else 400}/{int(height) if height > 0 else 300}"
            
            img_data = {
                **img,
                'actual_url': actual_url,  # This is what we'll use!
                'area': area
            }
            
            # Categorize based on smart criteria
            if width <= 32 and height <= 32:
                img_data['suggested_type'] = 'icon'
                tiny_icons.append(img_data)
            elif 'logo' in alt or 'logo' in src.lower() or (width < 200 and height < 100 and img.get('position', {}).get('top', 999) < 200):
                img_data['suggested_type'] = 'logo'
                logos.append(img_data)
            elif width >= 100 or height >= 100:
                # Meaningful content images
                img_data['suggested_type'] = 'content'
                meaningful_images.append(img_data)
            else:
                if any(indicator in context for indicator in ['product', 'feature', 'hero', 'banner', 'main']):
                    img_data['suggested_type'] = 'content'
                    meaningful_images.append(img_data)
                else:
                    img_data['suggested_type'] = 'icon'
                    tiny_icons.append(img_data)
        
        # Sort by importance (area) within each category
        meaningful_images.sort(key=lambda x: x['area'], reverse=True)
        logos.sort(key=lambda x: x['area'], reverse=True)
        
        return {
            'meaningful_images': meaningful_images,
            'logos': logos,
            'tiny_icons': tiny_icons
        }

    def create_comprehensive_prompt(self, scraped_data: Dict) -> str:
        """Create prompt with SMART image categorization"""
        
        visual_context = scraped_data.get('visual_context', {})
        text_data = scraped_data.get('text', {})
        
        # Get the rich data your scraper provides
        content_sections = visual_context.get('content_sections', [])
        grid_layouts = visual_context.get('grid_layouts', [])
        image_descriptions = visual_context.get('image_descriptions', [])
        interactive_elements = visual_context.get('interactive_elements', [])
        typography = visual_context.get('typography', {})
        
        # SMART: Filter images by importance
        image_categories = self.filter_meaningful_images(image_descriptions)
        meaningful_images = image_categories['meaningful_images']
        logos = image_categories['logos']
        tiny_icons = image_categories['tiny_icons']
        
        # Build content list
        content_list = f"""
NAVIGATION ITEMS:
{chr(10).join(f'• {item}' for item in text_data.get('navigation', [])[:10])}

HEADINGS:
{chr(10).join(f'• {heading}' for heading in text_data.get('headings', [])[:8])}

BUTTONS:
{chr(10).join(f'• {button}' for button in text_data.get('buttons', [])[:10])}

PARAGRAPHS:
{chr(10).join(f'• {p[:80]}...' for p in text_data.get('paragraphs', [])[:6])}
"""
        font_stack = typography.get('font_stack', {})
        custom_fonts = typography.get('custom_fonts', [])
        font_families = typography.get('font_families', [])
        
        typography_instructions = f"""
TYPOGRAPHY SPECIFICATIONS:

CUSTOM FONTS DETECTED ({len(custom_fonts)} web fonts):
{chr(10).join(f'• {font}' for font in custom_fonts[:5])}

FONT STACK USAGE:
Body Text:
├─ Font: {font_stack.get('body', {}).get('fontFamily', 'system-ui, -apple-system, sans-serif')}
├─ Size: {font_stack.get('body', {}).get('fontSize', '16px')}
├─ Weight: {font_stack.get('body', {}).get('fontWeight', '400')}
├─ Line Height: {font_stack.get('body', {}).get('lineHeight', '1.5')}
└─ Color: {font_stack.get('body', {}).get('color', '#000000')}

Headings:
├─ Font: {font_stack.get('headings', {}).get('fontFamily', 'inherit')}
├─ Size: {font_stack.get('headings', {}).get('fontSize', '32px')}
├─ Weight: {font_stack.get('headings', {}).get('fontWeight', '700')}
└─ Color: {font_stack.get('headings', {}).get('color', '#000000')}

Buttons:
├─ Font: {font_stack.get('buttons', {}).get('fontFamily', 'inherit')}
├─ Size: {font_stack.get('buttons', {}).get('fontSize', '16px')}
├─ Weight: {font_stack.get('buttons', {}).get('fontWeight', '500')}
├─ Transform: {font_stack.get('buttons', {}).get('textTransform', 'none')}
└─ Letter Spacing: {font_stack.get('buttons', {}).get('letterSpacing', 'normal')}

FONT USAGE PRIORITY:
{chr(10).join(f'{i+1}. {ff["family"]} (used {ff["usage_count"]} times{"*" if ff.get("is_custom") else ""})' 
              for i, ff in enumerate(font_families[:5]))}

IMPLEMENTATION RULES:
1. Use the EXACT font families specified above in the correct order
2. Include fallback fonts for each font stack
3. If custom fonts are detected, use appropriate web font service
4. Maintain font weights: {', '.join(str(k) for k in typography.get('font_weights', {}).keys())}
5. Keep the original text hierarchy with proper font sizes
"""

        # SMART image handling with ACTUAL URLs
        image_instructions = f"""
SMART IMAGE IMPLEMENTATION STRATEGY:

PRIORITY 1 - LOGOS ({len(logos)} found):
{chr(10).join(f'''Logo {i+1}: {img.get("alt", "Logo")}
├─ Size: {img.get("width")}×{img.get("height")}px
├─ URL: {img.get("actual_url")}
└─ Place in: Header/Navigation area
''' for i, img in enumerate(logos[:3]))}

PRIORITY 2 - MEANINGFUL CONTENT IMAGES ({len(meaningful_images)} found):
{chr(10).join(f'''Content Image {i+1}: {img.get("suggested_type", "content")}
├─ Size: {img.get("width")}×{img.get("height")}px  
├─ Context: "{img.get("context", "")[:50]}"
├─ URL: {img.get("actual_url")}
└─ Place in: {img.get("context", "Main content area")[:40]}
''' for i, img in enumerate(meaningful_images[:5]))}

PRIORITY 3 - TINY ICONS ({len(tiny_icons)} found):
For the {len(tiny_icons)} tiny icons (≤32px), use simple CSS icon replacements:
- Use Unicode symbols: ⚙️ 🔍 📱 💻 ⭐ ❤️ 🏠 📧 📞 ✓
- Or use CSS-only shapes with background colors
- Don't use <img> tags for these tiny elements

IMPLEMENTATION RULES:
1. ALWAYS implement logos and meaningful images with <img> tags
2. Use the EXACT URLs provided above (these are from the actual website!)
3. For tiny icons, use Unicode symbols or CSS shapes instead
4. Focus on the {len(logos + meaningful_images)} important images first
5. Make sure logos are prominently placed in header/navigation
6. If an image URL starts with 'data:', skip it (base64 encoded)
"""

        # Build layout info
        layout_info = f"""
DETECTED LAYOUT:
- Site Structure: {visual_context.get('site_structure', 'unknown')}
- Layout Style: {visual_context.get('layout_style', 'unknown')}
- Grid Layouts Found: {len(grid_layouts)}
- Interactive Elements: {len(interactive_elements)}
- Site Category: {visual_context.get('site_category', 'unknown')}

SMART IMAGE SUMMARY:
- Total images detected: {len(image_descriptions)}
- Logos: {len(logos)} (use <img> tags with actual URLs)
- Meaningful images: {len(meaningful_images)} (use <img> tags with actual URLs)  
- Tiny icons: {len(tiny_icons)} (use Unicode/CSS instead)
- Priority images to implement: {len(logos + meaningful_images)}
"""

        return f"""You must recreate this website EXACTLY using the comprehensive data below.

{content_list}

{image_instructions}

{layout_info}

CRITICAL REQUIREMENTS:

1. CONTENT COMPLETENESS:
   • Include ALL navigation items, headings, buttons, and paragraphs listed above
   • Don't skip ANY text content

2. SMART IMAGE IMPLEMENTATION:
   • ALWAYS implement the {len(logos)} logos with <img> tags and ACTUAL URLs from the website
   • ALWAYS implement the {len(meaningful_images)} meaningful images with <img> tags and ACTUAL URLs
   • For the {len(tiny_icons)} tiny icons, use Unicode symbols or CSS shapes (NOT <img> tags)
   • Use the EXACT image URLs provided - they are from the actual website!
   • Focus on quality over quantity - better to have fewer perfect images

3. LAYOUT & STRUCTURE:
   • Use CSS Grid or Flexbox for layouts (detected {len(grid_layouts)} grid layouts)
   • Follow the detected site structure: {visual_context.get('site_structure', 'unknown')}
   • Match the layout style: {visual_context.get('layout_style', 'unknown')}

4. INTERACTIVITY (DISABLED):
   • All buttons: onclick="return false;"
   • All links: href="#" onclick="return false;"
   • All forms: onsubmit="return false;"

5. RESPONSIVE DESIGN:
   • Make it mobile-responsive
   • Use modern CSS with proper breakpoints

Create a complete, working HTML file with embedded CSS that uses the ACTUAL images from the website."""

    def create_system_prompt(self) -> str:
        return """You are an expert web developer specializing in SMART website recreation.
TYPOGRAPHY PRIORITIES:
1. Use EXACT font families from the original site
2. Include Google Fonts link if custom fonts are detected
3. Match font weights precisely (100-900)
4. Preserve text hierarchy with correct sizes
5. Maintain line heights and letter spacing

SMART IMAGE STRATEGY:
- LOGOS: Always use <img> tags with exact URLs provided (from the actual website)
- MEANINGFUL IMAGES (≥100px): Always use <img> tags with exact URLs provided (from the actual website)  
- TINY ICONS (≤32px): Use Unicode symbols (⚙️ 🔍 📱) or CSS shapes instead of <img> tags

ABSOLUTE PRIORITIES:
1. SMART IMAGES: Use the ACTUAL image URLs from the website, not placeholders
2. CONTENT: Include ALL text content from the provided lists
3. LAYOUT: Use modern CSS (Grid/Flexbox) to match the detected structure
4. FUNCTIONALITY: Disable all interactive elements safely

CRITICAL RULES:
- Always use the EXACT image URLs provided - they are from the original website
- Don't create placeholder images or use picsum.photos
- Don't create 17 tiny <img> tags for icons
- Use Unicode symbols for small icons instead
- Focus on the important images that users actually see
- Quality over quantity for image implementation

Always return complete HTML with embedded CSS that works perfectly."""

    def create_simple_refinement_prompt(self, current_html: str, visual_similarity: float, iteration: int) -> str:
        """Refinement focused on smart image handling"""
        
        if visual_similarity > 0.8:
            return f"""The visual similarity is good ({visual_similarity:.3f}). Make only minor improvements:

1. Fine-tune logo and meaningful image positioning
2. Improve hover effects and transitions  
3. Adjust colors and spacing to better match screenshot
4. Ensure logos and main images are prominently displayed
5. Verify all image URLs are the actual ones from the website
6. Fine-tune typography:
   • Verify font families match exactly
   • Check if web fonts are loading properly
   • Adjust font weights and sizes

CRITICAL: Keep ALL existing content and important images exactly as they are.
Only improve styling and positioning.

Current HTML:
{current_html}

Return improved version with better styling but identical content and smart image handling."""
        
        else:
            # Count meaningful images vs tiny icons
            img_count = current_html.count('<img')
            unicode_count = len(re.findall(r'[⚙️🔍📱💻⭐❤️🏠📧📞✓]', current_html))
            
            return f"""Visual similarity is low ({visual_similarity:.3f}). Focus on SMART image improvements:

PRIORITY FIXES:
1. SMART IMAGE STRATEGY: Found {img_count} <img> tags, {unicode_count} Unicode icons
   • Ensure logos and meaningful images (≥100px) use <img> tags with ACTUAL URLs from the website
   • Replace tiny icons with Unicode symbols: ⚙️ 🔍 📱 💻 ⭐ ❤️ 🏠 📧 📞 ✓
   • Verify all image URLs are the original ones, not placeholders
   • Focus on quality over quantity - fewer perfect images is better

2. LAYOUT IMPROVEMENTS:
   • Better CSS Grid/Flexbox implementation
   • Improve spacing and positioning
   • Make logos more prominent in header

3. STYLING:
   • Better color scheme matching
   • Improved typography and spacing
   • More accurate visual recreation

CRITICAL: Keep ALL existing text content exactly as it is.
Focus on smart image handling and visual layout.

Current HTML:
{current_html}

Return improved version with SMART image strategy and better styling."""

    async def clone_website(self, scraped_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main cloning method with SMART image handling"""
        try:
            print("Starting cloning with SMART image filtering...")
            
            context = build_design_context(scraped_data)
            original_screenshot = scraped_data.get("visual", {}).get("screenshot_base64", "") or scraped_data.get("screenshot_base64", "")
            
            if not original_screenshot:
                raise Exception("No screenshot data available")

            # SMART image analysis
            visual_context = scraped_data.get('visual_context', {})
            image_descriptions = visual_context.get('image_descriptions', [])
            image_categories = self.filter_meaningful_images(image_descriptions)
            
            meaningful_count = len(image_categories['meaningful_images'])
            logo_count = len(image_categories['logos'])
            icon_count = len(image_categories['tiny_icons'])
            
            print(f"SMART image analysis:")
            print(f"   Total detected: {len(image_descriptions)} images")
            print(f"   Logos: {logo_count} (will use <img> tags)")
            print(f"   Meaningful images: {meaningful_count} (will use <img> tags)")
            print(f"   Tiny icons: {icon_count} (will use Unicode/CSS)")
            print(f"   Priority images to implement: {logo_count + meaningful_count}")

            # Initial generation with smart image handling
            print("Generating initial HTML with SMART image strategy...")
            html_content = await self._generate_html(scraped_data)
            
            # Validate initial content AND smart images
            initial_content_score = self._simple_content_validation(html_content, scraped_data)
            initial_image_score = self._validate_smart_image_implementation(html_content, scraped_data)
            print(f"Initial scores - Content: {initial_content_score:.1%}, Smart Images: {initial_image_score:.1%}")
            
            best_html = html_content
            best_similarity = 0.0
            iteration_results = []

            # Enhanced iterative refinement with smart image focus
            for iteration in range(1, self.max_iterations + 1):
                print(f"Iteration {iteration}: Testing current version...")
                
                try:
                    # Test current version
                    rendered_screenshot = await render_generated_html(html_content)
                    visual_similarity = compare_base64_images(original_screenshot, rendered_screenshot)
                    content_score = self._simple_content_validation(html_content, scraped_data)
                    image_score = self._validate_smart_image_implementation(html_content, scraped_data)
                    
                    print(f"Visual: {visual_similarity:.3f}, Content: {content_score:.3f}, Smart Images: {image_score:.3f}")
                    
                    # Track best version with smart scoring
                    combined_score = (visual_similarity * 0.6) + (content_score * 0.3) + (image_score * 0.1)
                    if combined_score > best_similarity:
                        best_html = html_content
                        best_similarity = combined_score
                        print(f"New best combined score: {combined_score:.3f}")
                    
                    iteration_results.append({
                        "iteration": iteration,
                        "visual_similarity": visual_similarity,
                        "content_score": content_score,
                        "smart_image_score": image_score,
                        "combined_score": combined_score
                    })
                    
                    # Stop if quality is good enough
                    if visual_similarity >= self.quality_threshold and image_score > 0.7:
                        print(f"Quality threshold reached!")
                        break
                    
                    # CRITICAL: If content score drops significantly, stop refining
                    if content_score < initial_content_score * 0.8:
                        print(f" Content score dropped too much, reverting to best version")
                        html_content = best_html
                        break
                    
                    # Refine with smart image focus if not last iteration
                    if iteration < self.max_iterations:
                        print(f"🔧 Making SMART improvements (logos + meaningful images)...")
                        html_content = await self._simple_refine(html_content, visual_similarity, iteration)
                
                except Exception as e:
                    print(f" Iteration {iteration} failed: {e}")
                    html_content = best_html
                    break

            # Use the best version
            final_html = best_html
            
            # Final assessment with smart image validation
            try:
                final_screenshot = await render_generated_html(final_html)
                final_similarity = compare_base64_images(original_screenshot, final_screenshot)
                final_content_score = self._simple_content_validation(final_html, scraped_data)
                final_image_score = self._validate_smart_image_implementation(final_html, scraped_data)
            except:
                final_similarity = best_similarity
                final_content_score = initial_content_score
                final_image_score = initial_image_score

            print(f"   Cloning complete:")
            print(f"   Visual Similarity: {final_similarity:.3f}")
            print(f"   Content Score: {final_content_score:.3f}")
            print(f"   Smart Image Score: {final_image_score:.3f}")

            return {
                "success": True,
                "html": final_html,
                "visual_similarity": final_similarity,
                "content_completeness": final_content_score,
                "scraper_data_utilization": final_content_score,
                "smart_image_score": final_image_score,
                "iterations": len(iteration_results),
                "analysis": {
                    "quality_score": final_similarity,
                    "content_preservation": final_content_score,
                    "smart_image_implementation": final_image_score,
                    "iterations_completed": len(iteration_results),
                    "image_strategy": f"Logos: {logo_count}, Meaningful: {meaningful_count}, Icons: {icon_count}",
                    "improvement_notes": "SMART image filtering - uses actual website images, Unicode for tiny icons"
                }
            }

        except Exception as e:
            print(f"Cloning failed: {str(e)}")
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "html": self._create_error_page(str(e))
            }

    def _validate_smart_image_implementation(self, html: str, scraped_data: Dict) -> float:
        """Validate SMART image implementation (logos + meaningful images)"""
        visual_context = scraped_data.get('visual_context', {})
        image_descriptions = visual_context.get('image_descriptions', [])
        
        if not image_descriptions:
            return 1.0  # Perfect if no images to implement
        
        # Filter to only meaningful images and logos
        image_categories = self.filter_meaningful_images(image_descriptions)
        priority_images = image_categories['meaningful_images'] + image_categories['logos']
        
        if not priority_images:
            return 1.0  # Perfect if no priority images
        
        total_priority_images = len(priority_images)
        implemented_images = 0
        
        # Check for proper implementation of priority images
        for img in priority_images:
            actual_url = img.get('actual_url', '')
            original_src = img.get('src', '')
            
            # Check if the actual URL is in the HTML
            if actual_url and actual_url in html:
                implemented_images += 1
            elif original_src and original_src in html:
                implemented_images += 1
            elif actual_url and 'picsum.photos' not in actual_url:
                # Check for partial matches (in case of URL modifications)
                url_parts = actual_url.split('/')[-1]  # Get filename
                if url_parts and url_parts in html:
                    implemented_images += 0.8
        
        # Bonus for using Unicode icons instead of tiny <img> tags
        unicode_icons = len(re.findall(r'[⚙️🔍📱💻⭐❤️🏠📧📞✓▶️◀️▲▼►◄]', html))
        if unicode_icons > 0:
            implemented_images += min(unicode_icons * 0.1, 0.5)  # Small bonus for smart icon usage
        
        score = min(implemented_images / total_priority_images, 1.0)
        return score

    async def _generate_html(self, scraped_data: Dict) -> str:
        """Generate initial HTML with smart image focus"""
        screenshot_data = scraped_data.get("visual", {}).get("screenshot_base64") or scraped_data.get("screenshot_base64")
        
        prompt = self.create_comprehensive_prompt(scraped_data)
        
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": screenshot_data
                    }
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }]

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8000,
            temperature=0.1,  # Lower temperature for more consistent implementation
            system=self.create_system_prompt(),
            messages=messages
        )

        return self._extract_html(response.content[0].text)

    async def _simple_refine(self, current_html: str, visual_similarity: float, iteration: int) -> str:
        """Simple refinement with smart image focus"""
        
        refinement_prompt = self.create_simple_refinement_prompt(current_html, visual_similarity, iteration)

        messages = [{
            "role": "user",
            "content": refinement_prompt
        }]

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8000,
            temperature=0.05,  # Very low temperature for refinement
            system=self.create_system_prompt(),
            messages=messages
        )

        return self._extract_html(response.content[0].text)

    def _simple_content_validation(self, html: str, scraped_data: Dict) -> float:
        """Simple validation of content preservation"""
        html_lower = html.lower()
        
        total_checks = 0
        passed_checks = 0
        
        text_data = scraped_data.get('text', {})
        
        # Check headings
        for heading in text_data.get('headings', [])[:8]:
            if heading and len(heading.strip()) > 2:
                total_checks += 1
                if heading.lower() in html_lower:
                    passed_checks += 1
        
        # Check buttons  
        for button in text_data.get('buttons', [])[:8]:
            if button and len(button.strip()) > 2:
                total_checks += 1
                if button.lower() in html_lower:
                    passed_checks += 1
        
        # Check navigation
        for nav in text_data.get('navigation', [])[:8]:
            if nav and len(nav.strip()) > 2:
                total_checks += 1
                if nav.lower() in html_lower:
                    passed_checks += 1
        
        # Basic structure checks
        total_checks += 2
        if 'onclick="return false;"' in html:
            passed_checks += 1
        if any(tag in html_lower for tag in ['<nav', '<header', '<footer', '<main']):
            passed_checks += 1
        
        return passed_checks / max(total_checks, 1)

    def _extract_html(self, response_text: str) -> str:
        """Extract HTML from response"""
        # Remove markdown
        response_text = re.sub(r'```html\n?', '', response_text)
        response_text = re.sub(r'```\n?', '', response_text)
        
        # Find HTML
        patterns = [
            r'<!DOCTYPE html>.*?</html>',
            r'<html.*?</html>'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
            if match:
                html = match.group(0).strip()
                return self._fix_html(html)
        
        return self._fix_html(response_text.strip())

    def _fix_html(self, html: str) -> str:
        """Basic HTML fixes with image preservation"""
        # Disable links
        html = re.sub(r'href="(?!#)[^"]*"', 'href="#" onclick="return false;"', html)
        
        # Disable buttons
        html = re.sub(r'<button(?![^>]*onclick=)', '<button onclick="return false;"', html)
        
        # Disable forms
        html = re.sub(r'<form(?![^>]*onsubmit=)', '<form onsubmit="return false;"', html)
        
        # Add viewport if missing
        if 'viewport' not in html:
            html = html.replace('<head>', '<head>\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        
        # Ensure images have proper loading attributes
        html = re.sub(r'<img([^>]*?)(?<!loading=")(?<!loading=\')>', r'<img\1 loading="lazy">', html)
        
        return html

    def _create_error_page(self, error_message: str) -> str:
        """Simple error page"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Cloning Error</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 40px;
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            text-align: center;
        }}
        .error-container {{
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            max-width: 500px;
        }}
        h1 {{
            color: #d32f2f;
            font-size: 28px;
            margin-bottom: 20px;
        }}
        p {{
            color: #666;
            line-height: 1.6;
            margin-bottom: 20px;
        }}
        .error-details {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 14px;
            color: #333;
            text-align: left;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <h1>Website Cloning Failed</h1>
        <p>An error occurred while attempting to clone the website. This could be due to various factors including API limits, complex page structure, or network issues.</p>
        <div class="error-details">{error_message}</div>
        <p>Please try again or use Classic mode for more reliable results.</p>
    </div>
</body>
</html>"""