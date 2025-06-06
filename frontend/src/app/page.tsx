"use client";

import { useState } from "react";
import Image from "next/image";

export default function Home() {
  const [url, setUrl] = useState('');
  const [mode, setMode] = useState<'classic' | 'llm' | 'iterative'>('classic'); // Default to classic
  const [isLoading, setIsLoading] = useState(false);
  const [clonedHtml, setClonedHtml] = useState('');
  const [screenshot, setScreenshot] = useState('');
  const [layout, setLayout] = useState<any>(null);
  const [viewMode, setViewMode] = useState<'html' | 'screenshot'>('html');
  const [error, setError] = useState('');
  
  // Enhanced state for all modes
  const [cloneStats, setCloneStats] = useState<{
    similarity: number;
    iterations: number;
    processingTime: number;
    mode: string;
  } | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUrl(e.target.value);
    setError('');
  };

  const handleClone = async () => {
    if (!url) {
      setError('Please enter a valid URL');
      return;
    }

    try {
      new URL(url);
    } catch {
      setError('Please enter a valid URL');
      return;
    }

    setIsLoading(true);
    setError('');
    setClonedHtml('');
    setScreenshot('');
    setLayout(null);
    setCloneStats(null);

    try {
      const requestBody = {
        url,
        mode,
        ...(mode === 'iterative' && {
          max_iterations: 1,
          quality_threshold: 0.85
        })
      };

      console.log(`🎯 Starting ${mode} clone...`);
      
      const response = await fetch('http://127.0.0.1:8000/api/clone', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to clone website');
      }

      const data = await response.json();
      console.log('API response:', data);
      
      if (data.success) {
        setClonedHtml(data.html);
        setScreenshot(data.screenshot_base64);
        setLayout(data.layout || null);
        
        // Set stats for all modes
        setCloneStats({
          similarity: data.visual_similarity || 1.0, // Classic mode defaults to 1.0
          iterations: data.iterations || 1,
          processingTime: data.processing_time || 0,
          mode: mode
        });
        
        console.log(`✅ ${mode} clone completed successfully!`);
      } else {
        throw new Error(data.error || 'Cloning failed');
      }
    } catch (err: any) {
      const errorMsg = err.message || 'Failed to clone website. Please try again.';
      setError(errorMsg);
      console.error('Clone error:', err);
      
      // Show helpful error suggestions
      if (errorMsg.includes('ANTHROPIC_API_KEY') && (mode === 'llm' || mode === 'iterative')) {
        setError('LLM modes require ANTHROPIC_API_KEY. Try Classic mode instead.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleClone();
    }
  };

  const getQualityGrade = (similarity: number) => {
    if (similarity >= 0.95) return { grade: 'A+', color: 'text-green-500' };
    if (similarity >= 0.9) return { grade: 'A', color: 'text-green-400' };
    if (similarity >= 0.8) return { grade: 'B', color: 'text-blue-400' };
    if (similarity >= 0.7) return { grade: 'C', color: 'text-yellow-400' };
    return { grade: 'D', color: 'text-red-400' };
  };

  const getModeDescription = (mode: string) => {
    const descriptions = {
      'classic': 'Direct HTML preservation with CSS inlining - Fast & Reliable',
      'llm': 'AI recreation using Claude - Creative but variable',
      'iterative': 'Multiple AI passes with refinement - Highest quality when working'
    };
    return descriptions[mode as keyof typeof descriptions] || '';
  };

  const getModeIcon = (mode: string) => {
    const icons = {
      'classic': '🔧',
      'llm': '🤖', 
      'iterative': '🎯'
    };
    return icons[mode as keyof typeof icons] || '⚡';
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col">
      {/* Header */}
      <header className="flex justify-between items-center p-6">
        <div className="flex items-center space-x-3">
          <h1 className="text-white text-xl font-semibold">Clone Sphere</h1>
          <span className="text-xs bg-purple-600 px-2 py-1 rounded-full">v2.0</span>
        </div>
        <button className="text-white p-2 hover:bg-white/10 rounded-lg transition-colors">
          <div className="w-6 h-6 flex flex-col justify-center space-y-1">
            <div className="w-full h-0.5 bg-white"></div>
            <div className="w-full h-0.5 bg-white"></div>
            <div className="w-full h-0.5 bg-white"></div>
          </div>
        </button>
      </header>

      {/* Main content */}
      <main className="flex-1 flex flex-col items-center justify-start pt-20 px-6">

        {/* Sphere + Curved Text */}
        <div className="relative mb-8 pb-20">
          <div className="relative w-64 h-64 mx-auto rounded-full overflow-hidden shadow-2xl">
            <Image
              src="/media/clonesphere.png"
              alt="Clone Sphere"
              fill
              className="object-cover"
              priority
            />
          </div>

          <svg
            className="absolute top-[60%] left-1/2 transform -translate-x-1/2"
            width="320"
            height="200"
            viewBox="0 0 320 160"
          >
            <defs>
              <path id="curve" d="M 40,0 A 160,160 0 0,0 280,0" fill="transparent" />
            </defs>
            <text fill="white" fontSize="37.5" fontWeight="500">
              <textPath href="#curve" startOffset="48%" textAnchor="middle">
                Clone ✨ Sphere
              </textPath>
            </text>
          </svg>
        </div>

        {/* Mode Selection - Enhanced */}
        <div className="mb-4 w-full max-w-md">
          <label className="block text-sm mb-2 text-white font-medium">Cloning Mode</label>
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as 'classic' | 'llm' | 'iterative')}
            className="w-full px-4 py-3 rounded-md bg-[#333] text-white border border-gray-600 focus:outline-none focus:border-purple-500 transition-colors"
          >
            <option value="classic">{getModeIcon('classic')} Classic (Direct HTML) - Recommended</option>
            <option value="llm">{getModeIcon('llm')} LLM Cloning (AI Recreation)</option>
            <option value="iterative">{getModeIcon('iterative')} Iterative Refinement (Advanced AI)</option>
          </select>
          <p className="text-xs text-gray-400 mt-1">{getModeDescription(mode)}</p>
        </div>

        {/* Input bar */}
        <div className="flex items-center bg-[#333] rounded-md px-4 py-2 w-150">
          <input
            type="text"
            placeholder="Enter URL (e.g., https://example.com)"
            value={url}
            onChange={handleInputChange}
            onKeyDown={handleKeyPress}
            className="flex-1 bg-transparent text-white placeholder-gray-400 focus:outline-none"
          />
          <button
            onClick={handleClone}
            disabled={isLoading}
            className="ml-2 text-white hover:opacity-80 transition disabled:opacity-50"
            aria-label="Clone"
          >
            {isLoading ? '⏳' : '⏶'}
          </button>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-900/50 border border-red-500 rounded-md">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {/* Clone Statistics - Enhanced for all modes */}
        {cloneStats && (
          <div className="mt-6 grid grid-cols-4 gap-4 w-full max-w-2xl">
            <div className="bg-[#333] p-3 rounded-lg text-center">
              <div className="text-lg font-bold text-purple-400">{getModeIcon(cloneStats.mode)}</div>
              <div className="text-xs text-gray-400">Mode</div>
              <div className="text-xs text-gray-500 capitalize">{cloneStats.mode}</div>
            </div>
            <div className="bg-[#333] p-3 rounded-lg text-center">
              <div className={`text-xl font-bold ${getQualityGrade(cloneStats.similarity).color}`}>
                {getQualityGrade(cloneStats.similarity).grade}
              </div>
              <div className="text-xs text-gray-400">Quality</div>
              <div className="text-xs text-gray-500">{(cloneStats.similarity * 100).toFixed(1)}%</div>
            </div>
            <div className="bg-[#333] p-3 rounded-lg text-center">
              <div className="text-xl font-bold text-blue-400">{cloneStats.iterations}</div>
              <div className="text-xs text-gray-400">Iterations</div>
              <div className="text-xs text-gray-500">{cloneStats.iterations === 1 ? 'Single' : 'Multiple'}</div>
            </div>
            <div className="bg-[#333] p-3 rounded-lg text-center">
              <div className="text-xl font-bold text-green-400">{cloneStats.processingTime.toFixed(1)}s</div>
              <div className="text-xs text-gray-400">Time</div>
              <div className="text-xs text-gray-500">
                {cloneStats.processingTime < 5 ? 'Fast' : cloneStats.processingTime < 15 ? 'Medium' : 'Slow'}
              </div>
            </div>
          </div>
        )}

        {/* Loading indicator */}
        {isLoading && (
          <div className="mt-6 text-center">
            <div className="inline-flex items-center space-x-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-500"></div>
              <span className="text-gray-400">
                {mode === 'classic' ? 'Preserving HTML...' : 
                 mode === 'llm' ? 'AI recreating...' : 
                 'Iteratively refining...'}
              </span>
            </div>
          </div>
        )}

        {(clonedHtml || screenshot) && (
          <div className="mt-12 w-full max-w-5xl bg-white text-black p-6 rounded-lg overflow-auto">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h2 className="text-xl font-semibold">Cloned Site Preview</h2>
                {cloneStats && (
                  <p className="text-sm text-gray-600">
                    {getModeIcon(cloneStats.mode)} {cloneStats.mode.charAt(0).toUpperCase() + cloneStats.mode.slice(1)} Mode • 
                    Quality: {getQualityGrade(cloneStats.similarity).grade} ({(cloneStats.similarity * 100).toFixed(1)}%) • 
                    {cloneStats.iterations} iteration{cloneStats.iterations !== 1 ? 's' : ''} • 
                    {cloneStats.processingTime.toFixed(1)}s
                  </p>
                )}
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setViewMode(viewMode === 'html' ? 'screenshot' : 'html')}
                  className="text-sm bg-black text-white px-3 py-1 rounded hover:opacity-80 transition"
                >
                  View as {viewMode === 'html' ? 'Screenshot' : 'HTML'}
                </button>
                {clonedHtml && (
                  <button
                    onClick={() => {
                      const blob = new Blob([clonedHtml], { type: 'text/html' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `cloned-website-${mode}.html`;
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                    className="text-sm bg-purple-600 text-white px-3 py-1 rounded hover:bg-purple-700 transition"
                  >
                    📥 Download HTML
                  </button>
                )}
              </div>
            </div>

            {viewMode === 'html' ? (
              <iframe
                srcDoc={clonedHtml}
                className="w-full h-[80vh] border rounded-md"
                sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-popups-to-escape-sandbox allow-top-navigation-by-user-activation"
                title="Cloned Website Preview"
              />
            ) : (
              <img
                src={`data:image/png;base64,${screenshot}`}
                alt="Website Screenshot"
                className="w-full h-auto border rounded-md"
              />
            )}

            {/* Enhanced Layout Info */}
            {layout && (
              <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-700">
                <div className="bg-gray-100 p-2 rounded">
                  <div className="font-medium">Navigation</div>
                  <div>{layout.has_nav ? '✅ Yes' : '❌ No'}</div>
                </div>
                <div className="bg-gray-100 p-2 rounded">
                  <div className="font-medium">Header</div>
                  <div>{layout.has_header ? '✅ Yes' : '❌ No'}</div>
                </div>
                <div className="bg-gray-100 p-2 rounded">
                  <div className="font-medium">Main Content</div>
                  <div>{layout.has_main ? '✅ Yes' : '❌ No'}</div>
                </div>
                <div className="bg-gray-100 p-2 rounded">
                  <div className="font-medium">Footer</div>
                  <div>{layout.has_footer ? '✅ Yes' : '❌ No'}</div>
                </div>
                {layout.element_count && (
                  <>
                    <div className="bg-gray-100 p-2 rounded">
                      <div className="font-medium">Elements</div>
                      <div>{layout.element_count}</div>
                    </div>
                    <div className="bg-gray-100 p-2 rounded">
                      <div className="font-medium">Images</div>
                      <div>{layout.image_count || 0}</div>
                    </div>
                    <div className="bg-gray-100 p-2 rounded">
                      <div className="font-medium">Links</div>
                      <div>{layout.link_count || 0}</div>
                    </div>
                    <div className="bg-gray-100 p-2 rounded">
                      <div className="font-medium">Buttons</div>
                      <div>{layout.button_count || 0}</div>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        )}

        {/* Mode comparison info */}
        {!clonedHtml && !isLoading && (
          <div className="mt-12 w-full max-w-4xl grid md:grid-cols-3 gap-6 text-center">
            <div className="bg-[#222] p-6 rounded-lg border border-gray-700">
              <div className="text-3xl mb-3">🔧</div>
              <h3 className="text-lg font-semibold mb-2">Classic Mode</h3>
              <p className="text-sm text-gray-400 mb-3">
                Direct HTML preservation with CSS inlining. Fast, reliable, and preserves original design.
              </p>
              <div className="text-xs text-green-400">✅ Recommended for most sites</div>
            </div>
            
            <div className="bg-[#222] p-6 rounded-lg border border-gray-700">
              <div className="text-3xl mb-3">🤖</div>
              <h3 className="text-lg font-semibold mb-2">LLM Mode</h3>
              <p className="text-sm text-gray-400 mb-3">
                AI recreates the website from scratch. Creative but results can vary.
              </p>
              <div className="text-xs text-yellow-400">⚠️ Requires API key</div>
            </div>
            
            <div className="bg-[#222] p-6 rounded-lg border border-gray-700">
              <div className="text-3xl mb-3">🎯</div>
              <h3 className="text-lg font-semibold mb-2">Iterative Mode</h3>
              <p className="text-sm text-gray-400 mb-3">
                Multiple AI passes with visual comparison. Highest quality when working.
              </p>
              <div className="text-xs text-blue-400">🚀 Most advanced</div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}