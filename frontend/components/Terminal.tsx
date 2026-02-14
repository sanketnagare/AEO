"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import TerminalLine from "./TerminalLine";
import { startAuditStream, type StreamEvent } from "@/lib/sse";

interface Line {
    id: number;
    text: string;
    type: "info" | "success" | "warning" | "error" | "progress" | "input" | "header" | "welcome" | "tip" | "bot" | "cta";
}

interface AuditScores {
    seo_score: number;
    aeo_score: number;
    geo_score: number;
    overall_score: number;
}

/* Welcome lines typed char-by-char */
const WELCOME_SEQUENCE: { text: string; type: Line["type"]; pauseAfter: number }[] = [
    { text: "🤖 AIVisibilityBot v0.1.0", type: "welcome", pauseAfter: 300 },
    { text: "Welcome! I'm your AI Visibility Auditor.", type: "info", pauseAfter: 200 },
    { text: "Enter your website URL below to get started:", type: "info", pauseAfter: 200 },
    { text: "I'll run 51+ automated checks across SEO, AEO & GEO in seconds.", type: "tip", pauseAfter: 0 },
];

/* ─── Queue item for the typewriter system ─── */
interface QueueItem {
    text: string;
    type: Line["type"];
    streamType: "instant" | "typing";
    isComplete?: boolean;
    completeData?: Record<string, unknown>;
}

/* Typing speed constants */
const TYPING_CHAR_SPEED = 12; // ms per character for typing messages
const INSTANT_LINE_DELAY = 60; // ms pause after each instant line for visual pacing

