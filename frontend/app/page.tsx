"use client";

import { useState, useEffect } from "react";
import Terminal from "@/components/Terminal";

/* ── Data ─────────────────────────────────────────── */

const ROTATING_WORDS = ["ChatGPT", "Perplexity", "Gemini", "AI Search"];

const STEPS = [
  { n: "01", icon: "🌐", title: "Enter Your URL", text: "Paste any URL into the terminal below. Instant results." },
  { n: "02", icon: "⚙️", title: "AI Runs the Audit", text: "51+ checks across SEO, AEO & GEO execute in seconds." },
  { n: "03", icon: "📋", title: "Get Your Report", text: "Actionable scores and recommendations, instantly." },
];

const FEATURES = [
  { icon: "🔍", title: "51+ Automated Checks", text: "Comprehensive audit across SEO, AEO, and GEO in one scan." },
  { icon: "🤖", title: "AI Citation Tracking", text: "See how ChatGPT, Perplexity, and Gemini reference your site." },
  { icon: "📊", title: "Content Gap Analysis", text: "Discover what questions AI answers that you're not." },
  { icon: "⚡", title: "Schema Generation", text: "Auto-generate structured data to boost AI discoverability." },
  { icon: "🏆", title: "Competitor Intelligence", text: "Benchmark your AI visibility against competitors." },
  { icon: "📈", title: "Weekly Reports", text: "Track visibility trends and improvements over time." },
];

const STATS = [
  { value: "27", label: "SEO Checks", color: "#4ade80" },
  { value: "12", label: "AEO Checks", color: "#38bdf8" },
  { value: "12", label: "GEO Checks", color: "#c084fc" },
  { value: "3", label: "AI Engines", color: "#22d3ee" },
];

const TICKER = [
  "SEO", "AEO", "GEO", "ChatGPT", "Perplexity", "Gemini",
  "Schema.org", "Structured Data", "Core Web Vitals", "Featured Snippets",
  "AI Citations", "Content Optimization",
];

/* ── Component ────────────────────────────────────── */

