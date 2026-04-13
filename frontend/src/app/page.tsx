"use client";

import { useState } from "react";

interface TabInfo {
  index: number;
  url: string;
  title: string;
  active: boolean;
}

export default function Home() {
  const [script, setScript] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("Idle");

  const [robotScript, setRobotScript] = useState("");
  const [bddScenario, setBddScenario] = useState("");
  
  const [bddCopied, setBddCopied] = useState(false);
  const [robotCopied, setRobotCopied] = useState(false);

  const [tabs, setTabs] = useState<TabInfo[]>([]);

  const baseUrl = `${process.env.NEXT_PUBLIC_API_URL}/api`;

  const apiCall = async (path: string, method: string = "POST", body?: any) => {
    setLoading(true);
    try {
      const res = await fetch(`${baseUrl}${path}`, {
        method,
        headers: { "Content-Type": "application/json" },
        body: body ? JSON.stringify(body) : undefined,
      });
      const data = await res.json();
      if (data.status === "error") {
        alert(`Error: ${data.message}`);
      }
      return data;
    } catch (error) {
      console.error("API Call failed:", error);
      alert("Make sure the backend is running at the configured API URL");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async (text: string, type: "bdd" | "robot") => {
    try {
      await navigator.clipboard.writeText(text);
      if (type === "bdd") {
        setBddCopied(true);
        setTimeout(() => setBddCopied(false), 2000);
      } else {
        setRobotCopied(true);
        setTimeout(() => setRobotCopied(false), 2000);
      }
    } catch (err) {
      console.error("Failed to copy:", err);
      alert("Failed to copy to clipboard");
    }
  };

  const refreshTabs = async () => {
    const res = await apiCall("/record/tabs", "GET");
    if (res?.tabs) {
      setTabs(res.tabs);
    }
  };

  const startBrowser = async () => {
    const res = await apiCall("/browser/start");
    if (res?.status === "success") {
      setStatus("Browser Running");
      // navigate to a start page
      await apiCall("/record/navigate", "POST", { url: "https://www.google.com" });
      await refreshTabs();
    }
  };

  const openNewTab = async () => {
    const url = prompt("Enter URL for the new tab:", "https://");
    if (!url || url === "https://") return;
    const res = await apiCall("/record/open-tab", "POST", { url });
    if (res?.status === "success") {
      setStatus(`Tab opened: ${url}`);
      await refreshTabs();
    }
  };

  const generateAll = async () => {
    const res = await apiCall("/generate/generate-all", "GET");
    if (res?.bdd) {
      setBddScenario(res.bdd);
      setRobotScript(res.robot);
      setStatus("Test Cases Generated");
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 px-6 md:px-8 py-6 md:py-12 font-sans text-slate-900 relative">
      {/* Loading Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center transition-opacity">
          <div className="bg-white p-6 rounded-2xl shadow-xl flex flex-col items-center gap-4">
            <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
            <p className="font-bold text-slate-700">Connecting to Agent...</p>
          </div>
        </div>
      )}

      <div className="w-full mx-auto space-y-8">
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-6">
          <div>
            <h1 className="text-3xl font-black text-slate-800 tracking-tight">AI Automation Agent</h1>
            <p className="text-slate-500 font-medium tracking-wide text-sm uppercase">BDD & Robot Framework Generator</p>
          </div>
          <div className="flex gap-3 flex-wrap">
            <button
              onClick={startBrowser}
              disabled={loading}
              className="bg-indigo-600 hover:bg-indigo-700 hover:scale-105 hover:shadow-lg text-white px-8 py-3 rounded-lg font-bold transition-all shadow-sm disabled:opacity-50 flex items-center gap-2"
            >
              {loading && status === "Idle" ? "Starting..." : "Start Browser"}
            </button>
            <button
              onClick={openNewTab}
              disabled={loading || status === "Idle"}
              className="bg-violet-600 hover:bg-violet-700 hover:scale-105 hover:shadow-lg text-white px-8 py-3 rounded-lg font-bold transition-all shadow-sm disabled:opacity-50 flex items-center gap-2"
            >
              + New Tab
            </button>
            <button
              onClick={generateAll}
              disabled={loading}
              className="bg-emerald-600 hover:bg-emerald-700 hover:scale-105 hover:shadow-lg text-white px-8 py-3 rounded-lg font-bold transition-all shadow-sm disabled:opacity-50"
            >
              Generate Test Case
            </button>
          </div>
        </header>

        {/* Active Tabs Strip */}
        {tabs.length > 0 && (
          <div className="flex items-center gap-3 overflow-x-auto pb-2">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-widest shrink-0">Open Tabs:</span>
            {tabs.map((tab) => (
              <div
                key={tab.index}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold border shrink-0 ${
                  tab.active
                    ? "bg-indigo-50 border-indigo-300 text-indigo-700"
                    : "bg-white border-slate-200 text-slate-600"
                }`}
              >
                <span className="w-5 h-5 bg-slate-100 text-slate-500 rounded flex items-center justify-center text-[10px] font-black">
                  {tab.index + 1}
                </span>
                <span className="truncate max-w-[200px]">{tab.title || tab.url}</span>
              </div>
            ))}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">
          {/* BDD Section */}
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-bold text-slate-700 flex items-center gap-2">
                <span className="w-6 h-6 bg-amber-100 text-amber-600 rounded flex items-center justify-center text-xs font-black">BDD</span>
                Gherkin Scenario
              </h2>
              {bddScenario && (
                <button
                  onClick={() => handleCopy(bddScenario, "bdd")}
                  className="text-xs font-bold bg-amber-100 hover:bg-amber-200 text-amber-700 px-3 py-1.5 rounded-lg transition-all"
                >
                  {bddCopied ? "Copied!" : "Copy"}
                </button>
              )}
            </div>
              <div className="bg-white border-2 border-slate-200 rounded-2xl overflow-hidden shadow-sm h-[75vh] flex flex-col relative">
              {bddScenario ? (
                <pre className="p-8 overflow-auto text-[15px] leading-loose font-mono text-slate-800 bg-amber-50/30 flex-1 whitespace-pre-wrap">
                  <code>{bddScenario}</code>
                </pre>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-slate-400 italic bg-slate-50">
                  <p>Start recording and click generate</p>
                </div>
              )}
            </div>
          </div>

          {/* Robot Section */}
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-bold text-slate-700 flex items-center gap-2">
                <span className="w-6 h-6 bg-blue-100 text-blue-600 rounded flex items-center justify-center text-xs font-black">RF</span>
                Robot Framework Script
              </h2>
              {robotScript && (
                <button
                  onClick={() => handleCopy(robotScript, "robot")}
                  className="text-xs font-bold bg-blue-100 hover:bg-blue-200 text-blue-700 px-3 py-1.5 rounded-lg transition-all"
                >
                  {robotCopied ? "Copied!" : "Copy"}
                </button>
              )}
            </div>
              <div className="bg-white border-2 border-slate-200 rounded-2xl overflow-hidden shadow-sm h-[75vh] flex flex-col relative">
              {robotScript ? (
                <pre className="p-8 overflow-auto text-[15px] leading-loose font-mono text-blue-900 bg-blue-50/20 flex-1 whitespace-pre-wrap">
                  <code>{robotScript}</code>
                </pre>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-slate-400 italic bg-slate-50">
                  <p>Robot script will appear here</p>
                </div>
              )}
            </div>
          </div>
        </div>

        <footer className="pt-6 border-t border-slate-200 flex justify-between items-center text-slate-400 text-xs font-bold uppercase tracking-widest">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${status === "Idle" ? "bg-slate-300" : "bg-green-500 animate-pulse"}`}></div>
            Status: <span className={status === "Idle" ? "text-slate-400" : "text-indigo-600"}>{status}</span>
          </div>
          <div>FastAPI Backend</div>
        </footer>
      </div>
    </main>
  );
}

