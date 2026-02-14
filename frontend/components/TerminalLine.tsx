"use client";

import React from "react";
import TerminalLoginCard from "./TerminalLoginCard";

interface TerminalLineProps {
    text: string;
    type: "info" | "success" | "warning" | "error" | "progress" | "input" | "header" | "welcome" | "tip" | "bot" | "cta";
    animated?: boolean;
}

const typeStyles: Record<string, string> = {
    info: "var(--terminal-text)",
    success: "var(--terminal-green)",
    warning: "var(--terminal-amber)",
    error: "var(--terminal-red)",
    progress: "var(--terminal-cyan)",
    input: "var(--terminal-prompt)",
    header: "var(--terminal-purple)",
    welcome: "var(--terminal-green)",
    tip: "var(--terminal-cyan)",
    bot: "var(--terminal-text)",
    cta: "var(--terminal-blue)",
};

const typeIcons: Record<string, string> = {
    success: "✓",
    warning: "⚠️",
    error: "❌",
    progress: "$",
    tip: "💡",
};

export default function TerminalLine({ text, type, animated = true }: TerminalLineProps) {
    // Don't add icon if text already has one
    const hasIcon = text.startsWith("✓") || text.startsWith("❌") || text.startsWith("⚠️") ||
        text.startsWith("🔴") || text.startsWith("$") || text.startsWith(">") ||
        text.startsWith("  ") || text.startsWith("💡") || text.startsWith("❯");

    const displayText = hasIcon ? text : (typeIcons[type] ? `${typeIcons[type]} ${text}` : text);

    // Welcome type gets gradient text
    if (type === "welcome") {
        return (
            <div
                className="terminal-line-enter py-[2px] leading-relaxed whitespace-pre-wrap break-words"
                style={{
                    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                    fontSize: "14px",
                    fontWeight: 700,
                    background: "linear-gradient(90deg, #7fd962, #39bae6, #c792ea)",
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                }}
            >
                {displayText}
            </div>
        );
    }

    // Tip type gets subtle background
    if (type === "tip") {
        return (
            <div
                className="terminal-line-enter py-[2px] leading-relaxed whitespace-pre-wrap break-words"
                style={{
                    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                    fontSize: "13px",
                    color: typeStyles[type],
                    padding: "4px 8px",
                    borderRadius: 6,
                    background: "rgba(57, 186, 230, 0.06)",
                    borderLeft: "2px solid rgba(57, 186, 230, 0.3)",
                    marginTop: 4,
                    marginBottom: 4,
                }}
            >
                {displayText}
            </div>
        );
    }

    // Bot messages — render "❯ bot:" prefix in special color
    if (type === "bot" || displayText.startsWith("❯ bot:")) {
        const prefixEnd = displayText.indexOf(":");
        const prefix = displayText.slice(0, prefixEnd + 1);
        const rest = displayText.slice(prefixEnd + 1);

        return (
            <div
                className="terminal-line-enter py-[3px] leading-relaxed whitespace-pre-wrap break-words"
                style={{
                    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                    fontSize: "14px",
                }}
            >
                <span style={{ color: "#ff9e64", fontWeight: 600 }}>{prefix}</span>
                <span style={{ color: "var(--terminal-text)" }}>{rest}</span>
            </div>
        );
    }

    // Call to Action (CTA) — Urgency Message + Login Card
    if (type === "cta") {
        return (
            <div className="terminal-line-enter mt-8 mb-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
                {/* Urgency Message and Login Card Container */}
                <div className="mb-6 px-4">
                    <div className="flex items-start gap-3 text-amber-500/90 mb-6">
                        <span className="text-xl mt-0.5">⚠️</span>
                        <div>
                            <p className="font-mono text-sm font-bold tracking-wide uppercase text-amber-500">
                                CRITICAL ACTION REQUIRED
                            </p>
                            <p className="font-mono text-sm text-gray-300 mt-1 leading-relaxed">
                                To see detailed analysis and get on-point fixes, please sign in.
                                <span className="text-red-400 font-bold ml-1">Your site is at risk.</span>
                            </p>
                        </div>
                    </div>

                    {/* Login Card */}
                    <div className="flex justify-center w-full">
                        <TerminalLoginCard />
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div
            className={`terminal-line-enter py-[2px] leading-relaxed whitespace-pre-wrap break-words`}
            style={{
                ...(typeStyles[type] ? { color: typeStyles[type] } : {}),
                fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                fontSize: "14px",
            }}
        >
            {displayText}
        </div>
    );
}