export default function Home() {
  const [wordIdx, setWordIdx] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setWordIdx((i) => (i + 1) % ROTATING_WORDS.length), 2800);
    return () => clearInterval(t);
  }, []);

  const scrollToTerminal = () => {
    document.getElementById("audit")?.scrollIntoView({ behavior: "smooth" });
    setTimeout(() => document.querySelector("input")?.focus(), 500);
  };

  return (
    <div className="stars-bg" style={{ minHeight: "100vh", position: "relative", overflow: "hidden" }}>

      {/* ───── NAV ───── */}
      <header style={{ position: "fixed", top: 24, left: "50%", transform: "translateX(-50%)", zIndex: 50 }}>
        <nav
          aria-label="Main navigation"
          style={{
            display: "flex", alignItems: "center", gap: 24,
            padding: "10px 20px", borderRadius: 9999,
            background: "rgba(5,5,10,0.7)", backdropFilter: "blur(16px)",
            border: "1px solid rgba(255,255,255,0.08)",
            boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
            whiteSpace: "nowrap",
          }}
        >
          <a href="#" style={{ display: "flex", alignItems: "center", gap: 8, textDecoration: "none", flexShrink: 0 }}>
            <div style={{
              width: 28, height: 28, borderRadius: 6, display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: 11, fontWeight: 900, background: "linear-gradient(135deg,#3b82f6,#22d3ee)", color: "#000",
            }}>AI</div>
            <span style={{ fontWeight: 700, fontSize: 14, color: "#e5e7eb", letterSpacing: "-0.01em" }}>AIVisibilityBot</span>
          </a>

          <div style={{ display: "flex", gap: 4, flexShrink: 0 }}>
            {["Why It Matters", "How It Works", "Features"].map((l) => (
              <a
                key={l}
                href={`#${l.toLowerCase().replace(/\s+/g, "-")}`}
                style={{
                  padding: "6px 12px", fontSize: 12, fontWeight: 500, color: "#9ca3af",
                  borderRadius: 9999, textDecoration: "none", transition: "color 0.2s",
                  whiteSpace: "nowrap",
                }}
                onMouseEnter={(e) => (e.currentTarget.style.color = "#fff")}
                onMouseLeave={(e) => (e.currentTarget.style.color = "#9ca3af")}
              >{l}</a>
            ))}
          </div>

          <div style={{ width: 1, height: 16, background: "rgba(255,255,255,0.08)", flexShrink: 0 }} />

          <button
            onClick={scrollToTerminal}
            style={{
              fontSize: 12, fontWeight: 700, padding: "6px 16px", borderRadius: 9999, border: "none",
              background: "#fff", color: "#000", cursor: "pointer",
              boxShadow: "0 0 20px rgba(255,255,255,0.15)",
              transition: "transform 0.2s, box-shadow 0.2s",
              whiteSpace: "nowrap", flexShrink: 0,
            }}
            onMouseEnter={(e) => { e.currentTarget.style.transform = "scale(1.05)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.transform = "scale(1)"; }}
          >Get Started</button>
        </nav>
      </header>

      <main>

        {/* ───── HERO ───── */}
        <section
          id="hero"
          style={{
            maxWidth: 900, margin: "0 auto", padding: "120px 24px 48px",
            textAlign: "center", position: "relative", zIndex: 10,
          }}
        >
          {/* Badge */}
          <div className="animate-section" style={{
            display: "inline-flex", alignItems: "center", gap: 8,
            padding: "6px 16px", borderRadius: 9999, fontSize: 12, fontWeight: 500,
            border: "1px solid rgba(59,130,246,0.2)", background: "rgba(59,130,246,0.06)",
            color: "#93c5fd", marginBottom: 32,
          }}>
            <span style={{
              width: 8, height: 8, borderRadius: "50%", background: "#3b82f6",
              boxShadow: "0 0 8px rgba(59,130,246,0.6)",
            }} />
            AI-Powered Audit Engine
          </div>

          {/* H1 */}
          <h1 className="animate-section delay-1" style={{
            fontSize: "clamp(32px, 4.5vw, 52px)", fontWeight: 900,
            lineHeight: 1.15, letterSpacing: "-0.03em", marginBottom: 40,
          }}>
            <span style={{
              display: "block",
              background: "linear-gradient(180deg, #ffffff 0%, #6b7280 100%)",
              WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
            }}>
              Is Your Brand Visible to
            </span>
            <span style={{ position: "relative", display: "inline-block", height: "1.3em", overflow: "hidden" }}>
              {ROTATING_WORDS.map((w, i) => (
                <span
                  key={w}
                  style={{
                    position: i === 0 ? "relative" : "absolute",
                    left: 0, right: 0,
                    visibility: i === wordIdx ? "visible" : "hidden",
                    opacity: i === wordIdx ? 1 : 0,
                    transform: i === wordIdx ? "translateY(0)" : "translateY(12px)",
                    transition: "opacity 0.45s, transform 0.45s",
                    background: i === 0 ? "linear-gradient(90deg,#4ade80,#22d3ee)"
                      : i === 1 ? "linear-gradient(90deg,#3b82f6,#06b6d4)"
                        : i === 2 ? "linear-gradient(90deg,#a78bfa,#ec4899)"
                          : "linear-gradient(90deg,#fbbf24,#f97316)",
                    WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
                  }}
                >{w}?</span>
              ))}
            </span>
          </h1>

          {/* Subtitle */}
          <p className="animate-section delay-2" style={{
            fontSize: "clamp(16px, 2.5vw, 20px)", color: "#9ca3af",
            maxWidth: 600, margin: "0 auto 40px", lineHeight: 1.7, fontWeight: 300,
          }}>
            Run <strong style={{ color: "#e5e7eb", fontWeight: 600 }}>51+ automated checks</strong> across
            SEO, AEO, and GEO. See how AI engines understand your site and what to fix.
          </p>

          {/* Stat pills */}
          <div className="animate-section delay-3" style={{
            display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 12, marginBottom: 0,
          }}>
            {[
              { icon: "✓", label: "51+ Checks" },
              { icon: "⚡", label: "3 AI Engines" },
              { icon: "📊", label: "Real-Time Results" },
            ].map((p) => (
              <div key={p.label} style={{
                display: "flex", alignItems: "center", gap: 8,
                padding: "8px 16px", borderRadius: 9999, fontSize: 13, fontWeight: 500,
                color: "#d1d5db",
                background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.06)",
              }}>
                <span style={{ fontSize: 11 }}>{p.icon}</span>
                {p.label}
              </div>
            ))}
          </div>
        </section>

        {/* ───── TERMINAL ───── */}
        <section
          id="audit"
          aria-label="Live audit terminal"
          style={{
            maxWidth: 960, margin: "0 auto", padding: "0 24px 120px",
            position: "relative", zIndex: 20,
          }}
        >
          <div className="animate-section delay-4">
            <Terminal />
          </div>
          {/* Glow */}
          <div style={{
            position: "absolute", top: "50%", left: "50%",
            transform: "translate(-50%,-50%)", width: "70%", height: "70%",
            background: "radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 70%)",
            borderRadius: "50%", zIndex: -1, pointerEvents: "none",
          }} />
        </section>

        {/* ───── TICKER ───── */}
        <div style={{
          borderTop: "1px solid rgba(255,255,255,0.04)",
          borderBottom: "1px solid rgba(255,255,255,0.04)",
          padding: "20px 0", overflow: "hidden", marginBottom: 120,
          position: "relative", zIndex: 10,
        }}>
          <div className="ticker-move">
            {[...TICKER, ...TICKER].map((t, i) => (
              <span key={i} style={{
                display: "inline-flex", alignItems: "center",
              }}>
                <span style={{
                  fontSize: 12, fontWeight: 600, color: "#374151",
                  textTransform: "uppercase", letterSpacing: "0.15em",
                  whiteSpace: "nowrap",
                }}>{t}</span>
                <span style={{
                  width: 4, height: 4, borderRadius: "50%", background: "#1f2937",
                  flexShrink: 0, margin: "0 24px",
                }} />
              </span>
            ))}
          </div>
        </div>

        {/* ───── WHY IT MATTERS TABLE ───── */}
        <section
          id="why-it-matters"
          aria-label="Why SEO AEO GEO matter"
          style={{ maxWidth: 1100, margin: "0 auto", padding: "0 24px 120px", position: "relative", zIndex: 10 }}
        >
          <div style={{ textAlign: "center", marginBottom: 48 }}>
            <span style={{
              display: "inline-block", fontSize: 11, fontWeight: 700,
              textTransform: "uppercase", letterSpacing: "0.2em", color: "#f59e0b", marginBottom: 12,
            }}>⚠️ Why It Matters</span>
            <h2 style={{
              fontSize: "clamp(28px, 4vw, 44px)", fontWeight: 800, letterSpacing: "-0.02em",
              marginBottom: 12,
              background: "linear-gradient(180deg,#fff 30%,#6b7280 100%)",
              WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
            }}>Search Is Changing. Are You Ready?</h2>
            <p style={{ fontSize: 15, color: "#6b7280", maxWidth: 580, margin: "0 auto" }}>
              40% of Gen Z already uses AI instead of Google. Your competitors are optimizing
              for these new engines. Every day you wait, you lose visibility.
            </p>
          </div>

          {/* Table */}
          <div style={{ overflowX: "auto" }}>
            <table style={{
              width: "100%", borderCollapse: "separate", borderSpacing: 0,
              background: "rgba(255,255,255,0.02)", borderRadius: 16,
              border: "1px solid rgba(255,255,255,0.06)", overflow: "hidden",
            }}>
              <thead>
                <tr>
                  {["Type", "What It Is", "Why You Need It", "Risk If Ignored"].map((h) => (
                    <th key={h} style={{
                      padding: "16px 20px", textAlign: "left", fontSize: 11, fontWeight: 700,
                      textTransform: "uppercase", letterSpacing: "0.15em", color: "#6b7280",
                      borderBottom: "1px solid rgba(255,255,255,0.06)",
                      background: "rgba(255,255,255,0.03)",
                    }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[
                  {
                    type: "SEO", color: "#4ade80",
                    what: "Search Engine Optimization",
                    why: "Rank on Google, Bing, and traditional search engines. The foundation of all online visibility.",
                    risk: "You disappear from search results. Competitors take your traffic.",
                  },
                  {
                    type: "AEO", color: "#38bdf8",
                    what: "Answer Engine Optimization",
                    why: "Get featured in AI-generated answers, snippets, and voice search results.",
                    risk: "AI assistants cite your competitors instead of you. Lost authority.",
                  },
                  {
                    type: "GEO", color: "#c084fc",
                    what: "Generative Engine Optimization",
                    why: "Be cited by ChatGPT, Perplexity, Gemini when users ask questions about your industry.",
                    risk: "You become invisible in the fastest-growing search channel.",
                  },
                ].map((row, i) => (
                  <tr key={row.type} style={{
                    borderBottom: i < 2 ? "1px solid rgba(255,255,255,0.04)" : "none",
                  }}>
                    <td style={{ padding: "20px", verticalAlign: "top" }}>
                      <span style={{
                        display: "inline-block", padding: "4px 12px", borderRadius: 8,
                        fontSize: 13, fontWeight: 800, color: row.color,
                        background: `${row.color}15`, letterSpacing: "0.05em",
                      }}>{row.type}</span>
                    </td>
                    <td style={{ padding: "20px", fontSize: 14, color: "#d1d5db", verticalAlign: "top", lineHeight: 1.5 }}>
                      {row.what}
                    </td>
                    <td style={{ padding: "20px", fontSize: 14, color: "#9ca3af", verticalAlign: "top", lineHeight: 1.5 }}>
                      {row.why}
                    </td>
                    <td style={{ padding: "20px", fontSize: 14, color: "#ef4444", verticalAlign: "top", lineHeight: 1.5, fontWeight: 500 }}>
                      {row.risk}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Urgency callout */}
          <div style={{
            marginTop: 32, textAlign: "center", padding: "20px 24px", borderRadius: 12,
            background: "rgba(245,158,11,0.06)", border: "1px solid rgba(245,158,11,0.15)",
          }}>
            <p style={{ fontSize: 14, color: "#fbbf24", fontWeight: 600 }}>
              ⚠️ Companies optimizing for AI today will dominate search tomorrow. Don&apos;t get left behind.
            </p>
          </div>
        </section>

        {/* ───── HOW IT WORKS ───── */}
        <section
          id="how-it-works"
          aria-label="How it works"
          style={{ maxWidth: 1100, margin: "0 auto", padding: "0 24px 120px", position: "relative", zIndex: 10 }}
        >
          <div style={{ textAlign: "center", marginBottom: 64 }}>
            <span style={{
              display: "inline-block", fontSize: 11, fontWeight: 700,
              textTransform: "uppercase", letterSpacing: "0.2em", color: "#3b82f6", marginBottom: 12,
            }}>How It Works</span>
            <h2 style={{
              fontSize: "clamp(28px, 4vw, 44px)", fontWeight: 800, letterSpacing: "-0.02em",
              background: "linear-gradient(180deg,#fff 30%,#6b7280 100%)",
              WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
            }}>Three Steps to AI Visibility</h2>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 24 }}>
            {STEPS.map((s) => (
              <div key={s.n} className="glass-card" style={{ padding: 32, textAlign: "center" }}>
                <div style={{ fontSize: 36, marginBottom: 16 }}>{s.icon}</div>
                <div style={{
                  fontSize: 11, fontWeight: 700, color: "rgba(59,130,246,0.5)",
                  textTransform: "uppercase", letterSpacing: "0.2em", marginBottom: 8,
                }}>Step {s.n}</div>
                <h3 style={{ fontSize: 20, fontWeight: 700, color: "#f3f4f6", marginBottom: 8 }}>{s.title}</h3>
                <p style={{ fontSize: 14, color: "#6b7280", lineHeight: 1.6 }}>{s.text}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ───── FEATURES ───── */}
        <section
          id="features"
          aria-label="Features"
          style={{ maxWidth: 1100, margin: "0 auto", padding: "0 24px 120px", position: "relative", zIndex: 10 }}
        >
          <div style={{ textAlign: "center", marginBottom: 64 }}>
            <span style={{
              display: "inline-block", fontSize: 11, fontWeight: 700,
              textTransform: "uppercase", letterSpacing: "0.2em", color: "#a78bfa", marginBottom: 12,
            }}>Features</span>
            <h2 style={{
              fontSize: "clamp(28px, 4vw, 44px)", fontWeight: 800, letterSpacing: "-0.02em",
              marginBottom: 12,
              background: "linear-gradient(180deg,#fff 30%,#6b7280 100%)",
              WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
            }}>Everything You Need for AI Visibility</h2>
            <p style={{ fontSize: 15, color: "#6b7280", maxWidth: 520, margin: "0 auto" }}>
              Traditional SEO is no longer enough. Optimize for the AI engines that are reshaping search.
            </p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 20 }}>
            {FEATURES.map((f) => (
              <div key={f.title} className="glass-card" style={{ padding: 28, textAlign: "center" }}>
                <div style={{ fontSize: 32, marginBottom: 14 }}>{f.icon}</div>
                <h3 style={{ fontSize: 17, fontWeight: 700, color: "#f3f4f6", marginBottom: 6 }}>{f.title}</h3>
                <p style={{ fontSize: 13, color: "#6b7280", lineHeight: 1.6 }}>{f.text}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ───── STATS ───── */}
        <section
          id="stats"
          aria-label="Audit statistics"
          style={{ maxWidth: 900, margin: "0 auto", padding: "0 24px 120px", position: "relative", zIndex: 10 }}
        >
          <div className="glass-card" style={{ padding: "56px 32px", textAlign: "center" }}>
            <div style={{
              display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 24,
            }}>
              {STATS.map((s) => (
                <div key={s.label}>
                  <div style={{ fontSize: 48, fontWeight: 900, color: s.color, lineHeight: 1, marginBottom: 8 }}>
                    {s.value}
                  </div>
                  <div style={{
                    fontSize: 11, fontWeight: 700, textTransform: "uppercase",
                    letterSpacing: "0.15em", color: "#6b7280",
                  }}>{s.label}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ───── CTA ───── */}
        <section
          aria-label="Call to action"
          style={{ maxWidth: 800, margin: "0 auto", padding: "0 24px 120px", position: "relative", zIndex: 10 }}
        >
          <div style={{
            textAlign: "center", padding: "64px 32px", borderRadius: 24,
            border: "1px solid rgba(255,255,255,0.06)",
            background: "linear-gradient(180deg, rgba(59,130,246,0.06) 0%, rgba(139,92,246,0.03) 100%)",
            position: "relative", overflow: "hidden",
          }}>
            {/* Glow */}
            <div style={{
              position: "absolute", top: -40, left: "50%", transform: "translateX(-50%)",
              width: 400, height: 120, background: "radial-gradient(circle, rgba(59,130,246,0.12),transparent 70%)",
              borderRadius: "50%", pointerEvents: "none",
            }} />

            <h2 style={{
              fontSize: "clamp(26px, 4vw, 40px)", fontWeight: 900, marginBottom: 16,
              background: "linear-gradient(180deg,#fff,#9ca3af)",
              WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
              position: "relative", zIndex: 1,
            }}>Ready to Get Cited by AI?</h2>

            <p style={{
              fontSize: 15, color: "#6b7280", maxWidth: 460, margin: "0 auto 32px",
              position: "relative", zIndex: 1,
            }}>
              Paste your URL above and discover how AI engines see your brand, with
              actionable recommendations.
            </p>

            <div style={{ position: "relative", zIndex: 1, display: "inline-block" }}>
              <button
                onClick={scrollToTerminal}
                style={{
                  fontSize: 16, fontWeight: 700, padding: "14px 32px", borderRadius: 9999,
                  border: "none", cursor: "pointer", color: "#fff",
                  background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
                  boxShadow: "0 0 30px rgba(59,130,246,0.3)",
                  transition: "transform 0.2s, box-shadow 0.2s",
                  display: "flex", alignItems: "center", gap: 8,
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "scale(1.05)";
                  e.currentTarget.style.boxShadow = "0 0 40px rgba(59,130,246,0.5)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "scale(1)";
                  e.currentTarget.style.boxShadow = "0 0 30px rgba(59,130,246,0.3)";
                }}
              >
                Start Your Audit
                <span style={{ opacity: 0.7 }}>→</span>
              </button>
            </div>
          </div>
        </section>
      </main>

      {/* ───── FOOTER ───── */}
      <footer style={{
        borderTop: "1px solid rgba(255,255,255,0.04)",
        background: "rgba(0,0,0,0.5)", backdropFilter: "blur(20px)",
        position: "relative", zIndex: 20,
      }}>
        <div style={{ maxWidth: 1100, margin: "0 auto", padding: "64px 24px" }}>
          <div style={{
            display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: 48, marginBottom: 48,
          }}>
            {/* Brand */}
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                <div style={{
                  width: 28, height: 28, borderRadius: 6, display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 11, fontWeight: 900, background: "linear-gradient(135deg,#3b82f6,#22d3ee)", color: "#000",
                }}>AI</div>
                <span style={{ fontWeight: 700, fontSize: 14, color: "#e5e7eb" }}>AIVisibilityBot</span>
              </div>
              <p style={{ fontSize: 13, color: "#4b5563", lineHeight: 1.7, maxWidth: 280 }}>
                The world&apos;s first autonomous AEO + GEO + SEO audit engine.
              </p>
            </div>

            {/* Product */}
            <div>
              <h4 style={{
                fontSize: 11, fontWeight: 700, textTransform: "uppercase",
                letterSpacing: "0.15em", color: "#6b7280", marginBottom: 16,
              }}>Product</h4>
              <ul style={{ listStyle: "none", padding: 0, display: "flex", flexDirection: "column", gap: 10 }}>
                {["Features", "How It Works", "Stats"].map((l) => (
                  <li key={l}>
                    <a
                      href={`#${l.toLowerCase().replace(/\s+/g, "-")}`}
                      style={{ fontSize: 13, color: "#4b5563", textDecoration: "none", transition: "color 0.2s" }}
                      onMouseEnter={(e) => (e.currentTarget.style.color = "#fff")}
                      onMouseLeave={(e) => (e.currentTarget.style.color = "#4b5563")}
                    >{l}</a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Company */}
            <div>
              <h4 style={{
                fontSize: 11, fontWeight: 700, textTransform: "uppercase",
                letterSpacing: "0.15em", color: "#6b7280", marginBottom: 16,
              }}>Company</h4>
              <ul style={{ listStyle: "none", padding: 0, display: "flex", flexDirection: "column", gap: 10 }}>
                {["Twitter", "GitHub", "Terms"].map((l) => (
                  <li key={l}>
                    <a
                      href="#"
                      style={{ fontSize: 13, color: "#4b5563", textDecoration: "none", transition: "color 0.2s" }}
                      onMouseEnter={(e) => (e.currentTarget.style.color = "#fff")}
                      onMouseLeave={(e) => (e.currentTarget.style.color = "#4b5563")}
                    >{l}</a>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Bottom */}
          <div style={{
            borderTop: "1px solid rgba(255,255,255,0.04)", paddingTop: 24,
            display: "flex", flexWrap: "wrap", justifyContent: "space-between", alignItems: "center", gap: 12,
          }}>
            <span style={{ fontSize: 12, color: "#374151" }}>
              © 2026 AIVisibilityBot. The future of search is conversational.
            </span>
            <span style={{ fontSize: 12, color: "#374151" }}>
              Built for the AI era.
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
