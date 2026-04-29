'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

interface LessonPlanResponse {
  success: boolean;
  query?: string;
  lesson_plan?: string;
  error?: string;
}

export default function Home() {
  const [query, setQuery] = useState('');
  const [k, setK] = useState(3);
  const [systemInstruction, setSystemInstruction] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<LessonPlanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL;

      const res = await fetch(`${API_URL}/planner`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          k: k,
          system_instruction: systemInstruction || undefined,
        }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data: LessonPlanResponse = await res.json();
      setResponse(data);

      if (!data.success) {
        setError(data.error || 'Failed to generate lesson plan');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Lesson Plan Generator
          </h1>
          <p className="text-xl text-gray-600">
            Generate personalized lesson plans tailored to your learning style
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Form Section */}
          <div className="lg:col-span-1">
            <form
              onSubmit={handleSubmit}
              className="bg-white rounded-lg shadow-lg p-8 sticky top-8"
            >
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Your Query
              </h2>

              {/* Query Input */}
              <div className="mb-6">
                <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
                  What would you like to learn?
                </label>
                <textarea
                  id="query"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="e.g., Teach me about data structures and their applications"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                  rows={5}
                  required
                />
              </div>

              {/* K Parameter */}
              <div className="mb-6">
                <label htmlFor="k" className="block text-sm font-medium text-gray-700 mb-2">
                  Context Chunks (k): <span className="font-bold text-indigo-600">{k}</span>
                </label>
                <input
                  id="k"
                  type="range"
                  min="1"
                  max="10"
                  value={k}
                  onChange={(e) => setK(parseInt(e.target.value))}
                  className="w-full"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Number of relevant context chunks to include
                </p>
              </div>

              {/* System Instruction */}
              <div className="mb-6">
                <label htmlFor="instruction" className="block text-sm font-medium text-gray-700 mb-2">
                  Custom Instruction (Optional)
                </label>
                <input
                  id="instruction"
                  type="text"
                  value={systemInstruction}
                  onChange={(e) => setSystemInstruction(e.target.value)}
                  placeholder="e.g., Focus on practical examples"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || !query.trim()}
                className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-bold py-3 px-4 rounded-lg transition duration-200 ease-in-out"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating...
                  </span>
                ) : (
                  'Generate Lesson Plan'
                )}
              </button>
            </form>
          </div>

          {/* Results Section */}
          <div className="lg:col-span-2">
            {error && (
              <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-lg mb-6">
                <p className="text-red-700 font-medium">Error</p>
                <p className="text-red-600 mt-1">{error}</p>
              </div>
            )}

            {response && response.success ? (
              <div className="bg-white rounded-lg shadow-lg p-8">
                <div className="mb-6">
                  <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
                    Your Query
                  </h2>
                  <p className="text-lg text-gray-900 font-medium">{response.query}</p>
                </div>

                <div className="border-t border-gray-200 pt-6">
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">
                    Lesson Plan
                  </h3>
                  <div className="prose prose-indigo max-w-none">
                    <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                      {response.lesson_plan}
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-6 border-t border-gray-200">
                  <button
                    onClick={() => {
                      setQuery('');
                      setResponse(null);
                      setError(null);
                    }}
                    className="text-indigo-600 hover:text-indigo-700 font-medium"
                  >
                    ← Generate Another
                  </button>
                </div>
              </div>
            ) : !loading && !response ? (
              <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-lg border-2 border-dashed border-indigo-300 p-12 text-center">
                <svg
                  className="mx-auto h-12 w-12 text-indigo-400 mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 6v6m0 0v6m0-6h6m0 0h6m0-6h-6m0 0H6"
                  />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Ready to learn something new?
                </h3>
                <p className="text-gray-600">
                  Enter your query and click "Generate Lesson Plan" to get started
                </p>
              </div>
            ) : null}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-gray-600 text-sm">
          <p>Powered by RAG + Cohere LLM</p>
        </div>
      </div>
    </div>
  );
}
