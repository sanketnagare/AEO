"use client";

import React, { useState } from "react";
import { supabase } from "@/lib/supabase";

type AuthMode = "signin" | "signup";

interface TerminalLoginCardProps {
    onSuccess?: () => void;
    onClose?: () => void;
}

export default function TerminalLoginCard(props: TerminalLoginCardProps) {
    const { onSuccess, onClose } = props;

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [mode, setMode] = useState<AuthMode>("signin");
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState<{ text: string; type: "success" | "error" } | null>(null);

    const handleEmailAuth = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setMessage(null);

        try {
            if (mode === "signup") {
                const { error } = await supabase.auth.signUp({
                    email,
                    password,
                });
                if (error) throw error;
                setMessage({ text: "✓ Check your email to confirm your account", type: "success" });
                // Note: For signup, we might wait for email confirmation or auto-login depending on config.
                // If auto-confirm is off, they can't login yet.
                // Assuming default Supabase behavior (confirm email required), we don't call onSuccess yet.
                // IF we want to allow immediate access (if email confirm is disabled), we could.
                // Safest: Check if session exists. 
                const { data } = await supabase.auth.getSession();
                if (data.session) {
                    onSuccess?.();
                }
            } else {
                const { error } = await supabase.auth.signInWithPassword({
                    email,
                    password,
                });
                if (error) throw error;
                setMessage({ text: "✓ Signed in successfully", type: "success" });
                onSuccess?.();
            }
        } catch (err: unknown) {
            const errorMessage = err instanceof Error ? err.message : "Authentication failed";
            setMessage({ text: errorMessage, type: "error" });
        } finally {
            setLoading(false);
        }
    };

    const handleGoogleLogin = async () => {
        setLoading(true);
        setMessage(null);

        try {
            const { error } = await supabase.auth.signInWithOAuth({
                provider: "google",
                options: {
                    redirectTo: `${window.location.origin}/`,
                },
            });
            if (error) throw error;
        } catch (err: unknown) {
            const errorMessage = err instanceof Error ? err.message : "Google login failed";
            setMessage({ text: errorMessage, type: "error" });
            setLoading(false);
        }
    };

    return (
        <div className="flex justify-center w-full">
            <div
                className="relative rounded-2xl bg-[#0A0E14]/90 backdrop-blur-xl border border-white/10 shadow-2xl overflow-hidden"
                style={{
                    width: "100%",
                    maxWidth: 400,
                    padding: "40px 32px",
                    boxShadow: "0 0 0 1px rgba(255,255,255,0.05), 0 24px 64px -12px rgba(0,0,0,0.5)"
                }}
            >
                {/* Subtle top highlight */}
                <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent" />

                {/* Close Button */}
                {onClose && (
                    <button
                        onClick={onClose}
                        className="absolute top-4 right-4 text-gray-500 hover:text-white transition-colors p-2 z-10"
                        aria-label="Close"
                    >
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                )}

                {/* Status Message */}
                {message && (
                    <div
                        className={`mb-4 px-3 py-2 rounded-lg font-mono text-xs border ${message.type === "success"
                            ? "bg-green-500/10 border-green-500/30 text-green-400"
                            : "bg-red-500/10 border-red-500/30 text-red-400"
                            }`}
                    >
                        {message.text}
                    </div>
                )}

                {/* Email Form */}
                <form onSubmit={handleEmailAuth} className="space-y-4">
                    <div className="space-y-2">
                        <label className="text-gray-200 font-mono text-sm font-bold ml-1">
                            Your Email:
                        </label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="email@example.com"
                            required
                            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3.5 text-gray-200 font-mono text-sm focus:outline-none focus:border-white/30 focus:bg-white/10 transition-all placeholder:text-gray-600"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-gray-200 font-mono text-sm font-bold ml-1">
                            Password:
                        </label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                            required
                            minLength={6}
                            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3.5 text-gray-200 font-mono text-sm focus:outline-none focus:border-white/30 focus:bg-white/10 transition-all placeholder:text-gray-600"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="group w-full relative overflow-hidden bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-mono text-sm font-bold py-4 rounded-lg transition-all active:scale-[0.98] shadow-lg shadow-orange-500/20 hover:shadow-orange-500/30"
                    >
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-200%] group-hover:animate-[shimmer_1.5s_infinite]" />
                        <span className="relative z-10">
                            {loading
                                ? "Processing..."
                                : mode === "signin"
                                    ? "Sign in with Email"
                                    : "Create Account"}
                        </span>
                    </button>
                </form>

                {/* Toggle Sign In / Sign Up */}
                <div className="mt-3 text-center">
                    <button
                        onClick={() => {
                            setMode(mode === "signin" ? "signup" : "signin");
                            setMessage(null);
                        }}
                        className="text-gray-500 hover:text-gray-300 font-mono text-xs transition-colors"
                    >
                        {mode === "signin"
                            ? "Don't have an account? Sign up"
                            : "Already have an account? Sign in"}
                    </button>
                </div>

                {/* Divider */}
                <div className="relative my-6">
                    <div className="absolute inset-0 flex items-center">
                        <div className="w-full border-t border-white/20" />
                    </div>
                    <div className="relative flex justify-center">
                        <span className="bg-black px-3 text-gray-500 font-mono text-xs tracking-wider">
                            --- OR ---
                        </span>
                    </div>
                </div>

                {/* Google Button */}
                <button
                    onClick={handleGoogleLogin}
                    disabled={loading}
                    className="group w-full relative overflow-hidden bg-white text-black font-mono text-sm font-bold py-4 rounded-lg transition-all hover:bg-gray-100 hover:scale-[1.01] active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-3 shadow-lg shadow-white/5"
                >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-black/5 to-transparent translate-x-[-200%] group-hover:animate-[shimmer_1.5s_infinite]" />
                    <svg className="w-5 h-5" viewBox="0 0 24 24">
                        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                        <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.04-3.71 1.04-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                        <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                        <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
                    </svg>
                    <span className="relative z-10">Sign in with Google</span>
                </button>
            </div>
        </div>
    );
}