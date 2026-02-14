"use client";

import { useState, useEffect } from "react";

export default function Navbar() {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 20);
        };
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    const scrollToTerminal = () => {
        document.getElementById("audit")?.scrollIntoView({ behavior: "smooth" });
        setTimeout(() => document.querySelector("input")?.focus(), 500);
        setIsMenuOpen(false);
    };

    const scrollToSection = (id: string) => {
        // Prevent default anchor behavior and scroll smoothly
        const element = document.getElementById(id);
        if (element) {
            element.scrollIntoView({ behavior: "smooth" });
            setIsMenuOpen(false);
        }
    };

    // Prevent scrolling when menu is open
    useEffect(() => {
        if (isMenuOpen) {
            document.body.style.overflow = "hidden";
        } else {
            document.body.style.overflow = "unset";
        }
        return () => {
            document.body.style.overflow = "unset";
        };
    }, [isMenuOpen]);

    const LINKS = [
        { label: "Why It Matters", id: "why-it-matters" },
        { label: "How It Works", id: "how-it-works" },
        { label: "Features", id: "features" },
    ];

    return (
        <>
            <header
                style={{
                    position: "fixed",
                    top: 24,
                    left: "50%",
                    transform: "translateX(-50%)",
                    zIndex: 50,
                    width: "90%",
                    maxWidth: "1000px",
                }}
                className="transition-all duration-300"
            >
                <nav
                    aria-label="Main navigation"
                    style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        padding: "10px 20px",
                        borderRadius: 9999,
                        background: "rgba(5,5,10,0.7)",
                        backdropFilter: "blur(16px)",
                        border: "1px solid rgba(255,255,255,0.08)",
                        boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
                    }}
                >
                    {/* Logo */}
                    <a
                        href="#"
                        onClick={(e) => {
                            e.preventDefault();
                            window.scrollTo({ top: 0, behavior: "smooth" });
                        }}
                        style={{
                            display: "flex",
                            alignItems: "center",
                            gap: 8,
                            textDecoration: "none",
                            flexShrink: 0,
                        }}
                    >
                        <div
                            style={{
                                width: 28,
                                height: 28,
                                borderRadius: 6,
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                fontSize: 11,
                                fontWeight: 900,
                                background: "linear-gradient(135deg,#3b82f6,#22d3ee)",
                                color: "#000",
                            }}
                        >
                            AI
                        </div>
                        <span
                            style={{
                                fontWeight: 700,
                                fontSize: 14,
                                color: "#e5e7eb",
                                letterSpacing: "-0.01em",
                            }}
                        >
                            AIVisibilityBot
                        </span>
                    </a>

                    {/* Desktop Links */}
                    <div className="hidden md:flex items-center gap-4 flex-shrink-0">
                        {LINKS.map((link) => (
                            <button
                                key={link.label}
                                onClick={() => scrollToSection(link.id)}
                                style={{
                                    padding: "6px 12px",
                                    fontSize: 12,
                                    fontWeight: 500,
                                    color: "#9ca3af",
                                    borderRadius: 9999,
                                    background: "transparent",
                                    border: "none",
                                    cursor: "pointer",
                                    whiteSpace: "nowrap",
                                    transition: "color 0.2s",
                                }}
                                onMouseEnter={(e) => (e.currentTarget.style.color = "#fff")}
                                onMouseLeave={(e) => (e.currentTarget.style.color = "#9ca3af")}
                            >
                                {link.label}
                            </button>
                        ))}

                        <div
                            style={{
                                width: 1,
                                height: 16,
                                background: "rgba(255,255,255,0.08)",
                                margin: "0 4px",
                            }}
                        />

                        <button
                            onClick={scrollToTerminal}
                            style={{
                                fontSize: 12,
                                fontWeight: 700,
                                padding: "6px 16px",
                                borderRadius: 9999,
                                border: "none",
                                background: "#fff",
                                color: "#000",
                                cursor: "pointer",
                                boxShadow: "0 0 20px rgba(255,255,255,0.15)",
                                transition: "transform 0.2s, box-shadow 0.2s",
                                whiteSpace: "nowrap",
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.transform = "scale(1.05)";
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.transform = "scale(1)";
                            }}
                        >
                            Get Started
                        </button>
                    </div>

                    {/* Mobile Menu Button */}
                    <button
                        className="md:hidden flex flex-col justify-center items-center w-8 h-8 rounded-full hover:bg-white/10 transition-colors gap-1.5 z-50 relative"
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                        aria-label="Toggle menu"
                        style={{ border: "none", background: "transparent", cursor: "pointer" }}
                    >
                        <span
                            className={`block w-5 h-0.5 bg-white transition-all duration-300 transform ${isMenuOpen ? "rotate-45 translate-y-2" : ""
                                }`}
                        />
                        <span
                            className={`block w-5 h-0.5 bg-white transition-all duration-300 ${isMenuOpen ? "opacity-0" : ""
                                }`}
                        />
                        <span
                            className={`block w-5 h-0.5 bg-white transition-all duration-300 transform ${isMenuOpen ? "-rotate-45 -translate-y-2" : ""
                                }`}
                        />
                    </button>
                </nav>
            </header>

            {/* Mobile Menu Overlay */}
            <div
                style={{
                    position: "fixed",
                    inset: 0,
                    background: "rgba(3, 4, 6, 0.98)",
                    zIndex: 40,
                    padding: "120px 24px 24px",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: 32,
                    transition: "opacity 0.3s ease-in-out, visibility 0.3s ease-in-out",
                    opacity: isMenuOpen ? 1 : 0,
                    visibility: isMenuOpen ? "visible" : "hidden",
                    pointerEvents: isMenuOpen ? "auto" : "none",
                }}
            >
                {LINKS.map((link) => (
                    <button
                        key={link.label}
                        onClick={() => scrollToSection(link.id)}
                        style={{
                            fontSize: 24,
                            fontWeight: 600,
                            color: "#e5e7eb",
                            background: "transparent",
                            border: "none",
                            cursor: "pointer",
                            transition: "transform 0.2s, color 0.2s",
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.color = "#3b82f6";
                            e.currentTarget.style.transform = "scale(1.1)";
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.color = "#e5e7eb";
                            e.currentTarget.style.transform = "scale(1)";
                        }}
                    >
                        {link.label}
                    </button>
                ))}

                <div
                    style={{
                        width: 60,
                        height: 1,
                        background: "rgba(255,255,255,0.1)",
                        margin: "0",
                    }}
                />

                <button
                    onClick={scrollToTerminal}
                    style={{
                        fontSize: 18,
                        fontWeight: 700,
                        padding: "16px 48px",
                        borderRadius: 9999,
                        border: "none",
                        background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
                        color: "#fff",
                        cursor: "pointer",
                        boxShadow: "0 0 30px rgba(59,130,246,0.3)",
                        transition: "transform 0.2s, box-shadow 0.2s",
                        width: "100%",
                        maxWidth: 320,
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
                    Get Started
                </button>
            </div>
        </>
    );
}