export default function Terminal() {
    const [lines, setLines] = useState<Line[]>([]);
    const [typingLineIndex, setTypingLineIndex] = useState(0);
    const [typingCharIndex, setTypingCharIndex] = useState(0);
    const [isBooting, setIsBooting] = useState(true);
    const [input, setInput] = useState("");
    const [isRunning, setIsRunning] = useState(false);
    const [isTyping, setIsTyping] = useState(false); // true while typewriter is processing queue
    const [scores, setScores] = useState<AuditScores | null>(null);
    const scrollRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    const lineIdRef = useRef(0);
    const cleanupRef = useRef<(() => void) | null>(null);

    // Typewriter queue
    const queueRef = useRef<QueueItem[]>([]);
    const isProcessingRef = useRef(false);
    const currentTypingTextRef = useRef<string>("");

    // Character-by-character typing effect for welcome
    useEffect(() => {
        if (!isBooting) return;
        if (typingLineIndex >= WELCOME_SEQUENCE.length) {
            const id = lineIdRef.current++;
            setLines((prev) => [...prev, { id, text: "", type: "info" }]);
            setIsBooting(false);
            setTimeout(() => inputRef.current?.focus(), 100);
            return;
        }

        const currentLine = WELCOME_SEQUENCE[typingLineIndex];
        const fullText = currentLine.text;

        if (typingCharIndex === 0) {
            const id = lineIdRef.current++;
            setLines((prev) => [...prev, { id, text: "", type: currentLine.type }]);
        }

        if (typingCharIndex < fullText.length) {
            const speed = 12 + Math.random() * 10;
            const timer = setTimeout(() => {
                setLines((prev) => {
                    const updated = [...prev];
                    const lastLine = updated[updated.length - 1];
                    updated[updated.length - 1] = {
                        ...lastLine,
                        text: fullText.slice(0, typingCharIndex + 1),
                    };
                    return updated;
                });
                setTypingCharIndex(typingCharIndex + 1);
            }, speed);
            return () => clearTimeout(timer);
        } else {
            const timer = setTimeout(() => {
                setTypingLineIndex(typingLineIndex + 1);
                setTypingCharIndex(0);
            }, currentLine.pauseAfter);
            return () => clearTimeout(timer);
        }
    }, [isBooting, typingLineIndex, typingCharIndex]);

    // Auto-scroll to bottom
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [lines]);

    const addLine = useCallback((text: string, type: Line["type"]) => {
        const id = lineIdRef.current++;
        setLines((prev) => [...prev, { id, text, type }]);
    }, []);

    /* ─── Typewriter Queue Processor ─── */
    const processQueue = useCallback(async () => {
        if (isProcessingRef.current) return;
        isProcessingRef.current = true;
        setIsTyping(true);

        while (queueRef.current.length > 0) {
            const item = queueRef.current.shift()!;

            // Handle completion event
            if (item.isComplete) {
                setIsRunning(false);
                if (item.completeData && typeof item.completeData === "object" && "scores" in item.completeData) {
                    const report = item.completeData as { scores: AuditScores };
                    setScores(report.scores);
                }
                addLine("", "info");
                // Removed prompt to type another URL as requested
                continue;
            }

            // Skip empty messages
            if (!item.text) continue;

            if (item.streamType === "typing") {
                // Character-by-character typewriter
                await typewriterLine(item.text, item.type);
            } else {
                // Instant display with small pause for visual pacing
                addLine(item.text, item.type);
                await sleep(INSTANT_LINE_DELAY);
            }
        }

        setIsTyping(false);
        isProcessingRef.current = false;
    }, [addLine]);

    const typewriterLine = useCallback(
        (fullText: string, type: Line["type"]) => {
            return new Promise<void>((resolve) => {
                const id = lineIdRef.current++;
                setLines((prev) => [...prev, { id, text: "", type }]);
                currentTypingTextRef.current = "";

                let charIdx = 0;
                const typeNext = () => {
                    if (charIdx < fullText.length) {
                        charIdx++;
                        const partialText = fullText.slice(0, charIdx);
                        currentTypingTextRef.current = partialText;
                        setLines((prev) => {
                            const updated = [...prev];
                            updated[updated.length - 1] = {
                                ...updated[updated.length - 1],
                                text: partialText,
                            };
                            return updated;
                        });
                        const speed = TYPING_CHAR_SPEED + Math.random() * 8;
                        setTimeout(typeNext, speed);
                    } else {
                        currentTypingTextRef.current = "";
                        resolve();
                    }
                };
                typeNext();
            });
        },
        []
    );

    const enqueueEvent = useCallback(
        (item: QueueItem) => {
            queueRef.current.push(item);
            // Start processing if not already running
            if (!isProcessingRef.current) {
                processQueue();
            }
        },
        [processQueue]
    );

    const handleSubmit = useCallback(
        (e: React.FormEvent) => {
            e.preventDefault();
            const raw = input.trim();
            if (!raw || isRunning || isBooting) return;

            setInput("");

            // Handle clear
            if (raw.toLowerCase() === "clear") {
                setLines([
                    { id: lineIdRef.current++, text: "🤖 AIVisibilityBot v0.1.0", type: "welcome" },
                    { id: lineIdRef.current++, text: "Terminal cleared. Ready for your next audit.", type: "info" },
                    { id: lineIdRef.current++, text: "", type: "info" },
                ]);
                setScores(null);
                queueRef.current = [];
                return;
            }

            // Validate URL
            let processedUrl = raw;
            if (!raw.startsWith("http://") && !raw.startsWith("https://")) {
                processedUrl = `https://${raw}`;
            }

            setIsRunning(true);
            setScores(null);

            addLine(`> audit ${processedUrl}`, "input");
            addLine("", "info");

            // Connect to SSE stream
            const cleanup = startAuditStream(processedUrl, {
                onEvent: (event: StreamEvent) => {
                    const typeMap: Record<string, Line["type"]> = {
                        info: "info",
                        success: "success",
                        warning: "warning",
                        error: "error",
                        progress: "progress",
                        cta: "cta",
                    };

                    // Determine the line type — bot messages that start with "❯ bot:" use "bot" type
                    let lineType = typeMap[event.type] || "info";
                    if (event.message.startsWith("❯ bot:")) {
                        lineType = "bot";
                    }

                    enqueueEvent({
                        text: event.message,
                        type: lineType,
                        streamType: event.stream_type || "instant",
                    });
                },
                onComplete: (data) => {
                    enqueueEvent({
                        text: "",
                        type: "info",
                        streamType: "instant",
                        isComplete: true,
                        completeData: data,
                    });
                },
                onError: (error) => {
                    addLine(`Error: ${error}`, "error");
                    addLine("Make sure the backend is running on http://localhost:8000", "error");
                    setIsRunning(false);
                },
            });

            cleanupRef.current = cleanup;
        },
        [input, isRunning, isBooting, addLine, enqueueEvent]
    );

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (cleanupRef.current) {
                cleanupRef.current();
            }
        };
    }, []);

    function getScoreColor(score: number): string {
        if (score >= 70) return "var(--terminal-green)";
        if (score >= 40) return "var(--terminal-amber)";
        return "var(--terminal-red)";
    }

    return (
        <div className="relative group w-full max-w-4xl mx-auto">
            {/* Outer Gradient Glow */}
            <div
                className="absolute -inset-1 rounded-2xl opacity-30 blur-xl transition duration-1000 group-hover:opacity-60 group-hover:duration-300"
                style={{ background: "linear-gradient(135deg, #3b82f6, #8b5cf6, #06b6d4)" }}
            />

            <div
                className="relative w-full rounded-2xl overflow-hidden z-10"
                style={{
                    background: "rgba(5, 8, 16, 0.97)",
                    backdropFilter: "blur(24px)",
                    border: "1px solid rgba(255, 255, 255, 0.08)",
                    boxShadow: "0 0 0 1px rgba(255,255,255,0.04), 0 4px 24px rgba(0,0,0,0.4), 0 24px 64px -16px rgba(0,0,0,0.6)",
                }}
            >
                {/* Terminal Header */}
                <div
                    className="flex items-center justify-between px-5 py-3 relative"
                    style={{
                        background: "linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)",
                    }}
                >
                    <div className="flex items-center gap-4">
                        <div className="flex gap-2">
                            <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#ff5f57", boxShadow: "0 0 6px rgba(255,95,87,0.4)" }} />
                            <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#febc2e", boxShadow: "0 0 6px rgba(254,188,46,0.4)" }} />
                            <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#28c840", boxShadow: "0 0 6px rgba(40,200,64,0.4)" }} />
                        </div>
                        <span
                            className="text-xs font-bold tracking-wide"
                            style={{
                                fontFamily: "'JetBrains Mono', monospace",
                                background: "linear-gradient(90deg, #e5e7eb, #9ca3af)",
                                WebkitBackgroundClip: "text",
                                WebkitTextFillColor: "transparent",
                            }}
                        >
                            AIVisibilityBot
                        </span>
                    </div>
                    <div className="flex items-center gap-3">
                        <span className="w-2 h-2 rounded-full animate-pulse" style={{ background: "var(--terminal-green)" }} />
                        <span
                            className="text-xs"
                            style={{ color: "var(--text-muted)", fontFamily: "'JetBrains Mono', monospace" }}
                        >
                            3 AI Engines Ready
                        </span>
                    </div>
                    {/* Header gradient beam */}
                    <div className="terminal-header-beam" />
                </div>

                {/* Terminal Body */}
                <div
                    ref={scrollRef}
                    className="terminal-scroll overflow-y-auto"
                    style={{ maxHeight: "600px", minHeight: "400px", padding: "28px 32px" }}
                    onClick={() => inputRef.current?.focus()}
                >
                    {/* Lines */}
                    {lines.map((line) => (
                        <TerminalLine key={line.id} text={line.text} type={line.type} />
                    ))}

                    {/* Blinking cursor while typing welcome or processing queue */}
                    {(isBooting || isTyping) && (
                        <span
                            className="cursor-blink inline-block"
                            style={{
                                color: "var(--terminal-green)",
                                fontFamily: "'JetBrains Mono', monospace",
                                fontSize: "14px",
                            }}
                        >
                            ▋
                        </span>
                    )}

                    {/* Score Summary Box */}
                    {scores && (
                        <div
                            className="mt-6 mb-4 p-4 rounded-lg score-glow relative overflow-hidden"
                            style={{
                                border: "1px solid rgba(88, 166, 255, 0.2)",
                                background: "rgba(30, 37, 51, 0.4)",
                                fontFamily: "'JetBrains Mono', monospace",
                                fontSize: "13px",
                            }}
                        >
                            <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500 rounded-full blur-[60px] opacity-10 pointer-events-none" />
                            <div className="flex flex-wrap gap-8 justify-center relative z-10">
                                <div className="text-center group">
                                    <div className="text-xs mb-1 uppercase tracking-wider transition-colors group-hover:text-white" style={{ color: "var(--text-secondary)" }}>SEO</div>
                                    <div className="text-2xl font-bold transition-transform group-hover:scale-110" style={{ color: getScoreColor(scores.seo_score) }}>
                                        {scores.seo_score}
                                    </div>
                                </div>
                                <div className="text-center group">
                                    <div className="text-xs mb-1 uppercase tracking-wider transition-colors group-hover:text-white" style={{ color: "var(--text-secondary)" }}>AEO</div>
                                    <div className="text-2xl font-bold transition-transform group-hover:scale-110" style={{ color: getScoreColor(scores.aeo_score) }}>
                                        {scores.aeo_score}
                                    </div>
                                </div>
                                <div className="text-center group">
                                    <div className="text-xs mb-1 uppercase tracking-wider transition-colors group-hover:text-white" style={{ color: "var(--text-secondary)" }}>GEO</div>
                                    <div className="text-2xl font-bold transition-transform group-hover:scale-110" style={{ color: getScoreColor(scores.geo_score) }}>
                                        {scores.geo_score}
                                    </div>
                                </div>
                                <div className="text-center pl-8 ml-2" style={{ borderLeft: "1px solid rgba(255,255,255,0.1)" }}>
                                    <div className="text-xs mb-1 uppercase tracking-wider" style={{ color: "var(--accent)" }}>OVERALL</div>
                                    <div className="text-2xl font-bold" style={{ color: getScoreColor(scores.overall_score) }}>
                                        {scores.overall_score}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Input Line */}
                    {!isBooting && !scores && (
                        <form onSubmit={handleSubmit} className="terminal-input-row flex items-center mt-2 group">
                            <span className="mr-2" style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: "14px" }}>
                                <span style={{ fontSize: "14px" }}>🤖</span>
                                <span style={{ color: "var(--terminal-prompt)", fontWeight: 600, marginLeft: 4 }}>{">"}</span>
                            </span>
                            <input
                                ref={inputRef}
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                disabled={isRunning}
                                placeholder={isRunning ? "Auditing..." : "Enter URL to audit..."}
                                className="flex-1 bg-transparent outline-none border-none placeholder-gray-600"
                                style={{
                                    color: "var(--terminal-text)",
                                    fontFamily: "'JetBrains Mono', monospace",
                                    fontSize: "14px",
                                    caretColor: "var(--terminal-green)",
                                }}
                                autoFocus
                            />
                            {!isRunning && !isTyping && (
                                <span className="cursor-blink ml-1" style={{ color: "var(--terminal-green)", fontFamily: "'JetBrains Mono', monospace", fontSize: "14px" }}>▋</span>
                            )}
                            {(isRunning || isTyping) && (
                                <span className="thinking-dots ml-2 flex items-center gap-[2px]">
                                    <span /><span /><span />
                                </span>
                            )}
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
}

/* Utility: sleep */
function sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
}
