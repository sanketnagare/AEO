/**
 * API client wrapper for backend REST calls.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface AuditReport {
    url: string;
    scores: {
        seo_score: number;
        aeo_score: number;
        geo_score: number;
        overall_score: number;
    };
    performance: {
        lcp: number | null;
        cls: number | null;
        inp: number | null;
        fcp: number | null;
        ttfb: number | null;
        performance_score: number | null;
        speed_index: number | null;
    } | null;
    seo_checks: CheckResult[];
    aeo_checks: CheckResult[];
    geo_checks: CheckResult[];
    word_count: number | null;
    title: string | null;
    meta_description: string | null;
    audited_at: string;
}

export interface CheckResult {
    check_name: string;
    audit_type: string;
    severity: "critical" | "warning" | "info" | "pass";
    message: string;
    recommendation?: string;
    current_value?: string;
    expected_value?: string;
}

/**
 * Call the REST audit endpoint (non-streaming).
 */
export async function auditPage(url: string): Promise<AuditReport> {
    const response = await fetch(`${API_BASE}/api/audit/single`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
    });
    if (!response.ok) {
        throw new Error(`Audit failed: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Health check.
 */
export async function healthCheck(): Promise<{ status: string; version: string }> {
    const response = await fetch(`${API_BASE}/api/health`);
    return response.json();
}
