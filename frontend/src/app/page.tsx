"use client";

import { useState } from "react";
import Image from "next/image";

export default function Home() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [clonedHtml, setClonedHtml] = useState('');
  const [screenshot, setScreenshot] = useState('');
  const [layout, setLayout] = useState<{ has_nav: boolean; has_header: boolean; has_main: boolean } | null>(null);
  const [viewMode, setViewMode] = useState<'html' | 'screenshot'>('html');
  const [error, setError] = useState('');

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

    try {
      const response = await fetch('/api/clone', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) throw new Error('Failed to clone website');

      const data = await response.json();
      console.log('API response:', data);
      setClonedHtml(data.html);
      setScreenshot(data.screenshot_base64);
      setLayout(data.layout || null);
    } catch (err) {
      setError('Failed to clone website. Please try again.');
      console.error('Clone error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleClone();
    }
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col">
      {/* Header */}
      <header className="flex justify-between items-center p-6">
        <div className="flex items-center space-x-3">
          <h1 className="text-white text-xl font-semibold">Clone Sphere</h1>
        </div>

        {/* Menu button */}
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
              <path
                id="curve"
                d="M 40,0 A 160,160 0 0,0 280,0"
                fill="transparent"
              />
            </defs>
            <text fill="white" fontSize="37.5" fontWeight="500">
              <textPath href="#curve" startOffset="48%" textAnchor="middle">
                Clone ✨ Sphere
              </textPath>
            </text>
          </svg>
        </div>

        {/* Input bar */}
        <div className="flex items-center bg-[#333] rounded-md px-4 py-2 w-150">
          <input
            type="text"
            placeholder="Enter URL"
            value={url}
            onChange={handleInputChange}
            onKeyDown={handleKeyPress}
            className="flex-1 bg-transparent text-white placeholder-gray-400 focus:outline-none"
          />
          <button
            onClick={handleClone}
            disabled={isLoading}
            className="ml-2 text-white hover:opacity-80 transition"
            aria-label="Clone"
          >
            ⏶
          </button>
        </div>

        {error && <p className="text-red-400 mt-4">{error}</p>}

        {(clonedHtml || screenshot) && (
          <div className="mt-12 w-full max-w-5xl bg-white text-black p-6 rounded-lg overflow-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Cloned Site Preview</h2>
              <button
                onClick={() => setViewMode(viewMode === 'html' ? 'screenshot' : 'html')}
                className="text-sm bg-black text-white px-3 py-1 rounded hover:opacity-80"
              >
                View as {viewMode === 'html' ? 'Screenshot' : 'HTML'}
              </button>
            </div>

            {viewMode === 'html' ? (
              <iframe
                srcDoc={clonedHtml}
                className="w-full h-[80vh] border rounded-md"
              />
            ) : (
              <img
                src={`data:image/png;base64,${screenshot}`}
                alt="Website Screenshot"
                className="w-full h-auto border rounded-md"
              />
            )}

            {layout && (
              <div className="mt-4 text-sm text-gray-700 space-y-1">
                <p><strong>Has Navigation:</strong> {layout.has_nav ? 'Yes' : 'No'}</p>
                <p><strong>Has Header:</strong> {layout.has_header ? 'Yes' : 'No'}</p>
                <p><strong>Has Main Content:</strong> {layout.has_main ? 'Yes' : 'No'}</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
