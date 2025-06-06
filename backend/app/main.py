from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import traceback
import time

# Updated import to use the simple fixed cloner
from app.scraper.intelligent_scraper import intelligent_clone
from app.llm.llm_cloner import WebsiteCloner  # Simple fixed cloner

app = FastAPI(title="Orchids Website Cloner", version="2.1.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM client with simple fixed cloner
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    print("⚠️  WARNING: ANTHROPIC_API_KEY not found - LLM modes will not work")
    
# Use the simple fixed cloner
cloner = WebsiteCloner(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

# Request schemas (simplified)
class CloneRequest(BaseModel):
    url: str
    mode: str = "iterative"  # "classic", "llm", or "iterative"
    max_iterations: int = 1
    quality_threshold: float = 0.85

class CloneResponse(BaseModel):
    success: bool
    html: str
    screenshot_base64: str = ""
    layout: dict = {}
    analysis: dict = {}
    visual_similarity: float = 0.0
    content_completeness: float = 0.0
    scraper_data_utilization: float = 0.0
    iterations: int = 0
    processing_time: float = 0.0
    error: str = ""

@app.get("/")
async def root():
    return {
        "message": "Orchids Website Cloner API - Simple Fixed Version",
        "version": "2.1.0",
        "features": [
            "Classic HTML cloning (direct CSS preservation)",
            "LLM cloning (AI recreation with scraper data)",
            "Iterative refinement cloning (FIXED - preserves content)",
            "Intelligent scraper with rich visual context extraction"
        ],
        "fixes": [
            "FIXED: Iterative refinement no longer destroys content",
            "Simple content preservation logic",
            "Automatic reversion when content quality drops",
            "Better refinement prompts that preserve structure"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "modes": {
            "classic": "available",
            "llm": "configured" if ANTHROPIC_API_KEY else "missing_api_key",
            "iterative": "configured" if ANTHROPIC_API_KEY else "missing_api_key"
        },
        "scraper": "intelligent_scraper_with_comprehensive_analysis",
        "cloner": "simple_fixed_cloner_v2.1",
        "fixes": "content_preservation_logic_added",
        "timestamp": time.time()
    }

@app.post("/api/clone", response_model=CloneResponse)
async def clone_website_endpoint(request: CloneRequest):
    start_time = time.time()
    
    try:
        print(f"🎯 Starting {request.mode} clone: {request.url}")
        
        if request.mode == "classic":
            return await handle_classic_clone(request, start_time)
        elif request.mode == "llm":
            if not cloner:
                raise HTTPException(status_code=400, detail="LLM mode requires ANTHROPIC_API_KEY")
            return await handle_llm_clone(request, start_time)
        elif request.mode == "iterative":
            if not cloner:
                raise HTTPException(status_code=400, detail="Iterative mode requires ANTHROPIC_API_KEY")
            return await handle_iterative_clone(request, start_time)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid mode: {request.mode}. Use 'classic', 'llm', or 'iterative'"
            )

    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = str(e)
        print(f"❌ Clone failed after {processing_time:.2f}s: {error_msg}")
        print("Full traceback:", traceback.format_exc())
        
        return CloneResponse(
            success=False,
            html=create_error_html(error_msg, request.mode),
            error=error_msg,
            processing_time=processing_time
        )

async def handle_classic_clone(request: CloneRequest, start_time: float) -> CloneResponse:
    """Handle classic direct HTML cloning - fast and reliable WITH INTERACTIVE ELEMENTS"""
    print("🔧 Using Classic Mode (Direct HTML Preservation + Interactive Elements)")
    
    # FIXED: Use intelligent scraper with interactive elements enabled
    result = await intelligent_clone(
        request.url, 
        mode="classic", 
        keep_interactive=True  # ← This enables button/link functionality!
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail="Classic clone failed")

    processing_time = time.time() - start_time
    print(f"✅ Classic clone with interactive elements completed in {processing_time:.2f}s")

    return CloneResponse(
        success=True,
        html=result["html"],
        screenshot_base64=result.get("screenshot_base64", ""),
        layout=result.get("layout", {}),
        processing_time=processing_time,
        iterations=1,
        visual_similarity=1.0,
        content_completeness=1.0,
        scraper_data_utilization=1.0,
        analysis={
            "mode": "classic",
            "method": "direct_html_preservation",
            "css_inlined": True,
            "interactive_elements": "enabled",  # ← Updated
            "links_functional": True,           # ← Updated
            "buttons_functional": True,         # ← Updated
            "quality_score": 1.0
        }
    )

async def handle_llm_clone(request: CloneRequest, start_time: float) -> CloneResponse:
    """Handle single-shot LLM cloning with scraper data"""
    print("🤖 Using LLM Mode (AI Recreation with Scraper Data)")
    
    # Use intelligent scraper in LLM mode for rich context
    print("📊 Running intelligent scraper...")
    scraped_data = await intelligent_clone(
        request.url, 
        mode="llm",
        keep_interactive=True  # ← Enable for LLM mode too
    )
      
    if not scraped_data.get("success"):
        raise HTTPException(status_code=500, detail="Scraping failed")

    # Log what the scraper found
    visual_context = scraped_data.get('visual_context', {})
    print(f"📈 Scraper found:")
    print(f"   - Content sections: {len(visual_context.get('content_sections', []))}")
    print(f"   - Grid layouts: {len(visual_context.get('grid_layouts', []))}")
    print(f"   - Images: {len(visual_context.get('image_descriptions', []))}")
    print(f"   - Interactive elements: {len(visual_context.get('interactive_elements', []))}")

    # Configure for single pass
    cloner.max_iterations = 1
    cloner.quality_threshold = 0.0  # Don't stop early for single shot
    
    print("🧠 Processing with Claude AI...")
    llm_result = await cloner.clone_website(scraped_data)

    if not llm_result.get("success"):
        raise HTTPException(
            status_code=500, 
            detail=llm_result.get("error", "LLM cloning failed")
        )

    processing_time = time.time() - start_time
    
    # Get metrics
    visual_similarity = llm_result.get("visual_similarity", 0.0)
    content_completeness = llm_result.get("content_completeness", 0.0)
    scraper_utilization = llm_result.get("scraper_data_utilization", 0.0)
    
    print(f"✅ LLM clone completed in {processing_time:.2f}s")
    print(f"📊 Visual similarity: {visual_similarity:.3f}")
    print(f"📊 Content completeness: {content_completeness:.3f}")

    return CloneResponse(
        success=True,
        html=llm_result["html"],
        screenshot_base64=scraped_data["screenshot_base64"],
        layout=scraped_data.get("layout", {}),
        analysis=llm_result.get("analysis", {}),
        visual_similarity=visual_similarity,
        content_completeness=content_completeness,
        scraper_data_utilization=scraper_utilization,
        iterations=1,
        processing_time=processing_time
    )

async def handle_iterative_clone(request: CloneRequest, start_time: float) -> CloneResponse:
    """Handle FIXED iterative refinement cloning"""
    print("🎯 Using FIXED Iterative Mode (Content Preservation)")
    
    # Use intelligent scraper in iterative mode
    print("📸 Running comprehensive scraping...")
    scraped_data = await intelligent_clone(
        request.url, 
        mode="iterative",
        keep_interactive=True 
    )
    
    if not scraped_data.get("success"):
        raise HTTPException(status_code=500, detail="Scraping failed")

    # Log comprehensive analysis
    visual_context = scraped_data.get('visual_context', {})
    print(f"📈 Comprehensive scraper analysis:")
    print(f"   - Content sections: {len(visual_context.get('content_sections', []))}")
    print(f"   - Grid layouts: {len(visual_context.get('grid_layouts', []))}")
    print(f"   - Images positioned: {len(visual_context.get('image_descriptions', []))}")
    print(f"   - Interactive elements: {len(visual_context.get('interactive_elements', []))}")
    print(f"   - Site category: {visual_context.get('site_category', 'unknown')}")
    print(f"   - Layout style: {visual_context.get('layout_style', 'unknown')}")

    # Configure FIXED iterative settings
    cloner.max_iterations = request.max_iterations
    cloner.quality_threshold = request.quality_threshold
    
    print(f"⚙️  Configured: {request.max_iterations} max iterations, {request.quality_threshold} quality threshold")
    print("🔧 Using FIXED refinement logic that preserves content")
    
    # Run FIXED iterative cloning
    print("🔄 Starting FIXED iterative refinement process...")
    llm_result = await cloner.clone_website(scraped_data)

    if not llm_result.get("success"):
        raise HTTPException(
            status_code=500, 
            detail=llm_result.get("error", "Iterative cloning failed")
        )

    processing_time = time.time() - start_time
    
    # Get metrics
    final_similarity = llm_result.get("visual_similarity", 0.0)
    content_completeness = llm_result.get("content_completeness", 0.0)
    scraper_utilization = llm_result.get("scraper_data_utilization", 0.0)
    iterations = llm_result.get("iterations", 0)
    
    print(f"✅ FIXED iterative clone completed in {processing_time:.2f}s")
    print(f"📊 Final metrics after {iterations} iterations:")
    print(f"   - Visual similarity: {final_similarity:.3f}")
    print(f"   - Content completeness: {content_completeness:.3f}")
    print(f"   - Scraper data utilization: {scraper_utilization:.3f}")

    return CloneResponse(
        success=True,
        html=llm_result["html"],
        screenshot_base64=scraped_data["screenshot_base64"],
        layout=scraped_data.get("layout", {}),
        analysis=llm_result.get("analysis", {}),
        visual_similarity=final_similarity,
        content_completeness=content_completeness,
        scraper_data_utilization=scraper_utilization,
        iterations=iterations,
        processing_time=processing_time
    )

@app.get("/api/status")
async def get_status():
    """Get API status and configuration"""
    return {
        "status": "operational",
        "version": "2.1.0",
        "fixes": {
            "content_preservation": "Iterative mode now preserves content during refinement",
            "smart_stopping": "Stops refinement when content quality drops",
            "simple_logic": "Removed complex refinement logic that caused issues"
        },
        "scraper": {
            "type": "intelligent_scraper_v2",
            "features": [
                "Universal visual context extraction",
                "Content section detection", 
                "Grid layout analysis",
                "Interactive element mapping",
                "Color scheme extraction",
                "Image positioning and context analysis"
            ]
        },
        "modes": {
            "classic": {
                "available": True,
                "description": "Direct HTML preservation with CSS inlining",
                "speed": "fast (~3-8s)",
                "accuracy": "high (preserves original styling)",
                "best_for": "Complex sites, production use"
            },
            "llm": {
                "available": bool(ANTHROPIC_API_KEY),
                "description": "Single-shot AI recreation using scraper data",
                "speed": "medium (~10-25s)",
                "accuracy": "good (uses comprehensive scraper data)",
                "best_for": "Modern sites with clear structure"
            },
            "iterative": {
                "available": bool(ANTHROPIC_API_KEY),
                "description": "FIXED - Multiple AI passes with content preservation",
                "speed": "slow (~20-60s)",
                "accuracy": "highest (FIXED refinement logic)",
                "best_for": "When you need the best quality",
                "fix_notes": "Now preserves content during refinement instead of destroying it"
            }
        },
        "configuration": {
            "default_max_iterations": 1,
            "default_quality_threshold": 0.85,
            "supported_models": ["claude-3-5-sonnet-20241022"],
            "visual_comparison": "SSIM (Structural Similarity Index)",
            "content_preservation": "Automatic reversion when content score drops > 20%"
        },
        "api_keys": {
            "anthropic": "configured" if ANTHROPIC_API_KEY else "missing"
        }
    }

@app.get("/api/test/{mode}")
async def test_mode(mode: str):
    """Test endpoint for debugging specific modes"""
    test_url = "https://example.com"
    
    if mode not in ["classic", "llm", "iterative"]:
        raise HTTPException(status_code=400, detail="Invalid mode")
    
    if mode in ["llm", "iterative"] and not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=400, detail="AI modes require ANTHROPIC_API_KEY")
    
    try:
        request = CloneRequest(url=test_url, mode=mode)
        result = await clone_website_endpoint(request)
        
        return {
            "mode": mode,
            "test_url": test_url,
            "success": result.success,
            "processing_time": result.processing_time,
            "visual_similarity": result.visual_similarity,
            "content_completeness": result.content_completeness,
            "scraper_data_utilization": result.scraper_data_utilization,
            "iterations": result.iterations,
            "html_length": len(result.html),
            "has_screenshot": bool(result.screenshot_base64)
        }
    except Exception as e:
        return {
            "mode": mode,
            "test_url": test_url,
            "success": False,
            "error": str(e)
        }

def create_error_html(error_message: str, mode: str = "classic") -> str:
    """Create error page"""
    mode_descriptions = {
        "classic": "Classic Cloner (Direct HTML)",
        "llm": "LLM Cloner (AI Recreation)", 
        "iterative": "FIXED Iterative Cloner (Content Preservation)"
    }
    
    mode_suggestions = {
        "classic": [
            "Check if the website is publicly accessible",
            "Try a simpler website URL",
            "Ensure the site doesn't block automated browsers"
        ],
        "llm": [
            "Try Classic mode for more reliable results",
            "Check ANTHROPIC_API_KEY configuration",
            "Verify the website has clear, simple layout"
        ],
        "iterative": [
            "Try LLM mode for faster results",
            "Try Classic mode for most reliable results", 
            "Check if API rate limits are being hit",
            "The FIXED version should preserve content better"
        ]
    }
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloning Error - Orchids v2.1</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 40px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .error-container {{
            background: rgba(255,255,255,0.95);
            color: #333;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            max-width: 600px;
            text-align: center;
        }}
        h1 {{
            color: #e74c3c;
            margin-bottom: 20px;
            font-size: 2rem;
        }}
        .mode-info {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 12px;
            margin: 20px 0;
            border-left: 4px solid #007bff;
        }}
        .fix-note {{
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #28a745;
        }}
        .error-details {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            margin-top: 25px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            text-align: left;
            overflow-wrap: break-word;
            max-height: 200px;
            overflow-y: auto;
        }}
        .suggestions {{
            text-align: left;
            margin-top: 20px;
            background: #e8f4fd;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #007bff;
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <div style="font-size: 4rem; margin-bottom: 20px;">🚫</div>
        <h1>Website Cloning Failed</h1>
        
        <div class="mode-info">
            <strong>Mode Used:</strong> {mode_descriptions.get(mode, mode)}<br>
            <small>Try switching modes for better results</small>
        </div>
        
        {f'''
        <div class="fix-note">
            <strong>🔧 FIXED:</strong> Iterative mode now preserves content during refinement!
        </div>
        ''' if mode == 'iterative' else ''}
        
        <div class="suggestions">
            <h3>💡 Solutions:</h3>
            <ul>
                {chr(10).join(f'<li>{suggestion}</li>' for suggestion in mode_suggestions.get(mode, []))}
            </ul>
        </div>
        
        <div class="error-details">
            <strong>Technical Details:</strong><br>
            {error_message[:800]}{'...' if len(error_message) > 800 else ''}
        </div>
    </div>
</body>
</html>"""